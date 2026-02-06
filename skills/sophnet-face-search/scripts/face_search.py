#!/usr/bin/env python3
"""
人脸检索脚本
支持两步流程：
1. 输入一张查询图片，检测最大人脸并提取embedding
2. 输入图片列表，检测所有人脸并计算相似度
"""

import requests
import os
import sys
import json
import argparse
import cv2
import numpy as np
from pathlib import Path

# API配置
FACE_API_URL = "https://www.sophnet.com/api/open-apis/projects/detect_and_embed"

# 默认阈值
DEFAULT_QUERY_THRESHOLD = 0.7
DEFAULT_SEARCH_THRESHOLD = 0.5
DEFAULT_SIMILARITY_THRESHOLD = 0.5


def get_soph_api_key():
    """获取sophnet API密钥

    优先级：
    1. 环境变量 SOPH_API_KEY
    2. Moltbot配置文件中的 sophnet.apiKey
    """
    # 首先检查环境变量
    api_key = os.environ.get("SOPH_API_KEY")
    if api_key:
        return api_key
    else:
        raise RuntimeError(
            "未找到sophnet API密钥。请通过以下方式之一配置： "
            " 1. 设置环境变量 SOPH_API_KEY "
            " 2. 在 Moltbot 配置文件中配置 models.providers.sophnet.apiKey"
        )

# 全局API密钥
try:
    soph_api_key = get_soph_api_key()
except RuntimeError as e:
    print(f"错误: {e}", file=sys.stderr)
    sys.exit(1)


def detect_faces(image_path):
    """调用API检测人脸"""
    if not os.path.exists(image_path):
        raise FileNotFoundError(f"图片文件不存在: {image_path}")

    ost_img = cv2.imread(image_path)
    if ost_img is None:
        raise ValueError(f"无法读取图片文件: {image_path}")

    # 确定图片的 MIME 类型
    input_file = Path(image_path)
    ext = input_file.suffix.lower()
    mime_types = {
        '.jpg': 'image/jpeg',
        '.jpeg': 'image/jpeg',
        '.png': 'image/png',
        '.webp': 'image/webp',
        '.bmp': 'image/bmp',
        '.gif': 'image/gif'
    }
    mime_type = mime_types.get(ext, 'image/jpeg')

    with open(image_path, 'rb') as f:
        files = {'file': (os.path.basename(image_path), f, mime_type)}
        headers = {"Authorization": f"Bearer {soph_api_key}"}
        response = requests.post(FACE_API_URL, files=files, headers=headers, timeout=30)

    if response.status_code != 200:
        raise RuntimeError(f"API请求失败: {response.status_code} - {response.text[:200]}")

    return ost_img, response.json().get('result', {})


def get_largest_face(faces):
    """从检测到的人脸中找出尺寸最大的人脸"""
    if not faces:
        return None

    largest_face = None
    largest_area = 0
    for face in faces:
        box = face.get('box', [])
        if len(box) >= 4:
            x1, y1, x2, y2 = box[0], box[1], box[2], box[3]
            area = (x2 - x1) * (y2 - y1)
            if area > largest_area:
                largest_area = area
                largest_face = face
    return largest_face


def draw_face_box_opencv(ost_img, image_path, face):
    """在图片上绘制人脸边界框"""
    input_file = Path(image_path)
    output_file = input_file.with_name(f"{input_file.stem}_face{input_file.suffix}")
    output_file = output_file.with_suffix('.jpg')
    output_path = str(output_file)

    if face:
        box = face.get('box', [])
        if len(box) >= 4:
            x1, y1, x2, y2 = int(box[0]), int(box[1]), int(box[2]), int(box[3])
            cv2.rectangle(ost_img, (x1, y1), (x2, y2), (0, 255, 0), 3)
    
    cv2.imwrite(output_path, ost_img)
    return output_path

def save_embedding(face, json_path):
    """保存人脸embedding到json文件"""
    if face is None:
        return None

    data = {
        "embedding": face.get('embedding', []),
        "box": face.get('box', []),
        "det_score": face.get('det_score', 0)
    }
    with open(json_path, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=2)
    return json_path


