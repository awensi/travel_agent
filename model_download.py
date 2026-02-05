#!/usr/bin/env python3
"""
BERT-base-Chinese 模型下载和使用完整示例
"""

import os
os.environ['HF_ENDPOINT'] = 'https://hf-mirror.com'
import torch
from transformers import BertTokenizer, BertModel, BertForSequenceClassification


class BertChineseDownloader:
    def __init__(self, model_name="bert-base-chinese", local_dir="./models/bert-base-chinese"):
        self.model_name = model_name
        self.local_dir = local_dir
        self.model = None
        self.tokenizer = None
    
    def download_model(self, use_mirror=False):
        """下载模型"""
        os.makedirs(self.local_dir, exist_ok=True)
        
        if use_mirror:
            # 使用镜像
            os.environ['HF_ENDPOINT'] = 'https://hf-mirror.com'
            print("使用国内镜像下载...")
        
        print(f"开始下载模型: {self.model_name}")
        print(f"保存到: {self.local_dir}")
        
        # 下载tokenizer
        print("下载tokenizer...")
        self.tokenizer = BertTokenizer.from_pretrained(
            self.model_name,
            cache_dir=self.local_dir
        )
        
        # 下载模型
        print("下载模型...")
        self.model = BertModel.from_pretrained(
            self.model_name,
            cache_dir=self.local_dir
        )
        
        # 保存到指定目录
        self.model.save_pretrained(self.local_dir)
        self.tokenizer.save_pretrained(self.local_dir)
        
        print("下载完成！")
        
        # 显示模型信息
        self.show_model_info()
        
        return self.local_dir
    
    def show_model_info(self):
        """显示模型信息"""
        if self.model and self.tokenizer:
            print("\n" + "="*50)
            print("模型信息:")
            print(f"模型名称: {self.model_name}")
            print(f"参数量: {sum(p.numel() for p in self.model.parameters()):,}")
            print(f"隐藏层大小: {self.model.config.hidden_size}")
            print(f"注意力头数: {self.model.config.num_attention_heads}")
            print(f"层数: {self.model.config.num_hidden_layers}")
            print(f"词汇表大小: {self.tokenizer.vocab_size}")
            print("="*50)
    
    def test_model(self, text="这是一个测试句子"):
        """测试模型"""
        if not self.model or not self.tokenizer:
            print("请先下载模型！")
            return
        
        print(f"\n测试文本: {text}")
        
        # 编码
        inputs = self.tokenizer(text, return_tensors="pt", padding=True, truncation=True)
        print(f"Token IDs: {inputs['input_ids']}")
        print(f"Tokens: {self.tokenizer.convert_ids_to_tokens(inputs['input_ids'][0])}")
        
        # 前向传播
        with torch.no_grad():
            outputs = self.model(**inputs)
        
        print(f"输出形状: {outputs.last_hidden_state.shape}")
        print(f"[CLS]向量形状: {outputs.pooler_output.shape}")
        
        return outputs

# 使用示例
if __name__ == "__main__":
    # 创建下载器
    downloader = BertChineseDownloader(
        model_name="bert-base-chinese",
        local_dir="D:\\files\\AIModels"  # 本地保存路径
    )
    
    # 下载模型（国内用户可以使用 use_mirror=True）
    model_path = downloader.download_model(use_mirror=True)
    
    # 测试模型
    test_texts = [
        "自然语言处理是人工智能的重要方向",
        "BERT模型在多个NLP任务上取得了领先效果",
        "今天天气真好，适合学习深度学习"
    ]
    
    for text in test_texts:
        downloader.test_model(text)
        print()