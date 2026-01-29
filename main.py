import yfinance as yf
import pandas as pd
from datetime import datetime

def get_data():
    tickers = ["SOXX", "URA", "GLD"]
    results = []

    for symbol in tickers:
        try:
            t = yf.Ticker(symbol)
            cp = t.history(period="1d")['Close'].iloc[-1]
            exp_dates = t.options
            if not exp_dates: continue
            
            opt = t.option_chain(exp_dates[0])
            atm_c = opt.calls.iloc[(opt.calls['strike'] - cp).abs().argsort()[:1]]
            atm_p = opt.puts.iloc[(opt.puts['strike'] - cp).abs().argsort()[:1]]
            move = atm_c['lastPrice'].values[0] + atm_p['lastPrice'].values[0]
            
            results.append({
                "symbol": symbol,
                "price": round(cp, 2),
                "s1_low": round(cp - move, 2),
                "s1_high": round(cp + move, 2),
                "s2_low": round(cp - move * 2, 2),
                "s2_high": round(cp + move * 2, 2),
                "move": round(move, 2)
            })
        except:
            continue
    return results

def generate_html(data):
    now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    
    # 카드형 UI 제작 (Tailwind CSS 사용으로 가시성 확보)
    cards = ""
    for d in data:
        cards += f"""
        <div class="bg-gray-800 p-6 rounded-xl border border-gray-700 shadow-lg">
            <h2 class="text-2xl font-bold text-blue-400 mb-2">{d['symbol']}</h2>
            <p class="text-gray-400 mb-4">현재가: <span class="text-white text-xl">${d['price']}</span></p>
            <div class="space-y-3">
                <div class="bg-gray-900 p-3 rounded-lg">
                    <p class="text-xs text-gray-500 uppercase">1 Sigma (68%)</p>
                    <p class="text-green-400 font-mono">${d['s1_low']} ~ ${d['s1_high']}</p>
                </div>
                <div class="bg-gray-900 p-3 rounded-lg border-l-4 border-yellow-500">
                    <p class="text-xs text-gray-500 uppercase">2 Sigma (95%) - Hunter V6 Zone</p>
                    <p class="text-yellow-400 font-bold font-mono">${d['s2_low']} ~ ${d['s2_high']}</p>
                </div>
            </div>
        </div>
        """

    html_template = f"""
    <!DOCTYPE html>
    <html lang="ko">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <script src="https://cdn.tailwindcss.com"></script>
        <title>Expected Move Dashboard</title>
    </head>
    <body class="bg-gray-900 text-white min-h-screen p-8">
        <div class="max-w-4xl mx-auto">
            <header class="mb-10 text-center">
                <h1 class="text-4xl font-extrabold mb-2">📊 Option Expected Move</h1>
                <p class="text-gray-500">최근 업데이트: {now} (KST)</p>
            </header>
            <div class="grid grid-cols-1 md:grid-cols-3 gap-6">
                {cards}
            </div>
            <footer class="mt-12 text-center text-gray-600 text-sm">
                데이터 출처: Yahoo Finance | Hunter V6 전략 참고용
            </footer>
        </div>
    </body>
    </html>
    """
    with open("index.html", "w", encoding="utf-8") as f:
        f.write(html_template)

if __name__ == "__main__":
    data = get_data()
    generate_html(data)