def save_embeddings(image_path, faces, json_path):
    """保存多个人脸embedding到json文件"""
    if faces is None:
        return None

    data = {
        "image_path": str(image_path),
        "embeddings": [face.get('embedding', []) for face in faces],
        "boxes": [face.get('box', []) for face in faces],
        "det_scores": [face.get('det_score', 0) for face in faces]
    }
    with open(json_path, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=2)
    return json_path


def get_baseface_embedding(image_path, det_thr=DEFAULT_QUERY_THRESHOLD, output_dir=None):
    """获取查询图片的最大人脸embedding"""
    input_file = Path(image_path)
    input_file_name = str(input_file)

    try:
        ost_image, result = detect_faces(input_file_name)
        faces_count = result.get("faces_count", 0)
        faces = result.get("output", [])
        faces = [face for face in faces if face.get('det_score', 0) >= det_thr]
        faces_count = len(faces)

        if faces_count > 0:
            largest_face = get_largest_face(faces)
            if largest_face:
                face_image_path = draw_face_box_opencv(ost_image, input_file_name, largest_face)
                
                # 保存embedding
                if output_dir:
                    output_dir = Path(output_dir)
                    output_dir.mkdir(parents=True, exist_ok=True)
                    json_path = output_dir / f"{input_file.stem}_embedding.json"
                else:
                    json_path = input_file.with_suffix('.json')
                
                save_embedding(largest_face, str(json_path))
                return str(json_path), str(face_image_path)
        return None, None
    except Exception as e:
        print(f"错误: {e}", file=sys.stderr)
        return None, None


def get_searchface_embeddings(image_paths, det_thr=DEFAULT_SEARCH_THRESHOLD, output_dir=None):
    """获取搜索图片列表的所有人脸embedding"""
    json_list = []

    if output_dir:
        output_dir = Path(output_dir)
        output_dir.mkdir(parents=True, exist_ok=True)

    for image_path in image_paths:
        try:
            ost_image, result = detect_faces(image_path)
            faces_count = result.get("faces_count", 0)
            faces = result.get("output", [])
            faces = [face for face in faces if face.get('det_score', 0) >= det_thr]
            faces_count = len(faces)

            if faces_count > 0:
                input_file = Path(image_path)
                if output_dir:
                    json_path = output_dir / f"{input_file.stem}_embeddings.json"
                else:
                    json_path = input_file.with_suffix('.json')

                save_embeddings(image_path, faces, json_path)
                json_list.append(str(json_path))
        except Exception as e:
            print(f"处理 {image_path} 时出错: {e}", file=sys.stderr)

    return json_list


def get_baseface_embedding_from_json(json_path):
    """从json文件加载查询人脸embedding"""
    embeddings = []
    with open(json_path, 'r', encoding='utf-8') as f:
        data = json.load(f)
        embeddings = data.get("embedding", [])
    return np.array(embeddings).astype(np.float32)


