import requests
import re
import time
import random
import pandas as pd
from urllib.parse import urljoin
from bs4 import BeautifulSoup
import datetime
import os
import json

USA_ROOT_URL = "https://www.cargoyellowpages.com/en/united-states/"
HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
}

STATE_FILE = "scraper_state.json"


def init_or_load_state():
    """初始化或加载断点续传状态"""
    if os.path.exists(STATE_FILE):
        try:
            with open(STATE_FILE, 'r', encoding='utf-8') as f:
                state_dict = json.load(f)
                return state_dict
        except Exception as e:
            print(f"    [!] 状态文件读取失败，将重新初始化: {e}")

    timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
    excel_name = f"CargoYellowPages_Leads_Final_{timestamp}.xlsx"
    return {
        "target_excel_name": excel_name,
        "completed_cities": []
    }


def save_state(state_dict):
    """持久化保存当前进度状态"""
    with open(STATE_FILE, 'w', encoding='utf-8') as f:
        json.dump(state_dict, f, ensure_ascii=False, indent=4)


def fetch_html(url, max_retries=3):
    """底层网络请求：强制 UTF-8 解码"""
    for attempt in range(max_retries):
        try:
            res = requests.get(url, headers=HEADERS, timeout=15)
            res.raise_for_status()
            res.encoding = 'utf-8'
            return res.text
        except Exception:
            time.sleep(2)
    return ""


def extract_companies_from_html(html_str, city_name):
    """智能解析引擎"""
    results = []
    soup = BeautifulSoup(html_str, 'html.parser')
    company_blocks = soup.find_all('div', class_=re.compile(r'^(bc-gold|bc-premium|bubbleInfo)$'))

    for block in company_blocks:
        block_text = block.get_text()
        if "YOUR COMPANY NAME" in block_text or "XXX-XXX XXXX" in block_text:
            continue

        data = {
            "Company Name": "", "State": "", "City": city_name,
            "Address": "", "Phone": "", "Fax": "",
            "Email": "", "Website": ""
        }

        name_tag = block.find('h2')
        if name_tag:
            updated_span = name_tag.find('span', class_='updated')
            if updated_span:
                updated_span.decompose()
            data['Company Name'] = name_tag.get_text(strip=True)
        else:
            continue

        addr_tag = block.find(attrs={"itemprop": "street-address"})
        if not addr_tag:
            addr_tag = block.find('div', class_='bcp-dir')
        if addr_tag:
            for img in addr_tag.find_all('img'):
                img.decompose()
            data['Address'] = addr_tag.get_text(separator=" ", strip=True)

        email_a = block.find('a', class_='mailinline')
        if email_a:
            parts = [c for c in email_a.contents if isinstance(c, str) and c.strip()]
            if len(parts) >= 2:
                data['Email'] = f"{parts[0].strip()}@{parts[1].strip()}"

        phone_img = block.find('img', alt=re.compile(r'phone', re.I))
        if phone_img and phone_img.parent:
            data['Phone'] = phone_img.parent.get_text(strip=True)

        fax_img = block.find('img', alt=re.compile(r'fax', re.I))
        if fax_img and fax_img.parent:
            data['Fax'] = fax_img.parent.get_text(strip=True)

        web_img = block.find('img', alt=re.compile(r'Visit:', re.I))
        if web_img and web_img.parent:
            raw_web = web_img.parent.get_text(strip=True)
            if raw_web.startswith('s://'):
                raw_web = raw_web[4:]
            data['Website'] = raw_web

        results.append(data)

    return results


def scrape_city_pages(city_url, city_name):
    """处理该城市的所有翻页"""
    current_url = city_url
    city_leads = []
    page_count = 1

    while current_url:
        print(f"    -> 正在读取 [{city_name}] 第 {page_count} 页...")
        html_str = fetch_html(current_url)
        if not html_str: break

        companies = extract_companies_from_html(html_str, city_name)
        city_leads.extend(companies)
        print(f"       + 本页提取到 {len(companies)} 家公司")

        soup = BeautifulSoup(html_str, 'html.parser')
        next_btn = soup.find('a', string=re.compile(r'Next', re.IGNORECASE))
        if next_btn and next_btn.has_attr('href'):
            current_url = urljoin(current_url, next_btn['href'])
            page_count += 1
            time.sleep(random.uniform(1.0, 2.0))
        else:
            break

    return city_leads


