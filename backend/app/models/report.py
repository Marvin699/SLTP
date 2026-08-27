"""报告记录模型"""
from sqlalchemy import Column, Integer, String, DateTime, Text, Boolean
from datetime import datetime
from app.core.database import Base


class ReportRecord(Base):
    """方案报告记录"""
    __tablename__ = "report_records"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, nullable=True, index=True)   # 归属用户（教师监控用）
    task_config = Column(Text, nullable=True)          # 任务配置JSON
    solution_data = Column(Text, nullable=True)        # 方案数据JSON
    diagnosis_data = Column(Text, nullable=True)       # 诊断数据JSON
    report_data = Column(Text, nullable=True)          # 报告数据JSON
    word_path = Column(String(500), nullable=True)     # Word文件路径
    pdf_path = Column(String(500), nullable=True)      # PDF文件路径
    filename = Column(String(200), nullable=True)      # 文件名
    scheme_type = Column(String(50), default="运输方案") # 方案类型
    aco_params = Column(Text, nullable=True)           # 生成时的ACO参数JSON（供派生重生成回填）
    is_chosen = Column(Boolean, default=False)         # 择优决策：是否为最终选定方案
    choice_reason = Column(Text, nullable=True)        # 择优决策理由
    created_at = Column(DateTime, default=datetime.now) # 创建时间
