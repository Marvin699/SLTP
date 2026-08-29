"""全流程交互日志模型（T8）

记录学生关键学习动作，供教师端监控与思辨能力评估使用。
"""
from sqlalchemy import Column, Integer, String, DateTime, Text
from datetime import datetime
from app.core.database import Base

# 动作类型常量
ACTION_PLAN_GENERATE = "方案生成"      # ACO 路径规划
ACTION_REPORT = "报告生成"            # 生成方案报告
ACTION_CHOOSE = "择优决策"            # 对比后选定最终方案
ACTION_VERIFICATION = "合规核验"      # 提交核验
ACTION_DEBATE = "反向质询"            # 辩论发言/新会话
ACTION_DERIVE = "派生重生成"          # 从报告回填参数重新规划


class ActivityLog(Base):
    """交互日志"""
    __tablename__ = "activity_logs"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, nullable=True, index=True)      # 操作者（匿名可为空）
    action = Column(String(30), nullable=False, index=True)   # 动作类型（见上方常量）
    payload = Column(Text, nullable=True)                     # 动作详情 JSON（摘要数据）
    plan_record_id = Column(Integer, nullable=True)           # 关联的方案记录
    created_at = Column(DateTime, default=datetime.now, index=True)


def log_activity(db, user_id, action, payload=None, plan_record_id=None):
    """记录一条交互日志（失败静默，不阻断业务流程）"""
    try:
        import json
        db.add(ActivityLog(
            user_id=user_id,
            action=action,
            payload=json.dumps(payload, ensure_ascii=False) if payload else None,
            plan_record_id=plan_record_id,
        ))
        db.commit()
    except Exception:
        try:
            db.rollback()
        except Exception:
            pass
