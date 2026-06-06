"""模块六：方案优出 API 路由"""
import json
import os
import re
import shutil
import urllib.parse
from fastapi import APIRouter, HTTPException, Query
from fastapi.responses import FileResponse, StreamingResponse
from pydantic import BaseModel
from typing import Dict, Any, Optional, List
from datetime import datetime
from pathlib import Path

from app.services.report_service import generate_report, generate_report_data, generate_word_report
from app.core.database import SessionLocal
from app.models.report import ReportRecord

router = APIRouter(prefix="/api/path-planning/report", tags=["模块六-方案优出"])

# 报告存储目录
REPORTS_DIR = Path(__file__).parent.parent.parent / "reports"
REPORTS_DIR.mkdir(exist_ok=True)


class GenerateReportRequest(BaseModel):
    task: Dict[str, Any]
    solution: Dict[str, Any]
    diagnosis: Optional[Dict[str, Any]] = None
    scheme_type: Optional[str] = "运输方案"


class UpdateReportRequest(BaseModel):
    report_data: Dict[str, Any]


@router.post("/generate")
def generate_report_endpoint(req: GenerateReportRequest):
    """
    生成方案报告（Word + PDF）
    
    请求体:
        task: 任务配置
        solution: 方案数据
        diagnosis: 诊断结果（可选）
        scheme_type: 方案类型（可选，默认"路径规划方案"）
    
    返回:
        报告信息和下载链接
    """
    try:
        import logging
        logger = logging.getLogger(__name__)
        
        logger.info(f"收到生成报告请求，scheme_type={req.scheme_type}")
        logger.info(f"task keys: {list(req.task.keys()) if req.task else 'None'}")
        logger.info(f"solution keys: {list(req.solution.keys()) if req.solution else 'None'}")
        
        # 更新方案类型到task
        if req.scheme_type:
            if req.task:
                req.task['scheme_type'] = req.scheme_type
        
        # 生成报告
        result = generate_report(
            req.task, 
            req.solution, 
            req.diagnosis,
            output_dir=str(REPORTS_DIR)
        )
        
        logger.info(f"报告生成成功: {result['filename']}")
        
        # 保存到数据库
        db = SessionLocal()
        record = ReportRecord(
            task_config=json.dumps(req.task, ensure_ascii=False),
            solution_data=json.dumps(req.solution, ensure_ascii=False),
            diagnosis_data=json.dumps(req.diagnosis, ensure_ascii=False) if req.diagnosis else None,
            report_data=json.dumps(result['data'], ensure_ascii=False),
            word_path=result['word'],
            pdf_path=result['pdf'],
            filename=result['filename'],
            scheme_type=req.scheme_type or "路径规划方案",
        )
        db.add(record)
        db.commit()
        db.refresh(record)
        
        report_id = record.id
        db.close()
        
        logger.info(f"报告保存到数据库，ID={report_id}")
        
        return {
            "id": report_id,
            "filename": result['filename'],
            "word_url": f"/api/report/download/{report_id}/word",
            "pdf_url": f"/api/report/download/{report_id}/pdf",
            "data": result['data'],
            "created_at": datetime.now().isoformat(),
        }
    except Exception as e:
        import traceback
        error_detail = f"生成报告失败: {type(e).__name__}: {str(e)}\n{traceback.format_exc()}"
        logger.error(error_detail)
        raise HTTPException(status_code=500, detail=error_detail)


def _ascii_name(name: str) -> str:
    return (re.sub(r'[^A-Za-z0-9._-]+', '_', name).strip('_') or 'report')


def _enc_name(name: str, ext: str) -> str:
    clean = re.sub(r'[\\/:*?"<>|\s]+', '_', name).strip('_') or 'report'
    try:
        return urllib.parse.quote((clean + '.' + ext).encode('utf-8'))
    except Exception:
        return clean + '.' + ext

@router.get("/download/{report_id}/word")
def download_word(report_id: int):
    """下载Word报告"""
    try:
        db = SessionLocal()
        record = db.query(ReportRecord).filter(ReportRecord.id == report_id).first()
        db.close()

        if not record:
            raise HTTPException(status_code=404, detail="报告不存在")

        if not os.path.exists(record.word_path):
            raise HTTPException(status_code=404, detail="Word文件不存在")

        base = record.filename or 'report'
        safe_ascii = _ascii_name(base)
        encoded = _enc_name(base, 'docx')
        headers = {
            'Content-Disposition': (
                f"attachment; filename=\"{safe_ascii}.docx\"; "
                f"filename*=UTF-8''{encoded}"
            ),
            'Cache-Control': 'no-cache, no-store, must-revalidate',
            'Pragma': 'no-cache',
            'Expires': '0',
        }
        return FileResponse(
            record.word_path,
            media_type="application/vnd.openxmlformats-officedocument.wordprocessingml.document",
            filename=f"{safe_ascii}.docx",
            headers=headers,
        )
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"下载失败: {str(e)}")


