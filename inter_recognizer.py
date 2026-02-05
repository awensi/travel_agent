import torch
import torch.nn as nn
from transformers import BertTokenizer, BertModel
from typing import Dict
import regex as re

class InterRecognizer:
    
    def __init__(self, model_path="D:\\files\\AIModels\\models--bert-base-chinese\\snapshots\\8f23c25b06e129b6c986331a13d8d025a92cf0ea"):
        self.tokenizer = BertTokenizer.from_pretrained(model_path)
        self.model = BertModel.from_pretrained(model_path)
        for param in self.model.parameters():
            param.requires_grad = False
        self.classifier = nn.Linear(768, 4)  #5个意图识别类别
        
        self.categories = ["地点", "预算", "排除", "兴趣"]
        # self.categories = ["查询天气", "设置闹钟", "播放音乐", "搜索信息"]
        # 术语提取模式
        # 针对旅游领域的多意图术语提取模式
        self.term_patterns = {
            "地点": [
                # 城市名称模式
                r"去(.{2,8}?)(?:旅游|旅行|游玩|度假)",
                r"到(.{2,8}?)(?:旅游|旅行|游玩)",
                r"在(.{2,8}?)(?:玩|旅游|旅行)",
                r"想去(.{2,8}?)(?:旅游|旅行)",
                r"(.{2,8}?)(?:市|省|区|县)(?:旅游|旅行)",
                r"目的地是(.{2,10}?)",
                r"地点(.{2,10}?)",
                
                # 具体景点模式
                r"参观(.{2,10}?)(?:景点|景区|地方)",
                r"游览(.{2,10}?)(?:景点|景区)",
                r"玩(.{2,8}?)(?:景点|地方)",
                r"(.{2,10}?)(?:景点|景区|名胜)",
                
                # 简单地点提及
                r"(\b(?:北京|上海|广州|深圳|杭州|成都|西安|南京|苏州|厦门|青岛|大连|昆明|丽江|大理|三亚|桂林|张家界|九寨沟|黄山|西藏|新疆|内蒙古)\b)",
                r"(\b(?:云南|四川|海南|浙江|江苏|广东|福建|山东|辽宁|湖南|湖北|陕西)\b)",
            ],
            
            "预算": [
                # 明确预算模式
                r"预算(.{1,10}?)(?:元|块|钱)",
                r"花费(.{1,10}?)(?:元|块|钱)",
                r"价格(.{1,10}?)(?:元|块|钱)",
                r"费用(.{1,10}?)(?:元|块|钱)",
                r"准备(.{1,10}?)(?:元|块|钱)",
                r"打算花(.{1,10}?)(?:元|块|钱)",
                
                # 金额范围模式
                r"(\d+)[\-~～](\d+)(?:元|块|钱)",
                r"(\d+)(?:多|左右|大概|大约|差不多)(?:元|块|钱)",
                r"(\d+)(?:千|k)(?:元|块|钱)?",
                r"(\d+)(?:万|w)(?:元|块|钱)?",
                
                # 简单金额提及
                r"(\d+)(?:元|块|钱)",
                r"花费(\d+)",
                r"价格(\d+)",
                r"(\d+)的预算",
                
                # 预算水平描述
                r"(高预算|豪华|奢侈|高端)",
                r"(中档|适中|一般|普通)",
                r"(经济|便宜|省钱|低预算)",
            ],
            
            "排除": [
                # 明确排除模式
                r"不(.{1,8}?)(?:去|玩|参观|游览)",
                r"避免(.{1,10}?)",
                r"排除(.{1,10}?)",
                r"不要(.{1,10}?)",
                r"别(.{1,8}?)(?:去|玩)",
                r"拒绝(.{1,10}?)",
                r"避开(.{1,10}?)",
                
                # 负面偏好模式
                r"不喜欢(.{1,10}?)",
                r"讨厌(.{1,8}?)",
                r"反感(.{1,8}?)",
                r"怕(.{1,8}?)",
                
                # 条件排除模式
                r"太(.{1,6}?)(?:的?地方|的?景点)",
                r"过于(.{1,6}?)(?:的?地方|的?景点)",
                r"人太多",
                r"太拥挤",
                r"商业化",
                r"太贵",
                
                # 具体排除项
                r"排除(.{1,10}?)(?:类型|类别|地方)",
                r"不要(.{1,10}?)(?:的|之)?游",
                r"避免(.{1,10}?)(?:的|之)?景点",
            ],
            
            "兴趣": [
                # 明确兴趣模式
                r"喜欢(.{1,12}?)",
                r"感兴趣(.{1,12}?)",
                r"爱好(.{1,10}?)",
                r"想(.{1,10}?)(?:体验|感受|尝试)",
                r"希望(.{1,10}?)",
                r"想要(.{1,10}?)",
                r"钟意(.{1,10}?)",
                r"热爱(.{1,10}?)",
                
                # 兴趣类别模式
                r"对(.{1,12}?)(?:感兴趣|有兴趣|很喜欢)",
                r"对(.{1,12}?)(?:有热情|有感觉)",
                r"偏爱(.{1,10}?)",
                r"倾向于(.{1,10}?)",
                
                # 具体兴趣内容
                r"喜欢(.{1,10}?)(?:文化|历史|艺术|音乐|美食|购物|自然|风光|探险|休闲)",
                r"对(.{1,10}?)(?:文化|历史|艺术|音乐|美食|购物|自然|风光|探险|休闲)感兴趣",
                
                # 活动类型兴趣
                r"想体验(.{1,10}?)(?:活动|项目)",
                r"喜欢(.{1,8}?)(?:游|旅行|旅游)方式",
                r"倾向于(.{1,8}?)(?:类型|风格)的旅行",
            ]
        }
        # 设置多标签分类的阈值
        self.confidence_threshold = 0.3  # 置信度阈值，超过这个值就认为包含该意图


    def extract_intent(self, user_request : str) -> Dict:
        #使用bert进行意图识别
        #tokenize输入
        input = self.tokenizer(user_request, 
                               return_tensors='pt',
                               truncation=True, 
                               padding=True, 
                               max_length=128)
        #torch.no_grad()详解