def get_all_usa_cities():
    """获取所有美国城市入口"""
    print(">>> 初始化：正在扫描全美城市地图...")
    html_str = fetch_html(USA_ROOT_URL)
    if not html_str: return []

    soup = BeautifulSoup(html_str, 'html.parser')
    unique_cities = {}

    for div in soup.find_all('div', class_='ct_city'):
        a_tag = div.find('a', href=True)
        if a_tag:
            full_url = urljoin(USA_ROOT_URL, a_tag['href'])
            name = a_tag.get_text(strip=True)
            unique_cities[full_url] = name

    return [{"url": url, "city_name": name} for url, name in unique_cities.items()]


def save_to_excel_safely(new_leads, target_excel):
    """智能防占用保存：保证持续写入到唯一文件"""
    if not new_leads: return
    df_new = pd.DataFrame(new_leads)
    cols = ['Company Name', 'State', 'City', 'Email', 'Phone', 'Fax', 'Address', 'Website']
    df_new = df_new[cols]

    while True:
        try:
            if os.path.exists(target_excel):
                df_exist = pd.read_excel(target_excel)
                df_combined = pd.concat([df_exist, df_new], ignore_index=True)
                df_combined.to_excel(target_excel, index=False)
            else:
                df_new.to_excel(target_excel, index=False)
            break

        except PermissionError:
            print(f"\n    [!] 写入被拒绝！你可能正在打开 {target_excel}")
            print("    [!] 程序不会崩溃，已暂停。请关闭该 Excel 文件，5秒后自动重试写入...")
            time.sleep(5)
        except Exception as e:
            print(f"\n    [!] 写入 Excel 发生未知错误: {e}")
            break


def main():
    state_dict = init_or_load_state()
    target_excel = state_dict["target_excel_name"]
    completed_cities = set(state_dict["completed_cities"])

    all_cities = get_all_usa_cities()
    if not all_cities:
        print("[!] 无法获取城市列表，请检查网络。")
        return

    total_cities = len(all_cities)
    pending_cities = [c for c in all_cities if c["city_name"] not in completed_cities]

    if len(pending_cities) == 0:
        print(f"\n>>> 所有 {total_cities} 个城市已全部抓取完毕！任务结束。")
        if os.path.exists(STATE_FILE):
            os.remove(STATE_FILE)
            print(f">>> 记录文件 {STATE_FILE} 已物理销毁，下次启动将生成全新时间戳任务。")
        return

    if len(pending_cities) < total_cities:
        print(f">>> [断点续传] 读取到配置进度，目标文件锁定为：{target_excel}")
        print(f">>> 已跳过 {total_cities - len(pending_cities)} 个城市，剩余 {len(pending_cities)} 个即将继续...")
        time.sleep(2)
    else:
        print(f">>> [全新任务] 成功锁定 {total_cities} 个城市，目标生成文件为：{target_excel}")

    for i, city_info in enumerate(pending_cities):
        c_name = city_info["city_name"]
        print(
            f"\n[任务进度 {i + 1}/{len(pending_cities)} - 全局 {len(completed_cities) + i + 1}/{total_cities}] 启动城市: {c_name}")

        leads = scrape_city_pages(city_info["url"], c_name)
        if leads:
            save_to_excel_safely(leads, target_excel)
            print(f"    [OK] {c_name} 完工，{len(leads)} 条数据已追加至 {target_excel}。")
        else:
            print(f"    [-] {c_name} 为空，已跳过。")

        state_dict["completed_cities"].append(c_name)
        save_state(state_dict)

        time.sleep(random.uniform(2.0, 4.0))

    print(f"\n=============================================")
    print(f">>> 全美数据收割彻底完成！文件：{target_excel}")
    if os.path.exists(STATE_FILE):
        os.remove(STATE_FILE)
        print(f">>> 状态记录已自动置空，完美收官。")
    print(f"=============================================")


if __name__ == "__main__":
    main()