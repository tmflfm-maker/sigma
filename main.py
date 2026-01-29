import yfinance as yf
import pandas as pd
from datetime import datetime

def get_data():
    # 1. UGL을 리스트에 추가했습니다.
    tickers = ["SOXX", "URA", "GLD", "UGL"]
    results = []

    for symbol in tickers:
        try:
            t = yf.Ticker(symbol)
            cp = t.history(period="1d")['Close'].iloc[-1]
            exp_dates = t.options
            if not exp_dates: continue
            
            opt = t.option_chain(exp_dates[0])
            # ATM 옵션 찾기
            atm_c = opt.calls.iloc[(opt.calls['strike'] - cp).abs().argsort()[:1]]
            atm_p = opt.puts.iloc[(opt.puts['strike'] - cp).abs().argsort()[:1]]
            
            # 프리미엄 합산 (1시그마 폭)
            move = atm_c['lastPrice'].values[0] + atm_p['lastPrice'].values[0]
            
            s2_low = cp - (move * 2)
            # 2. 하단선까지의 남은 거리(%) 계산
            # (현재가 - 하단선) / 현재가 * 100
            dist_to_low = ((cp - s2_low) / cp) * 100
            
            results.append({
                "symbol": symbol,
                "price": round(cp, 2),
                "s1_low": round(cp - move, 2),
                "s1_high": round(cp + move, 2),
                "s2_low": round(s2_low, 2),
                "s2_high": round(cp + move * 2, 2),
                "dist_pct": round(dist_to_low, 2)
            })
        except:
            continue
    return results

def generate_html(data):
    now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    
    cards = ""
    for d in data:
        # 하단선과의 거리에 따른 색상 변화 (가까울수록 붉은색)
        dist_color = "text-yellow-400" if d['dist_pct'] > 2 else "text-red-500 font-bold"
        
        cards += f"""
        <div class="bg-gray-800 p-6 rounded-xl border border-gray-700 shadow-lg hover:border-blue-500 transition-all">
            <div class="flex justify-between items-start mb-4">
                <h2 class="text-3xl font-black text-blue-400">{d['symbol']}</h2>
                <div class="text-right">
                    <p class="text-xs text-gray-500 uppercase">Distance to Bottom</p>
                    <p class="{dist_color} text-lg">{d['dist_pct']}% 남음</p>
                </div>
            </div>
            
            <p class="text-gray-400 mb-6">현재가: <span class="text-white text-2xl font-mono">${d['price']}</span></p>
            
            <div class="space-y-4">
                <div class="bg-gray-900 p-3 rounded-lg border-l-4 border-green-500">
                    <p class="text-xs text-gray-400 mb-1">1 Sigma (68% Range)</p>
                    <p class="text-green-400 font-mono text-sm">${d['s1_low']} ~ ${d['s1_high']}</p>
                </div>
                <div class="bg-gray-900 p-3 rounded-lg border-l-4 border-yellow-500">
                    <p class="text-xs text-gray-400 mb-1">2 Sigma (95% Hunter Zone)</p>
                    <p class="text-yellow-400 font-bold font-mono text-lg">${d['s2_low']} ~ ${d['s2_high']}</p>
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
        <title>Sigma Hunter Dashboard</title>
    </head>
    <body class="bg-gray-900 text-white min-h-screen p-4 md:p-8">
        <div class="max-w-6xl mx-auto">
            <header class="mb-10 flex justify-between items-end">
                <div>
                    <h1 class="text-4xl font-black mb-2">🎯 Sigma Hunter</h1>
                    <p class="text-gray-500">실시간 변동성 감시</p>
                </div>
                <div class="text-right text-sm text-gray-600">
                    Last Update: {now}
                </div>
            </header>
            
            <div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
                {cards}
            </div>
            
            <div class="mt-12 p-6 bg-gray-800 rounded-xl border border-gray-700">
                <h3 class="text-lg font-bold mb-2 text-blue-300">💡 사용 팁</h3>
                <ul class="text-gray-400 text-sm list-disc list-inside space-y-1">
                    <li><b>Distance to Bottom:</b> 현재가에서 2시그마 하단선까지의 거리를 나타냅니다.</li>
                    <li>값이 <b>0%에 가까워질수록</b> 통계적 저점(Hunter Zone)에 도달한 것입니다.</li>
                </ul>
            </div>
        </div>
    </body>
    </html>
    """
    with open("index.html", "w", encoding="utf-8") as f:
        f.write(html_template)

if __name__ == "__main__":
    data = get_data()
    generate_html(data)
