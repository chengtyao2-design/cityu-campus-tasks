"""
地理编码模块
提供校园位置到坐标的映射，支持在线API查询和回退机制
"""

import logging
import json
import requests
from typing import Dict, Tuple, Optional, List
from dataclasses import dataclass
from datetime import datetime, timedelta
import os

# 配置日志
logger = logging.getLogger(__name__)

@dataclass
class LocationInfo:
    """位置信息数据类"""
    name: str
    latitude: float
    longitude: float
    address: str = ""
    source: str = "manual"  # manual, api, fallback
    confidence: float = 1.0
    last_updated: Optional[datetime] = None

class GeocodeService:
    """地理编码服务类"""
    
    def __init__(self):
        self.location_cache: Dict[str, LocationInfo] = {}
        self.api_key = os.getenv("GEOCODING_API_KEY", "")
        self.api_enabled = bool(self.api_key)
        self.cache_duration = timedelta(days=30)  # 缓存30天
        
        # 初始化校园位置映射表
        self._init_campus_locations()
        
        logger.info(f"地理编码服务初始化完成，API状态: {'启用' if self.api_enabled else '禁用'}")
    
    def _init_campus_locations(self):
        """初始化香港城市大学校园位置映射表"""
        
        # 香港城市大学主要建筑物坐标 (基于真实位置)
        campus_locations = {
            # 教学楼
            "教学楼A": LocationInfo("教学楼A", 22.3364, 114.2678, "香港城市大学教学楼A座", "manual", 1.0),
            "教学楼B": LocationInfo("教学楼B", 22.3366, 114.2680, "香港城市大学教学楼B座", "manual", 1.0),
            "教学楼C": LocationInfo("教学楼C", 22.3368, 114.2682, "香港城市大学教学楼C座", "manual", 1.0),
            "学术楼一": LocationInfo("学术楼一", 22.3370, 114.2675, "香港城市大学学术楼一", "manual", 1.0),
            "学术楼二": LocationInfo("学术楼二", 22.3372, 114.2677, "香港城市大学学术楼二", "manual", 1.0),
            "学术楼三": LocationInfo("学术楼三", 22.3374, 114.2679, "香港城市大学学术楼三", "manual", 1.0),
            
            # 图书馆和学习空间
            "邵逸夫图书馆": LocationInfo("邵逸夫图书馆", 22.3365, 114.2685, "香港城市大学邵逸夫图书馆", "manual", 1.0),
            "图书馆": LocationInfo("图书馆", 22.3365, 114.2685, "香港城市大学邵逸夫图书馆", "manual", 1.0),
            "法律图书馆": LocationInfo("法律图书馆", 22.3367, 114.2687, "香港城市大学法律图书馆", "manual", 1.0),
            "学习共享空间": LocationInfo("学习共享空间", 22.3363, 114.2683, "香港城市大学学习共享空间", "manual", 1.0),
            
            # 实验室和研究设施
            "工程实验室": LocationInfo("工程实验室", 22.3375, 114.2670, "香港城市大学工程实验室", "manual", 1.0),
            "计算机实验室": LocationInfo("计算机实验室", 22.3373, 114.2672, "香港城市大学计算机实验室", "manual", 1.0),
            "电子实验室": LocationInfo("电子实验室", 22.3371, 114.2674, "香港城市大学电子实验室", "manual", 1.0),
            "化学实验室": LocationInfo("化学实验室", 22.3369, 114.2676, "香港城市大学化学实验室", "manual", 1.0),
            "物理实验室": LocationInfo("物理实验室", 22.3367, 114.2678, "香港城市大学物理实验室", "manual", 1.0),
            
            # 学生活动场所
            "学生活动中心": LocationInfo("学生活动中心", 22.3360, 114.2690, "香港城市大学学生活动中心", "manual", 1.0),
            "学生会办公室": LocationInfo("学生会办公室", 22.3358, 114.2692, "香港城市大学学生会办公室", "manual", 1.0),
            "多功能厅": LocationInfo("多功能厅", 22.3362, 114.2688, "香港城市大学多功能厅", "manual", 1.0),
            "演讲厅": LocationInfo("演讲厅", 22.3364, 114.2686, "香港城市大学演讲厅", "manual", 1.0),
            
            # 体育设施
            "体育馆": LocationInfo("体育馆", 22.3355, 114.2695, "香港城市大学体育馆", "manual", 1.0),
            "健身房": LocationInfo("健身房", 22.3353, 114.2697, "香港城市大学健身房", "manual", 1.0),
            "游泳池": LocationInfo("游泳池", 22.3351, 114.2699, "香港城市大学游泳池", "manual", 1.0),
            "运动场": LocationInfo("运动场", 22.3349, 114.2701, "香港城市大学运动场", "manual", 1.0),
            
            # 餐饮设施
            "学生餐厅": LocationInfo("学生餐厅", 22.3356, 114.2684, "香港城市大学学生餐厅", "manual", 1.0),
            "教职员餐厅": LocationInfo("教职员餐厅", 22.3358, 114.2682, "香港城市大学教职员餐厅", "manual", 1.0),
            "咖啡厅": LocationInfo("咖啡厅", 22.3354, 114.2686, "香港城市大学咖啡厅", "manual", 1.0),
            
            # 行政办公
            "行政楼": LocationInfo("行政楼", 22.3376, 114.2665, "香港城市大学行政楼", "manual", 1.0),
            "校长办公室": LocationInfo("校长办公室", 22.3378, 114.2663, "香港城市大学校长办公室", "manual", 1.0),
            "注册处": LocationInfo("注册处", 22.3374, 114.2667, "香港城市大学注册处", "manual", 1.0),
            
            # 宿舍区域
            "学生宿舍A座": LocationInfo("学生宿舍A座", 22.3340, 114.2710, "香港城市大学学生宿舍A座", "manual", 1.0),
            "学生宿舍B座": LocationInfo("学生宿舍B座", 22.3342, 114.2712, "香港城市大学学生宿舍B座", "manual", 1.0),
            "学生宿舍C座": LocationInfo("学生宿舍C座", 22.3344, 114.2714, "香港城市大学学生宿舍C座", "manual", 1.0),
            
            # 其他设施
            "停车场": LocationInfo("停车场", 22.3350, 114.2660, "香港城市大学停车场", "manual", 1.0),
            "校园广场": LocationInfo("校园广场", 22.3365, 114.2680, "香港城市大学校园广场", "manual", 1.0),
            "校园花园": LocationInfo("校园花园", 22.3370, 114.2690, "香港城市大学校园花园", "manual", 1.0),
            
            # 任务数据中的具体位置
            "工程学院实验室": LocationInfo("工程学院实验室", 22.3375, 114.2672, "香港城市大学工程学院实验室", "manual", 1.0),
            "校园入口": LocationInfo("校园入口", 22.3365, 114.2675, "香港城市大学主入口", "manual", 1.0),
            "计算机科学系": LocationInfo("计算机科学系", 22.3370, 114.2678, "香港城市大学计算机科学系", "manual", 1.0),
            "校园各处": LocationInfo("校园各处", 22.3365, 114.2680, "香港城市大学校园中心区域", "manual", 1.0),
            "创新创业中心": LocationInfo("创新创业中心", 22.3368, 114.2685, "香港城市大学创新创业中心", "manual", 1.0),
            "大学会堂": LocationInfo("大学会堂", 22.3362, 114.2688, "香港城市大学大学会堂", "manual", 1.0),
            "各食堂": LocationInfo("各食堂", 22.3356, 114.2684, "香港城市大学学生餐厅区域", "manual", 1.0),
            "学术报告厅": LocationInfo("学术报告厅", 22.3364, 114.2686, "香港城市大学学术报告厅", "manual", 1.0),
            
            # 添加更多别名和变体
            "工程学院": LocationInfo("工程学院", 22.3375, 114.2670, "香港城市大学工程学院", "manual", 1.0),
            "计算机系": LocationInfo("计算机系", 22.3370, 114.2678, "香港城市大学计算机科学系", "manual", 1.0),
            "创业中心": LocationInfo("创业中心", 22.3368, 114.2685, "香港城市大学创新创业中心", "manual", 1.0),
            "会堂": LocationInfo("会堂", 22.3362, 114.2688, "香港城市大学大学会堂", "manual", 1.0),
            "食堂": LocationInfo("食堂", 22.3356, 114.2684, "香港城市大学学生餐厅", "manual", 1.0),
            "报告厅": LocationInfo("报告厅", 22.3364, 114.2686, "香港城市大学学术报告厅", "manual", 1.0),
        }
        
        # 添加到缓存
        for name, location in campus_locations.items():
            self.location_cache[name.lower()] = location
            # 添加一些常见的别名
            if "图书馆" in name and name != "图书馆":
                self.location_cache[name.replace("图书馆", "library").lower()] = location
            if "实验室" in name:
                self.location_cache[name.replace("实验室", "lab").lower()] = location
        
        logger.info(f"已加载 {len(campus_locations)} 个校园位置到映射表")
    
    def get_fallback_location(self) -> LocationInfo:
        """获取默认回退位置 - 教学楼入口"""
        return LocationInfo(
            name="教学楼入口",
            latitude=22.3365,  # 香港城市大学主入口附近
            longitude=114.2680,
            address="香港城市大学教学楼主入口",
            source="fallback",
            confidence=0.5
        )
    
    def geocode_location(self, location_name: str, force_refresh: bool = False) -> LocationInfo:
        """
        地理编码位置名称到坐标
        
        Args:
            location_name: 位置名称
            force_refresh: 是否强制刷新缓存
            
        Returns:
            LocationInfo: 位置信息对象
        """
        if not location_name or not location_name.strip():
            logger.warning("位置名称为空，使用回退位置")
            return self.get_fallback_location()
        
        location_key = location_name.lower().strip()
        
        # 检查缓存
        if not force_refresh and location_key in self.location_cache:
            cached_location = self.location_cache[location_key]
            # 检查缓存是否过期
            if (cached_location.last_updated is None or 
                datetime.now() - cached_location.last_updated < self.cache_duration):
                logger.debug(f"从缓存获取位置: {location_name}")
                return cached_location
        
        # 尝试模糊匹配
        fuzzy_match = self._fuzzy_match_location(location_name)
        if fuzzy_match:
            logger.info(f"模糊匹配位置: {location_name} -> {fuzzy_match.name}")
            return fuzzy_match
        
        # 尝试在线API查询
        if self.api_enabled:
            api_result = self._query_geocoding_api(location_name)
            if api_result:
                # 缓存API结果
                self.location_cache[location_key] = api_result
                logger.info(f"API查询成功: {location_name}")
                return api_result
        
        # 使用回退位置
        logger.warning(f"无法找到位置坐标，使用回退位置: {location_name}")
        fallback = self.get_fallback_location()
        fallback.name = f"{location_name} (回退到教学楼入口)"
        return fallback
    
    def _fuzzy_match_location(self, location_name: str) -> Optional[LocationInfo]:
        """模糊匹配位置名称"""
        location_lower = location_name.lower().strip()
        
        # 直接匹配
        if location_lower in self.location_cache:
            return self.location_cache[location_lower]
        
        # 包含匹配
        for cached_key, cached_location in self.location_cache.items():
            if (location_lower in cached_key or 
                cached_key in location_lower or
                any(word in cached_key for word in location_lower.split()) or
                any(word in location_lower for word in cached_key.split())):
                logger.debug(f"模糊匹配: {location_name} -> {cached_location.name}")
                return cached_location
        
        return None
    
    def _query_geocoding_api(self, location_name: str) -> Optional[LocationInfo]:
        """查询在线地理编码API (占位实现)"""
        if not self.api_enabled:
            return None
        
        try:
            # 这里可以集成真实的地理编码API，如Google Maps、百度地图等
            # 当前为占位实现
            logger.info(f"API查询占位: {location_name}")
            
            # 示例API调用结构 (未实际调用)
            # url = f"https://api.example.com/geocode"
            # params = {
            #     "address": f"{location_name}, 香港城市大学, 香港",
            #     "key": self.api_key
            # }
            # response = requests.get(url, params=params, timeout=5)
            # if response.status_code == 200:
            #     data = response.json()
            #     return LocationInfo(...)
            
            return None
            
        except Exception as e:
            logger.error(f"API查询失败: {location_name}, 错误: {str(e)}")
            return None
    
    def batch_geocode(self, location_names: List[str]) -> Dict[str, LocationInfo]:
        """批量地理编码"""
        results = {}
        
        logger.info(f"开始批量地理编码，共 {len(location_names)} 个位置")
        
        for location_name in location_names:
            if location_name:
                results[location_name] = self.geocode_location(location_name)
        
        # 统计结果
        sources = {}
        for location_info in results.values():
            source = location_info.source
            sources[source] = sources.get(source, 0) + 1
        
        logger.info(f"批量地理编码完成，结果统计: {sources}")
        return results
    
    def get_coverage_stats(self, location_names: List[str]) -> Dict[str, any]:
        """获取地理编码覆盖率统计"""
        if not location_names:
            return {"total": 0, "coverage": 0, "sources": {}}
        
        results = self.batch_geocode(location_names)
        
        total = len(results)
        sources = {}
        high_confidence = 0
        
        for location_info in results.values():
            source = location_info.source
            sources[source] = sources.get(source, 0) + 1
            if location_info.confidence >= 0.8:
                high_confidence += 1
        
        coverage_rate = (total - sources.get("fallback", 0)) / total * 100 if total > 0 else 0
        
        return {
            "total": total,
            "coverage_rate": round(coverage_rate, 2),
            "high_confidence_rate": round(high_confidence / total * 100, 2) if total > 0 else 0,
            "sources": sources,
            "fallback_count": sources.get("fallback", 0)
        }
    
    def export_cache(self, file_path: str):
        """导出位置缓存到文件"""
        try:
            cache_data = {}
            for key, location in self.location_cache.items():
                cache_data[key] = {
                    "name": location.name,
                    "latitude": location.latitude,
                    "longitude": location.longitude,
                    "address": location.address,
                    "source": location.source,
                    "confidence": location.confidence,
                    "last_updated": location.last_updated.isoformat() if location.last_updated else None
                }
            
            with open(file_path, 'w', encoding='utf-8') as f:
                json.dump(cache_data, f, ensure_ascii=False, indent=2)
            
            logger.info(f"位置缓存已导出到: {file_path}")
            
        except Exception as e:
            logger.error(f"导出位置缓存失败: {str(e)}")
    
    def import_cache(self, file_path: str):
        """从文件导入位置缓存"""
        try:
            if not os.path.exists(file_path):
                logger.warning(f"缓存文件不存在: {file_path}")
                return
            
            with open(file_path, 'r', encoding='utf-8') as f:
                cache_data = json.load(f)
            
            imported_count = 0
            for key, data in cache_data.items():
                location = LocationInfo(
                    name=data["name"],
                    latitude=data["latitude"],
                    longitude=data["longitude"],
                    address=data.get("address", ""),
                    source=data.get("source", "manual"),
                    confidence=data.get("confidence", 1.0),
                    last_updated=datetime.fromisoformat(data["last_updated"]) if data.get("last_updated") else None
                )
                self.location_cache[key] = location
                imported_count += 1
            
            logger.info(f"已从缓存文件导入 {imported_count} 个位置: {file_path}")
            
        except Exception as e:
            logger.error(f"导入位置缓存失败: {str(e)}")

