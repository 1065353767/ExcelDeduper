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

# ==========================================
# 欧洲专版：基础路径与国家名录字典
# ==========================================
BASE_EN_URL = "https://www.cargoyellowpages.com/en/"
HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
}

# 专属状态文件，与美国的区分开，防止串档
STATE_FILE = "europe_scraper_state.json"

# 从你提供的目录中提取的欧洲国家映射表 (Key: 展示名, Value: URL路径名)
EUROPE_COUNTRIES = {
    "Albania": "albania", "Andorra": "andorra", "Austria": "austria",
    "Belarus": "belarus", "Belgium": "belgium", "Bosnia Herzegovina": "bosnia-herzegovina",
    "Bulgaria": "bulgaria", "Croatia": "croatia", "Cyprus": "cyprus",
    "Czech Republic": "czech-republic", "Denmark": "denmark", "Estonia": "estonia",
    "Finland": "finland", "France": "france", "Germany": "germany",
    "Greece": "greece", "Hungary": "hungary", "Iceland": "iceland",
    "Ireland": "ireland", "Italy": "italy", "Latvia": "latvia",
    "Liechtenstein": "liechtenstein", "Lithuania": "lithuania", "Luxembourg": "luxembourg",
    "Macedonia": "macedonia", "Malta": "malta", "Moldova": "moldova",
    "Monaco": "monaco", "Montenegro": "montenegro", "Netherlands": "netherlands",
    "Norway": "norway", "Poland": "poland", "Portugal": "portugal",
    "Romania": "romania", "Russia": "russia", "San Marino": "san-marino", "Serbia": "serbia",
    "Slovakia": "slovakia", "Slovenia": "slovenia", "Spain": "spain",
    "Sweden": "sweden", "Switzerland": "switzerland", "Ukraine": "ukraine",
    "United Kingdom": "united-kingdom"
}


def init_or_load_state():
    """初始化或加载欧洲版断点续传状态"""
    if os.path.exists(STATE_FILE):
        try:
            with open(STATE_FILE, 'r', encoding='utf-8') as f:
                return json.load(f)
        except Exception as e:
            print(f"    [!] 状态文件读取失败: {e}")

    timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
    excel_name = f"CargoYellowPages_Europe_Final_{timestamp}.xlsx"
    return {
        "target_excel_name": excel_name,
        "completed_tasks": []  # 格式将变为 "国家_城市"
    }


def save_state(state_dict):
    """持久化保存"""
    with open(STATE_FILE, 'w', encoding='utf-8') as f:
        json.dump(state_dict, f, ensure_ascii=False, indent=4)


def fetch_html(url, max_retries=3):
    """底层网络请求"""
    for attempt in range(max_retries):
        try:
            res = requests.get(url, headers=HEADERS, timeout=15)
            res.raise_for_status()
            res.encoding = 'utf-8'
            return res.text
        except Exception:
            time.sleep(2)
    return ""


def extract_companies_from_html(html_str, country_name, city_name):
    """智能解析引擎（新增 Country 字段）"""
    results = []
    soup = BeautifulSoup(html_str, 'html.parser')
    company_blocks = soup.find_all('div', class_=re.compile(r'^(bc-gold|bc-premium|bubbleInfo)$'))

    for block in company_blocks:
        block_text = block.get_text()
        if "YOUR COMPANY NAME" in block_text or "XXX-XXX XXXX" in block_text:
            continue

        # 新增 Country 维度
        data = {
            "Company Name": "", "Country": country_name, "State": "", "City": city_name,
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


def scrape_city_pages(city_url, country_name, city_name):
    """处理该城市的所有翻页"""
    current_url = city_url
    city_leads = []
    page_count = 1

    while current_url:
        print(f"      -> 正在读取 [{city_name}] 第 {page_count} 页...")
        html_str = fetch_html(current_url)
        if not html_str: break

        companies = extract_companies_from_html(html_str, country_name, city_name)
        city_leads.extend(companies)

        soup = BeautifulSoup(html_str, 'html.parser')
        next_btn = soup.find('a', string=re.compile(r'Next', re.IGNORECASE))
        if next_btn and next_btn.has_attr('href'):
            current_url = urljoin(current_url, next_btn['href'])
            page_count += 1
            time.sleep(random.uniform(1.0, 2.0))
        else:
            break

    return city_leads


def get_cities_for_country(country_url):
    """获取指定国家下的所有城市入口"""
    html_str = fetch_html(country_url)
    if not html_str: return []

    soup = BeautifulSoup(html_str, 'html.parser')
    unique_cities = {}

    for div in soup.find_all('div', class_='ct_city'):
        a_tag = div.find('a', href=True)
        if a_tag:
            full_url = urljoin(country_url, a_tag['href'])
            name = a_tag.get_text(strip=True)
            unique_cities[full_url] = name

    return [{"url": url, "city_name": name} for url, name in unique_cities.items()]


def save_to_excel_safely(new_leads, target_excel):
    """智能防占用保存"""
    if not new_leads: return
    df_new = pd.DataFrame(new_leads)
    # Excel 新增列 Country
    cols = ['Company Name', 'Country', 'State', 'City', 'Email', 'Phone', 'Fax', 'Address', 'Website']
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
            print(f"\n      [!] 写入被拒绝！请关闭 Excel 文件 {target_excel}，5秒后自动重试...")
            time.sleep(5)
        except Exception as e:
            print(f"\n      [!] 写入 Excel 发生错误: {e}")
            break


def main():
    state_dict = init_or_load_state()
    target_excel = state_dict["target_excel_name"]
    completed_tasks = set(state_dict["completed_tasks"])

    print(">>> [欧洲计划] 启动！开始扫描预设的欧洲国家名录...")

    total_countries = len(EUROPE_COUNTRIES)
    country_index = 0

    for country_name, slug in EUROPE_COUNTRIES.items():
        country_index += 1
        country_url = f"{BASE_EN_URL}{slug}/"

        print(f"\n==================================================")
        print(f">>> 跨国扫描 [{country_index}/{total_countries}]: {country_name}")
        print(f"==================================================")

        cities = get_cities_for_country(country_url)
        if not cities:
            print(f"  [-] {country_name} 暂无城市数据或抓取失败。")
            continue

        print(f"  [+] 成功锁定 {country_name} 境内的 {len(cities)} 个城市。")

        for city_info in cities:
            c_name = city_info["city_name"]
            c_url = city_info["url"]
            task_id = f"{country_name}_{c_name}"  # 唯一任务ID，防止跨国同名城市冲突

            if task_id in completed_tasks:
                continue  # 已完成，直接断点跳过

            print(f"\n  [启动城市] {country_name} -> {c_name}")
            leads = scrape_city_pages(c_url, country_name, c_name)

            if leads:
                save_to_excel_safely(leads, target_excel)
                print(f"      [OK] 入库 {len(leads)} 条数据。")
            else:
                print(f"      [-] 为空，跳过。")

            # 存入断点配置
            state_dict["completed_tasks"].append(task_id)
            save_state(state_dict)

            time.sleep(random.uniform(2.0, 4.0))

    print(f"\n=============================================")
    print(f">>> 欧洲板块数据收割彻底完成！文件：{target_excel}")
    if os.path.exists(STATE_FILE):
        os.remove(STATE_FILE)
        print(f">>> 状态记录已自动置空，完美收官。")
    print(f"=============================================")


if __name__ == "__main__":
    main()