@router.get("/download/{report_id}/pdf")
def download_pdf(report_id: int):
    """下载PDF报告"""
    try:
        db = SessionLocal()
        record = db.query(ReportRecord).filter(ReportRecord.id == report_id).first()
        db.close()

        if not record:
            raise HTTPException(status_code=404, detail="报告不存在")

        if not os.path.exists(record.pdf_path):
            raise HTTPException(status_code=404, detail="PDF文件不存在")

        base = record.filename or 'report'
        safe_ascii = _ascii_name(base)
        encoded = _enc_name(base, 'pdf')
        headers = {
            'Content-Disposition': (
                f"attachment; filename=\"{safe_ascii}.pdf\"; "
                f"filename*=UTF-8''{encoded}"
            ),
            'Cache-Control': 'no-cache, no-store, must-revalidate',
            'Pragma': 'no-cache',
            'Expires': '0',
        }
        return FileResponse(
            record.pdf_path,
            media_type="application/pdf",
            filename=f"{safe_ascii}.pdf",
            headers=headers,
        )
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"下载失败: {str(e)}")


@router.get("/history")
def get_report_history(limit: int = 20):
    """
    获取报告历史记录
    
    参数:
        limit: 返回记录数量（默认20条）
    
    返回:
        报告记录列表
    """
    try:
        db = SessionLocal()
        records = db.query(ReportRecord).order_by(
            ReportRecord.created_at.desc()
        ).limit(limit).all()
        
        result = []
        for record in records:
            # report_data 是 JSON 字符串，需要解析
            report_data = {}
            if record.report_data:
                try:
                    report_data = json.loads(record.report_data)
                except:
                    pass
            
            result.append({
                "id": record.id,
                "filename": record.filename,
                "scheme_type": record.scheme_type,
                "project_name": report_data.get('project_name', '未知项目') if isinstance(report_data, dict) else '未知项目',
                "created_at": record.created_at.isoformat() if record.created_at else None,
            })
        
        db.close()
        return {"records": result}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"获取历史记录失败: {str(e)}")


@router.get("/{report_id}")
def get_report_detail(report_id: int):
    """
    获取报告详情
    
    参数:
        report_id: 报告ID
    
    返回:
        报告详情（包含完整数据）
    """
    try:
        db = SessionLocal()
        record = db.query(ReportRecord).filter(ReportRecord.id == report_id).first()
        
        if not record:
            db.close()
            raise HTTPException(status_code=404, detail="报告不存在")
        
        result = {
            "id": record.id,
            "filename": record.filename,
            "scheme_type": record.scheme_type,
            "word_url": f"/api/report/download/{record.id}/word",
            "pdf_url": f"/api/report/download/{record.id}/pdf",
            "report_data": json.loads(record.report_data) if record.report_data else None,
            "task_config": json.loads(record.task_config) if record.task_config else None,
            "solution_data": json.loads(record.solution_data) if record.solution_data else None,
            "created_at": record.created_at.isoformat() if record.created_at else None,
        }
        
        db.close()
        return result
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"获取报告详情失败: {str(e)}")


@router.put("/{report_id}")
def update_report(report_id: int, req: UpdateReportRequest):
    """
    更新报告数据（重新生成Word）
    
    参数:
        report_id: 报告ID
        report_data: 更新的报告数据
    
    返回:
        更新后的报告信息
    """
    try:
        db = SessionLocal()
        record = db.query(ReportRecord).filter(ReportRecord.id == report_id).first()
        
        if not record:
            db.close()
            raise HTTPException(status_code=404, detail="报告不存在")
        
        # 更新报告数据
        record.report_data = json.dumps(req.report_data, ensure_ascii=False)
        
        # 重新生成Word
        word_path = generate_word_report(req.report_data, record.word_path)
        record.word_path = word_path
        
        db.commit()
        db.close()
        
        return {
            "id": report_id,
            "message": "报告已更新",
            "word_url": f"/api/report/download/{report_id}/word",
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"更新报告失败: {str(e)}")


@router.delete("/{report_id}")
def delete_report(report_id: int):
    """
    删除报告
    
    参数:
        report_id: 报告ID
    
    返回:
        删除结果
    """
    try:
        db = SessionLocal()
        record = db.query(ReportRecord).filter(ReportRecord.id == report_id).first()
        
        if not record:
            db.close()
            raise HTTPException(status_code=404, detail="报告不存在")
        
        # 删除文件
        if record.word_path and os.path.exists(record.word_path):
            os.remove(record.word_path)
        if record.pdf_path and os.path.exists(record.pdf_path):
            os.remove(record.pdf_path)
        
        # 删除数据库记录
        db.delete(record)
        db.commit()
        db.close()
        
        return {"success": True, "message": "报告已删除"}
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"删除报告失败: {str(e)}")
