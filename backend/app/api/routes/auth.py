"""用户认证与用户管理 API

接口列表：
- POST /api/auth/register          学生自助注册（可填教师邀请码）
- POST /api/auth/login             登录（返回 JWT）
- GET  /api/auth/me                获取当前用户信息
- POST /api/auth/change-password   修改密码
- POST /api/auth/batch-register    教师批量导入学生（需教师权限）
- GET  /api/auth/students          教师查看学生列表（需教师权限）
- POST /api/auth/students/{id}/claim  教师认领未分配学生（需教师权限）
- GET  /api/auth/invite-code       教师查看自己的邀请码（需教师权限）
- POST /api/auth/invite-code       教师重置邀请码（需教师权限）
- POST /api/auth/reset-password/{user_id}  教师重置学生密码（需教师权限）
- DELETE /api/auth/students/{user_id}  教师删除学生（需教师权限）
"""
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from sqlalchemy import or_
from pydantic import BaseModel, field_validator
from typing import List, Optional
from datetime import datetime
import secrets

from app.core.deps import get_db, get_current_user, require_teacher
from app.core.security import hash_password, verify_password, create_access_token
from app.models.user import User

router = APIRouter(prefix="/api/auth", tags=["用户认证"])


# ============ 请求模型 ============

class RegisterRequest(BaseModel):
    username: str  # 学生姓名
    student_no: str  # 学号
    password: str
    class_name: Optional[str] = None
    group_no: Optional[str] = None
    invite_code: Optional[str] = None  # 教师邀请码（选填）

    @field_validator("username", "student_no", "password")
    @classmethod
    def not_empty(cls, v):
        if not v or not v.strip():
            raise ValueError("字段不能为空")
        return v.strip()


class LoginRequest(BaseModel):
    username: str
    password: str


class ChangePasswordRequest(BaseModel):
    old_password: str
    new_password: str


class UpdateProfileRequest(BaseModel):
    username: Optional[str] = None
    avatar: Optional[str] = None  # emoji 字符或图标标识
    class_name: Optional[str] = None
    group_no: Optional[str] = None


class BatchStudentItem(BaseModel):
    username: str  # 姓名
    student_no: str  # 学号
    class_name: Optional[str] = None
    group_no: Optional[str] = None


class BatchRegisterRequest(BaseModel):
    students: List[BatchStudentItem]
    default_password: str = "123456"


class ResetPasswordRequest(BaseModel):
    new_password: str = "123456"


# ============ 工具函数 ============

def user_to_dict(user: User) -> dict:
    d = {
        "id": user.id,
        "username": user.username,
        "role": user.role,
        "student_no": user.student_no,
        "class_name": user.class_name,
        "group_no": user.group_no,
        "teacher_id": user.teacher_id,
        "must_change_password": user.must_change_password,
        "avatar": user.avatar,
        "is_active": user.is_active,
        "created_at": user.created_at.strftime("%Y-%m-%d %H:%M:%S") if user.created_at else None,
    }
    if user.role == "teacher":
        d["invite_code"] = user.invite_code
    return d


def gen_invite_code(db: Session) -> str:
    """生成不重复的 6 位邀请码（大写字母+数字，去掉易混淆字符）"""
    alphabet = "ABCDEFGHJKLMNPQRSTUVWXYZ23456789"
    while True:
        code = "".join(secrets.choice(alphabet) for _ in range(6))
        if not db.query(User).filter(User.invite_code == code).first():
            return code


def ensure_teacher_invite_code(db: Session, teacher: User) -> str:
    """确保教师有邀请码，没有则生成"""
    if not teacher.invite_code:
        teacher.invite_code = gen_invite_code(db)
        db.commit()
    return teacher.invite_code


def resolve_teacher_id(db: Session, invite_code: Optional[str]) -> Optional[int]:
    """按邀请码确定学生归属教师；无码时若全平台仅一位教师则自动归属"""
    if invite_code and invite_code.strip():
        teacher = db.query(User).filter(
            User.role == "teacher", User.invite_code == invite_code.strip().upper()
        ).first()
        if not teacher:
            raise HTTPException(status_code=400, detail="邀请码无效，请核对后重新填写")
        return teacher.id
    teachers = db.query(User).filter(User.role == "teacher").all()
    if len(teachers) == 1:
        return teachers[0].id
    return None


# ============ 接口实现 ============

@router.post("/register")
def register(req: RegisterRequest, db: Session = Depends(get_db)):
    """学生自助注册"""
    # 检查用户名是否已存在
    existing = db.query(User).filter(User.username == req.username).first()
    if existing:
        raise HTTPException(status_code=400, detail=f"用户名「{req.username}」已被注册")

    # 检查学号是否已存在
    if req.student_no:
        existing_no = db.query(User).filter(User.student_no == req.student_no).first()
        if existing_no:
            raise HTTPException(status_code=400, detail=f"学号「{req.student_no}」已被注册")

    if len(req.password) < 6:
        raise HTTPException(status_code=400, detail="密码长度不能少于 6 位")

    user = User(
        username=req.username,
        password_hash=hash_password(req.password),
        role="student",
        student_no=req.student_no,
        class_name=req.class_name,
        group_no=req.group_no,
        teacher_id=resolve_teacher_id(db, req.invite_code),
        must_change_password=False,  # 自助注册的学生已自设密码
    )
    db.add(user)
    db.commit()
    db.refresh(user)

    token = create_access_token(user.id, user.username, user.role)
    return {
        "success": True,
        "message": "注册成功",
        "token": token,
        "user": user_to_dict(user),
    }