def get_searchface_embeddings_from_json(json_paths):
    """从json文件列表加载搜索人脸embeddings"""
    all_embeddings = {}
    for json_path in json_paths:
        with open(json_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
            embeddings = data.get("embeddings", [])
            image_name = data.get("image_path", "")
            all_embeddings[image_name] = np.array(embeddings).astype(np.float32)
    return all_embeddings


def cosine_similarity(vec1, vec2):
    """计算余弦相似度"""
    dot_product = np.dot(vec1, vec2)
    norm1 = np.linalg.norm(vec1)
    norm2 = np.linalg.norm(vec2)
    if norm1 == 0 or norm2 == 0:
        return 0
    return dot_product / (norm1 * norm2)


def search_similar_faces(base_json_path, search_json_paths, threshold=DEFAULT_SIMILARITY_THRESHOLD):
    """搜索相似人脸"""
    if not base_json_path or not search_json_paths:
        return []

    face_embedding = get_baseface_embedding_from_json(base_json_path)
    search_embeddings = get_searchface_embeddings_from_json(search_json_paths)

    results = []
    for image_name, embeddings in search_embeddings.items():
        for idx, embedding in enumerate(embeddings):
            similarity = cosine_similarity(face_embedding, embedding)
            if similarity >= threshold:
                results.append({
                    "image_path": image_name,
                    "face_index": idx,
                    "similarity": float(similarity)
                })

    # 按相似度降序排序
    results.sort(key=lambda x: x["similarity"], reverse=True)
    return results


def main():
    parser = argparse.ArgumentParser(description='人脸检索工具')
    subparsers = parser.add_subparsers(dest='command', help='子命令')

    # 第一步：处理查询图片
    parser_base = subparsers.add_parser('base', help='处理查询图片，提取最大人脸embedding')
    parser_base.add_argument('image_path', help='查询图片路径')
    parser_base.add_argument('--det-thr', type=float, default=DEFAULT_QUERY_THRESHOLD,
                            help=f'检测阈值 (默认: {DEFAULT_QUERY_THRESHOLD})')
    parser_base.add_argument('--output-dir', help='输出目录')
    
    # 第二步：处理搜索图片列表并执行检索
    parser_search = subparsers.add_parser('search', help='处理搜索图片列表并执行匹配（一步式）或仅生成embedding（旧模式）')
    parser_search.add_argument('paths', nargs='+', help='查询特征.json（一步式）或图片路径列表（旧模式）')
    parser_search.add_argument('--det-thr', type=float, default=DEFAULT_SEARCH_THRESHOLD,
                              help=f'检测阈值 (默认: {DEFAULT_SEARCH_THRESHOLD})')
    parser_search.add_argument('--threshold', type=float, default=DEFAULT_SIMILARITY_THRESHOLD,
                              help=f'相似度阈值 (默认: {DEFAULT_SIMILARITY_THRESHOLD})')
    parser_search.add_argument('--output-dir', help='输出目录')
    
    args = parser.parse_args()

    if args.command == 'base':
        json_path, face_image_path = get_baseface_embedding(args.image_path, args.det_thr, args.output_dir)
        if json_path:
            print(f"查询人脸embedding已保存: {json_path}")
            print(f"画框图片: MEDIA:{face_image_path}")
            # 输出专用标记，方便自动化脚本解析
            print(f"FACE_PREVIEW:{face_image_path}")
        else:
            print("未检测到人脸", file=sys.stderr)
            sys.exit(1)

    elif args.command == 'search':
        # 检测工作模式：一步式（含查询特征.json）或旧模式（仅图片列表）
        first_path = args.paths[0]

        if first_path.endswith('.json'):
            # 一步式模式：第一个参数是查询特征.json
            base_json_path = first_path
            image_paths = args.paths[1:]

            if not image_paths:
                print("错误: 一步式模式需要提供查询特征.json和至少一张搜索图片", file=sys.stderr)
                sys.exit(1)

            # 生成搜索图片的embeddings
            json_paths = get_searchface_embeddings(image_paths, args.det_thr, args.output_dir)

            if not json_paths:
                print("未检测到任何人脸", file=sys.stderr)
                sys.exit(1)

            # 执行匹配
            results = search_similar_faces(base_json_path, json_paths, args.threshold)
            if results:
                print(f"找到 {len(results)} 个相似人脸:")
                for r in results:
                    similarity_percent = r['similarity'] * 100
                    print(f"  {r['image_path']} (人脸#{r['face_index']}, 相似度: {similarity_percent:.2f}%)")
                    print(f"  MEDIA:{r['image_path']}")
                
                # 输出所有匹配图片的路径列表（逗号分隔），方便自动化脚本解析
                matched_images = [r['image_path'] for r in results]
                print(f"MATCHED_IMAGES:{','.join(matched_images)}")
            else:
                print("未找到相似人脸")
    else:
        parser.print_help()


if __name__ == "__main__":
    main()