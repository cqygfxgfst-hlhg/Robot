# backend/app/services/modal_service.py

import modal
import os

# Modal 会自动使用已配置的 Token，不需要手动设置
app = modal.App("training-job")

@app.function(
    image=modal.Image.debian_slim().pip_install("torch","torchvision"), 
    timeout=3600,
)
def train(model_name: str, dataset_url: str, parameters: dict):
    """训练函数 - 包含详细的日志记录"""
    import time
    import random
    import traceback
    from datetime import datetime
    
    # 初始化日志
    logs = []
    
    def log(message):
        """记录日志"""
        timestamp = datetime.utcnow().isoformat()
        log_entry = f"[{timestamp}] {message}"
        print(log_entry)
        logs.append(log_entry)
    
    try:
        log(f"=== 开始训练任务 ===")
        log(f"模型名称: {model_name}")
        log(f"数据集地址: {dataset_url}")
        log(f"训练参数: {parameters}")
        log(f"开始时间: {datetime.utcnow().isoformat()}")
        
        # 步骤1: 环境检查
        log("步骤1: 检查训练环境...")
        import sys
        log(f"Python版本: {sys.version}")
        log(f"工作目录: {os.getcwd()}")
        
        # 步骤2: 数据准备
        log("步骤2: 准备训练数据...")
        log(f"从 {dataset_url} 下载数据集...")
        time.sleep(1)  # 模拟数据下载
        log("数据集下载完成")
        
        # 步骤3: 模型初始化
        log("步骤3: 初始化模型...")
        log(f"加载模型: {model_name}")
        time.sleep(1)  # 模拟模型加载
        log("模型加载完成")
        
        # 步骤4: 训练过程
        log("步骤4: 开始训练...")
        epochs = parameters.get('epochs', 10)
        batch_size = parameters.get('batch_size', 32)
        learning_rate = parameters.get('lr', 0.001)
        
        log(f"训练配置: epochs={epochs}, batch_size={batch_size}, lr={learning_rate}")
        
        for epoch in range(epochs):
            log(f"Epoch {epoch+1}/{epochs}: 开始训练...")
            time.sleep(0.5)  # 模拟每个epoch的训练时间
            
            # 模拟训练指标
            train_loss = random.uniform(0.1, 0.5)
            val_loss = random.uniform(0.08, 0.4)
            accuracy = random.uniform(0.85, 0.95)
            
            log(f"Epoch {epoch+1}/{epochs}: train_loss={train_loss:.4f}, val_loss={val_loss:.4f}, accuracy={accuracy:.4f}")
        
        # 步骤5: 模型保存
        log("步骤5: 保存训练结果...")
        log("模型权重已保存")
        log("训练指标已记录")
        
        # 步骤6: 清理资源
        log("步骤6: 清理训练资源...")
        log("GPU内存已释放")
        log("临时文件已清理")
        
        log("=== 训练任务完成 ===")
        log(f"结束时间: {datetime.utcnow().isoformat()}")
        
        return {
            "status": "success",
            "logs": logs,
            "final_accuracy": accuracy,
            "final_loss": val_loss
        }
        
    except Exception as e:
        log(f"=== 训练任务失败 ===")
        log(f"错误类型: {type(e).__name__}")
        log(f"错误信息: {str(e)}")
        log(f"异常栈:")
        for line in traceback.format_exc().split('\n'):
            if line.strip():
                log(f"  {line}")
        log(f"失败时间: {datetime.utcnow().isoformat()}")
        
        # 将日志作为错误信息的一部分抛出
        error_with_logs = f"训练失败\n\n详细日志:\n" + "\n".join(logs)
        raise Exception(error_with_logs)