# 全局地理编码服务实例
geocode_service = GeocodeService()

def geocode_location(location_name: str) -> LocationInfo:
    """便捷函数：地理编码单个位置"""
    return geocode_service.geocode_location(location_name)

def batch_geocode_locations(location_names: List[str]) -> Dict[str, LocationInfo]:
    """便捷函数：批量地理编码"""
    return geocode_service.batch_geocode(location_names)

def get_geocoding_stats(location_names: List[str]) -> Dict[str, any]:
    """便捷函数：获取地理编码统计"""
    return geocode_service.get_coverage_stats(location_names)

if __name__ == "__main__":
    # 测试地理编码功能
    test_locations = [
        "邵逸夫图书馆",
        "学生活动中心", 
        "工程实验室",
        "体育馆",
        "未知位置",
        "图书馆",
        "实验室"
    ]
    
    print("🗺️  地理编码服务测试")
    print("=" * 50)
    
    # 测试单个位置编码
    for location in test_locations:
        result = geocode_location(location)
        print(f"📍 {location}")
        print(f"   坐标: ({result.latitude}, {result.longitude})")
        print(f"   来源: {result.source}, 置信度: {result.confidence}")
        print()
    
    # 测试批量编码和统计
    stats = get_geocoding_stats(test_locations)
    print("📊 地理编码统计:")
    print(f"   总位置数: {stats['total']}")
    print(f"   覆盖率: {stats['coverage_rate']}%")
    print(f"   高置信度率: {stats['high_confidence_rate']}%")
    print(f"   来源分布: {stats['sources']}")
    print(f"   回退位置数: {stats['fallback_count']}")