import json


def dict2json(data_dict, file_path):
    """
    入参：需要保存的字典 (dict)，以及目标保存路径
    动作：将字典转换为 JSON 并覆盖保存到指定路径
    注意：ensure_ascii=False 保证正常中文，indent=4 保证格式化排版
    """
    with open(file_path, 'w', encoding='utf-8') as f:
        json.dump(data_dict, f, ensure_ascii=False, indent=4)


def json2dict(file_path):
    """
    入参：JSON文件的绝对路径
    出参：解析后的 Python 字典 (dict)
    注意：不捕获异常，若文件不存在或格式错误，直接向上抛出
    """
    with open(file_path, 'r', encoding='utf-8') as f:
        return json.load(f)
