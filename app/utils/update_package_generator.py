import os
import json
import zipfile
import hashlib
import shutil
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Optional, Tuple

class UpdatePackageGenerator:
    def __init__(self, project_root: str = None):
        # 优先使用传入的项目路径，否则使用当前工作目录
        if project_root:
            self.project_root = Path(project_root)
        else:
            self.project_root = Path.cwd()
        
        self.static_dir = self.project_root / 'static'
        self.updates_dir = self.static_dir / 'updates'
        self.frontend_dir = self.project_root / 'frontend'
        self.backend_dir = self.project_root / 'app'
        self.client_dir = self.project_root / 'client'
        
        # 确保更新目录存在
        self.updates_dir.mkdir(parents=True, exist_ok=True)
    
    def get_current_version(self) -> str:
        """获取当前版本号"""
        version_file = self.project_root / 'VERSION'
        if version_file.exists():
            with open(version_file, 'r', encoding='utf-8') as f:
                return f.read().strip()
        return '1.0.0'
    
    def get_git_hash(self) -> str:
        """获取当前Git提交哈希"""
        try:
            # 尝试导入git模块，如果失败则返回unknown
            import git
            repo = git.Repo(self.project_root)
            return repo.head.object.hexsha[:8]
        except ImportError:
            # 如果没有安装GitPython，返回unknown
            return 'unknown'
        except Exception:
            # 其他错误也返回unknown
            return 'unknown'
    
    def calculate_hash(self, file_path: Path) -> str:
        """计算文件的MD5哈希值"""
        hash_md5 = hashlib.md5()
        with open(file_path, "rb") as f:
            for chunk in iter(lambda: f.read(4096), b""):
                hash_md5.update(chunk)
        return hash_md5.hexdigest()
    
    def calculate_directory_hash(self, directory: Path, exclude_patterns: List[str] = None) -> str:
        """计算目录的哈希值（基于所有文件的哈希值）"""
        if exclude_patterns is None:
            exclude_patterns = []
        
        hash_values = []
        
        for file_path in directory.rglob('*'):
            if file_path.is_file():
                # 检查是否应该排除
                should_exclude = False
                for pattern in exclude_patterns:
                    if pattern in str(file_path):
                        should_exclude = True
                        break
                
                if not should_exclude:
                    file_hash = self.calculate_hash(file_path)
                    relative_path = file_path.relative_to(directory)
                    hash_values.append(f"{relative_path}:{file_hash}")
        
        # 排序确保一致性
        hash_values.sort()
        
        # 计算组合哈希值
        combined = ''.join(hash_values)
        return hashlib.md5(combined.encode()).hexdigest()
    
    def create_update_package(self, 
                             package_type: str = 'full',
                             include_frontend: bool = True,
                             include_backend: bool = True,
                             include_client: bool = False) -> Dict:
        """创建更新包
        
        Args:
            package_type: 包类型 ('electron', 'flask', 'docker', 'full')
            include_frontend: 是否包含前端文件
            include_backend: 是否包含后端文件
            include_client: 是否包含客户端文件
        """
        try:
            current_version = self.get_current_version()
            git_hash = self.get_git_hash()
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            
            # 生成包名
            package_name = f"log-analyzer-{package_type}-{current_version}-{git_hash}-{timestamp}.zip"
            package_path = self.updates_dir / package_name
            
            # 创建ZIP文件
            with zipfile.ZipFile(package_path, 'w', zipfile.ZIP_DEFLATED) as zipf:
                # 添加前端文件
                if include_frontend and self.frontend_dir.exists():
                    self._add_frontend_files(zipf)
                
                # 添加后端文件
                if include_backend and self.backend_dir.exists():
                    self._add_backend_files(zipf)
                
                # 添加客户端文件
                if include_client and self.client_dir.exists():
                    self._add_client_files(zipf)
                
                # 添加版本信息
                version_info = {
                    'version': current_version,
                    'git_hash': git_hash,
                    'timestamp': timestamp,
                    'package_type': package_type,
                    'package_name': package_name,
                    'includes': {
                        'frontend': include_frontend,
                        'backend': include_backend,
                        'client': include_client
                    }
                }
                
                zipf.writestr('version.json', json.dumps(version_info, indent=2, ensure_ascii=False))
            
            # 创建版本特定的JSON文件
            version_json_path = self.updates_dir / f"version-{current_version}-{git_hash}.json"
            with open(version_json_path, 'w', encoding='utf-8') as f:
                json.dump(version_info, f, indent=2, ensure_ascii=False)
            
            # 更新latest.json
            self._update_latest_json(version_info)
            
            return {
                'success': True,
                'package_name': package_name,
                'package_path': str(package_path),
                'version_info': version_info
            }
            
        except Exception as e:
            return {
                'success': False,
                'error': str(e)
            }
    
    def _add_frontend_files(self, zipf: zipfile.ZipFile):
        """添加前端文件到ZIP包"""
        frontend_excludes = [
            'node_modules',
            '.git',
            'dist',
            'build',
            'coverage',
            '.nyc_output',
            '.env',
            '.env.local',
            '.env.development.local',
            '.env.test.local',
            '.env.production.local'
        ]
        
        for file_path in self.frontend_dir.rglob('*'):
            if file_path.is_file():
                # 检查是否应该排除
                should_exclude = False
                for exclude in frontend_excludes:
                    if exclude in str(file_path):
                        should_exclude = True
                        break
                
                if not should_exclude:
                    relative_path = file_path.relative_to(self.project_root)
                    zipf.write(file_path, relative_path)
    
    def _add_backend_files(self, zipf: zipfile.ZipFile):
        """添加后端文件到ZIP包"""
        backend_excludes = [
            '__pycache__',
            '.pyc',
            '.pyo',
            '.pyd',
            '.git',
            'tests',
            'test_',
            '.env',
            'venv',
            'env',
            '.pytest_cache',
            '.coverage'
        ]
        
        for file_path in self.backend_dir.rglob('*'):
            if file_path.is_file():
                # 检查是否应该排除
                should_exclude = False
                for exclude in backend_excludes:
                    if exclude in str(file_path):
                        should_exclude = True
                        break
                
                if not should_exclude:
                    relative_path = file_path.relative_to(self.project_root)
                    zipf.write(file_path, relative_path)
    
    def _add_client_files(self, zipf: zipfile.ZipFile):
        """添加客户端文件到ZIP包"""
        client_excludes = [
            'node_modules',
            '.git',
            'dist',
            'build',
            'coverage',
            '.nyc_output',
            '.env',
            '.env.local',
            '.env.development.local',
            '.env.test.local',
            '.env.production.local',
            'python-app'  # 不包含Python应用，因为这是Flask更新包
        ]
        
        for file_path in self.client_dir.rglob('*'):
            if file_path.is_file():
                # 检查是否应该排除
                should_exclude = False
                for exclude in client_excludes:
                    if exclude in str(file_path):
                        should_exclude = True
                        break
                
                if not should_exclude:
                    relative_path = file_path.relative_to(self.project_root)
                    zipf.write(file_path, relative_path)
    
    def _update_latest_json(self, version_info: Dict):
        """更新latest.json文件"""
        latest_json_path = self.updates_dir / 'latest.json'
        
        latest_info = {
            'version': version_info['version'],
            'git_hash': version_info['git_hash'],
            'timestamp': version_info['timestamp'],
            'package_type': version_info['package_type'],
            'package_name': version_info['package_name'],
            'download_url': f"/api/updates/download/{version_info['version']}",
            'includes': version_info['includes']
        }
        
        with open(latest_json_path, 'w', encoding='utf-8') as f:
            json.dump(latest_info, f, indent=2, ensure_ascii=False)
    
    def check_for_updates(self, current_version: str, current_hash: str) -> Optional[Dict]:
        """检查是否有可用更新"""
        try:
            latest_file = self.updates_dir / 'latest.json'
            if not latest_file.exists():
                return None
            
            with open(latest_file, 'r', encoding='utf-8') as f:
                latest_info = json.load(f)
            
            # 检查版本和哈希值
            if (latest_info['version'] != current_version or 
                latest_info['git_hash'] != current_hash):
                return latest_info
            
            return None
            
        except Exception as e:
            print(f"Error checking for updates: {e}")
            return None
    
    def list_available_packages(self) -> List[Dict]:
        """列出所有可用的更新包"""
        packages = []
        
        try:
            for zip_file in self.updates_dir.glob('*.zip'):
                # 尝试从ZIP包中读取版本信息
                try:
                    with zipfile.ZipFile(zip_file, 'r') as zipf:
                        if 'version.json' in zipf.namelist():
                            version_data = json.loads(zipf.read('version.json').decode('utf-8'))
                            packages.append({
                                'file_name': zip_file.name,
                                'file_size': zip_file.stat().st_size,
                                'version_info': version_data
                            })
                except Exception:
                    # 如果无法读取版本信息，只提供基本信息
                    packages.append({
                        'file_name': zip_file.name,
                        'file_size': zip_file.stat().st_size,
                        'version_info': None
                    })
        except Exception as e:
            print(f"Error listing packages: {e}")
        
        return packages
    
    def clean_old_packages(self, keep_count: int = 5) -> Dict:
        """清理旧的更新包，保留最新的几个"""
        try:
            packages = self.list_available_packages()
            
            # 按时间戳排序
            packages.sort(key=lambda x: x['version_info']['timestamp'] if x['version_info'] else '0', reverse=True)
            
            # 删除多余的包
            deleted_count = 0
            for package in packages[keep_count:]:
                try:
                    package_path = self.updates_dir / package['file_name']
                    if package_path.exists():
                        package_path.unlink()
                        deleted_count += 1
                except Exception as e:
                    print(f"Failed to delete {package['file_name']}: {e}")
            
            return {
                'success': True,
                'deleted_count': deleted_count,
                'remaining_count': len(packages) - deleted_count
            }
            
        except Exception as e:
            return {
                'success': False,
                'error': str(e)
            }
    
    # 兼容性方法
    def generate_docker_update_package(self) -> Dict:
        """生成Docker更新包（兼容性方法）"""
        return self.create_update_package(
            package_type='docker',
            include_frontend=True,
            include_backend=True,
            include_client=False
        )
    
    def generate_client_update_package(self) -> Dict:
        """生成客户端更新包（兼容性方法）"""
        return self.create_update_package(
            package_type='client',
            include_frontend=True,
            include_backend=False,
            include_client=True
        )