#1. 核心作用：禁用梯度计算
#torch.no_grad()是一个上下文管理器，在它的作用域内，PyTorch不会计算和存储梯度
        with torch.no_grad():
            outputs = self.model(**input)
            pooled_output = outputs.pooler_output

            #分类预测
            logits = self.classifier(pooled_output)
            # #线性降维，将4维降至一维
            # probabilities = torch.softmax(logits, dim=1)
            # #获取可能性最大的预测
            # confidence, predicted = torch.max(probabilities, 1)
            probalities = torch.sigmoid(logits)
        
        detected_intents = []
        probs = probalities[0].tolist() #转换为列表

        for i,confidence in enumerate(probs):
            if confidence >= self.confidence_threshold:
                category = self.categories[i]
                term = self._extract_term_for_category(user_request, category)

                intent_result = {
                    "category": category,
                    "term": term,
                    "confidence": round(confidence, 2)
                }
                detected_intents.append(intent_result)
        if not detected_intents:
            return self._format_result("未知意图", " ", 0.1)
        #按照置信度排序
        detected_intents.sort(key=lambda x: x["confidence"], reverse=True)
        return detected_intents

        # category = self.categories[predicted.item()]
        # term = self._extract_term_with_ner(user_request, category)
        # confidence_value = confidence.item()

        # return self._format_result(category, term, confidence_value)

    def _extract_term_for_category(self, user_request, category):
        #为特定意图类别提取术语
        if category not in self.term_patterns:
            return ""
        for pattern in self.term_patterns[category]:
            match = re.search(pattern, user_request)
            if match:
                for group in match.groups():
                    if group and self._is_valid_term(group):
                        return group.strip()
                if match.group(0):
                    return match.group[0].strip()
        return ""
    
    def _extract_term_with_ner(self, user_request, category) -> str:
        #结合规则和简单的NER提取术语
        if category not in self.term_patterns[category]:
            return ""
        
        for pattern in self.term_patterns[category]:
            match = re.search(pattern, user_request)
            if match:
                #提取第一个有效的捕获组
                for group in match.groups():
                    if group and self._is_valid_term(group):
                        return group.strip()
        return ""


    def _is_valid_term(self, term: str) -> bool:
        #检查术语是否有效
        if not term or len(term) > 20:
            return False
        # 过滤掉常见的功能词
        invalid_terms = {"的", "了", "在", "是", "有", "和", "就", "都", "很", "一些", "什么"}
        return term not in invalid_terms
    
    def _format_result(self, category, term, confidence_value):
        #格式化输出
        return {
            "category": category,
            "term": term,
            "confidence": round(confidence_value, 2)
        }

if __name__ == "__main__":
    print("begin")
    recognizer = InterRecognizer()
    
    test_case = "我想去云南旅游，旅游时间在8天，预算八千块，不喜欢商业化的景点，对人文景观这些地方感兴趣"
    result = recognizer.extract_intent(test_case)
    print(result)