@router.post("/login")
def login(req: LoginRequest, db: Session = Depends(get_db)):
    """登录接口（学生和教师通用）"""
    # 支持用户名或学号登录
    user = db.query(User).filter(
        or_(User.username == req.username, User.student_no == req.username)
    ).first()

    if not user or not verify_password(req.password, user.password_hash):
        raise HTTPException(status_code=401, detail="账号或密码错误")

    if not user.is_active:
        raise HTTPException(status_code=403, detail="账号已被禁用，请联系教师")

    token = create_access_token(user.id, user.username, user.role)
    return {
        "success": True,
        "message": "登录成功",
        "token": token,
        "user": user_to_dict(user),
    }


@router.get("/me")
def get_me(current_user: User = Depends(get_current_user)):
    """获取当前登录用户信息"""
    return {"success": True, "user": user_to_dict(current_user)}


@router.put("/profile")
def update_profile(
    req: UpdateProfileRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """更新个人资料（用户名、头像、班级、小组）"""
    # 更新用户名（检查唯一性）
    if req.username is not None and req.username.strip():
        new_name = req.username.strip()
        if new_name != current_user.username:
            existing = db.query(User).filter(User.username == new_name, User.id != current_user.id).first()
            if existing:
                raise HTTPException(status_code=400, detail=f"用户名「{new_name}」已被占用")
            current_user.username = new_name

    # 更新头像（emoji 或图标标识，限长 20）
    if req.avatar is not None:
        current_user.avatar = req.avatar.strip()[:20] if req.avatar.strip() else None

    # 学生可更新班级和小组
    if req.class_name is not None:
        current_user.class_name = req.class_name.strip() or None
    if req.group_no is not None:
        current_user.group_no = req.group_no.strip() or None

    db.commit()
    db.refresh(current_user)

    return {"success": True, "message": "资料更新成功", "user": user_to_dict(current_user)}


@router.post("/change-password")
def change_password(
    req: ChangePasswordRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """修改密码"""
    if not verify_password(req.old_password, current_user.password_hash):
        raise HTTPException(status_code=400, detail="原密码错误")

    if len(req.new_password) < 6:
        raise HTTPException(status_code=400, detail="新密码长度不能少于 6 位")

    current_user.password_hash = hash_password(req.new_password)
    current_user.must_change_password = False  # 改密后清除强制标记
    db.commit()

    return {"success": True, "message": "密码修改成功"}


@router.post("/batch-register")
def batch_register(
    req: BatchRegisterRequest,
    teacher: User = Depends(require_teacher),
    db: Session = Depends(get_db),
):
    """教师批量导入学生"""
    if not req.students:
        raise HTTPException(status_code=400, detail="学生列表不能为空")

    success_count = 0
    fail_list = []

    for idx, item in enumerate(req.students):
        try:
            # 跳过空行
            if not item.username or not item.student_no:
                fail_list.append({"row": idx + 1, "reason": "姓名或学号为空"})
                continue

            # 检查重复
            existing = db.query(User).filter(
                or_(User.username == item.username, User.student_no == item.student_no)
            ).first()
            if existing:
                fail_list.append({"row": idx + 1, "reason": f"姓名「{item.username}」或学号「{item.student_no}」已存在"})
                continue

            user = User(
                username=item.username,
                password_hash=hash_password(req.default_password),
                role="student",
                student_no=item.student_no,
                class_name=item.class_name,
                group_no=item.group_no,
                teacher_id=teacher.id,  # 批量导入的学生归该教师
                must_change_password=True,  # 批量导入强制改密
            )
            db.add(user)
            success_count += 1
        except Exception as e:
            fail_list.append({"row": idx + 1, "reason": str(e)})

    db.commit()

    return {
        "success": True,
        "message": f"导入完成：成功 {success_count} 人，失败 {len(fail_list)} 人",
        "success_count": success_count,
        "fail_count": len(fail_list),
        "fail_list": fail_list,
    }


@router.get("/students")
def list_students(
    keyword: Optional[str] = None,
    class_name: Optional[str] = None,
    teacher: User = Depends(require_teacher),
    db: Session = Depends(get_db),
):
    """教师查看学生列表（我的学生 + 未分配的散生，支持搜索）"""
    query = db.query(User).filter(
        User.role == "student",
        or_(User.teacher_id == teacher.id, User.teacher_id.is_(None)),
    )

    if keyword:
        query = query.filter(
            or_(
                User.username.contains(keyword),
                User.student_no.contains(keyword),
                User.group_no.contains(keyword),
            )
        )
    if class_name:
        query = query.filter(User.class_name == class_name)

    students = query.order_by(User.created_at.desc()).all()

    result = []
    for s in students:
        d = user_to_dict(s)
        d["assigned"] = s.teacher_id == teacher.id  # False = 未分配，可认领
        result.append(d)

    return {
        "success": True,
        "total": len(result),
        "students": result,
    }


@router.post("/students/{user_id}/claim")
def claim_student(
    user_id: int,
    teacher: User = Depends(require_teacher),
    db: Session = Depends(get_db),
):
    """教师认领未分配的学生"""
    user = db.query(User).filter(User.id == user_id, User.role == "student").first()
    if not user:
        raise HTTPException(status_code=404, detail="学生不存在")
    if user.teacher_id and user.teacher_id != teacher.id:
        raise HTTPException(status_code=400, detail=f"该学生已归属其他教师，无法认领")

    user.teacher_id = teacher.id
    db.commit()
    return {"success": True, "message": f"已将「{user.username}」纳入名下"}


@router.patch("/students/{user_id}/group")
def set_student_group(
    user_id: int,
    group_no: Optional[str] = None,
    teacher: User = Depends(require_teacher),
    db: Session = Depends(get_db),
):
    """教师设置学生的小组编号（用于虚拟仿真视频按组匹配，传空串清除）"""
    user = db.query(User).filter(User.id == user_id, User.role == "student").first()
    if not user:
        raise HTTPException(status_code=404, detail="学生不存在")

    user.group_no = (group_no or "").strip() or None
    db.commit()
    label = f"第 {user.group_no} 组" if user.group_no else "未分组"
    return {"success": True, "message": f"已将「{user.username}」设为 {label}", "group_no": user.group_no}


@router.get("/invite-code")
def get_invite_code(
    teacher: User = Depends(require_teacher),
    db: Session = Depends(get_db),
):
    """教师查看自己的邀请码（没有则自动生成）"""
    code = ensure_teacher_invite_code(db, teacher)
    return {"success": True, "invite_code": code}


@router.post("/invite-code")
def reset_invite_code(
    teacher: User = Depends(require_teacher),
    db: Session = Depends(get_db),
):
    """教师重置邀请码（旧码立即失效）"""
    teacher.invite_code = gen_invite_code(db)
    db.commit()
    return {"success": True, "invite_code": teacher.invite_code, "message": "邀请码已重置"}


@router.post("/reset-password/{user_id}")
def reset_password(
    user_id: int,
    req: ResetPasswordRequest,
    teacher: User = Depends(require_teacher),
    db: Session = Depends(get_db),
):
    """教师重置学生密码"""
    user = db.query(User).filter(User.id == user_id, User.role == "student").first()
    if not user:
        raise HTTPException(status_code=404, detail="学生不存在")

    user.password_hash = hash_password(req.new_password)
    user.must_change_password = True  # 重置后强制改密
    db.commit()

    return {"success": True, "message": f"已重置「{user.username}」的密码为 {req.new_password}"}


@router.delete("/students/{user_id}")
def delete_student(
    user_id: int,
    teacher: User = Depends(require_teacher),
    db: Session = Depends(get_db),
):
    """教师删除学生账号"""
    user = db.query(User).filter(User.id == user_id, User.role == "student").first()
    if not user:
        raise HTTPException(status_code=404, detail="学生不存在")

    db.delete(user)
    db.commit()
    return {"success": True, "message": f"已删除学生「{user.username}」"}


@router.get("/stats")
def get_user_stats(
    teacher: User = Depends(require_teacher),
    db: Session = Depends(get_db),
):
    """教师端：用户统计（用于首页驾驶舱）"""
    from sqlalchemy import func as sql_func

    total_students = db.query(sql_func.count(User.id)).filter(User.role == "student").scalar() or 0
    active_students = db.query(sql_func.count(User.id)).filter(
        User.role == "student", User.is_active == True
    ).scalar() or 0
    today = datetime.now().strftime("%Y-%m-%d")
    today_new = db.query(sql_func.count(User.id)).filter(
        User.role == "student",
        sql_func.strftime("%Y-%m-%d", User.created_at) == today
    ).scalar() or 0

    # 按班级统计
    class_rows = db.query(
        User.class_name, sql_func.count(User.id)
    ).filter(User.role == "student").group_by(User.class_name).all()

    # 按小组统计
    group_rows = db.query(
        User.group_no, sql_func.count(User.id)
    ).filter(User.role == "student", User.group_no.isnot(None)).group_by(User.group_no).all()

    return {
        "success": True,
        "stats": {
            "total_students": total_students,
            "active_students": active_students,
            "today_new": today_new,
            "by_class": [{"name": r[0] or "未分班", "count": r[1]} for r in class_rows],
            "by_group": [{"name": r[0] or "未分组", "count": r[1]} for r in group_rows],
        },
    }
