# Stock Options Calculator (ISO vs NSO) — Reddit Distribution Posts

*Strategy: 90% value / 10% product. Link to the free web tool ONLY in comments after engagement. Never lead with the product.*

---

## Post 1: r/cscareerquestions

**Title:** ISO vs NSO: I ran the tax numbers at different exercise prices — the difference was $40K

**Body:**

I have stock options at a startup and kept hearing "ISOs are better for taxes" without understanding why. So I modeled both paths at different exit prices. The gap is huge.

**Setup:** 10,000 options, $2 strike, $20 FMV. So $18 spread per share = $180K "profit" at exercise.

**ISO path:** Exercise triggers AMT (Alternative Minimum Tax), not ordinary income. If you hold 1+ year after exercise and 2+ years after grant, the gain at *sale* is taxed as long-term capital gains. So you pay AMT at exercise (which can create a credit for later) and LTCG at sale. Complicated but often better for high upside.

**NSO path:** Exercise triggers ordinary income tax on the spread. No AMT. At sale, you pay capital gains on the *additional* gain (sale price − FMV at exercise). Simpler, but you're taxed twice on the spread — once as income, once implicitly in the cost basis.

**At $20 exit (same as FMV):** ISO wins — you've already exercised, no additional tax at sale. NSO: you paid ordinary income on $180K at exercise. Roughly $50K+ in tax depending on bracket.

**At $50 exit:** Both have gains. ISO: LTCG on $30/share × 10K = $300K. NSO: you already paid income tax on $180K at exercise; now cap gains on $300K. The ISO path can net $30–40K more after tax.

**At $10 exit (underwater):** You're screwed either way if you already exercised. This is why "exercise when you have liquidity" matters. Don't exercise early if the company might go to zero.

I built a free calculator that compares ISO vs NSO at different exit prices. You plug in your numbers and see net proceeds for each path. No sign-up. Happy to share if useful.

---

## Post 2: r/stocks

**Title:** Startup stock options: when does exercising early (and holding for LTCG) actually make sense?

**Body:**

I have ISO options at a startup. The classic advice: exercise early, hold 1+ year, pay LTCG instead of ordinary income. But that only works if (a) you have cash to exercise, (b) the company doesn't go to zero, and (c) the spread isn't so big that AMT kills you.

I ran the numbers for different scenarios:

**Scenario 1: Small spread, early exercise**
- 10K options, $2 strike, $3 FMV. Spread = $10K. AMT impact is minimal. Exercise now, hold for LTCG. If stock 10x to $30, you pay LTCG on $270K instead of ordinary income. Saves ~$50K in tax.

**Scenario 2: Large spread, late exercise**
- 10K options, $2 strike, $20 FMV. Spread = $180K. Exercise triggers big AMT. If you're in a high bracket, AMT can be $40K+. You need to sell some shares to cover, or have cash. The "exercise and hold" strategy is harder.

**Scenario 3: NSO instead of ISO**
- NSO: exercise = ordinary income on spread. No AMT. Simpler, but you pay more tax on the spread. ISO can win if you hold for LTCG, but NSO is often better if you're going to sell soon (e.g., at IPO) because you avoid AMT complexity.

**The 83(b) election:** If you exercise *before* vesting (early exercise), you file 83(b) within 30 days. That locks in the spread at exercise for tax purposes. If the stock goes up, all future gain is cap gains. High risk, high reward.

**My takeaway:** Run your numbers. The "right" answer depends on strike, FMV, expected exit price, and your tax bracket. I built a free web calculator that compares ISO vs NSO at different exit prices. No sign-up. Link in comments if anyone wants it.

---

## Post 3: r/financialindependence

**Title:** Stock options and early retirement: how I'm modeling the tax impact of different exercise strategies

**Body:**

I'm targeting FIRE in 8–10 years. I have ISO options at a startup that could be a meaningful chunk of my portfolio — or nothing. I built a model to understand the tax implications of different exercise/sale strategies.

**Key variables:**
- **Exercise timing:** Early (pay cash now, hold for LTCG) vs at exit (cashless exercise, sell immediately). Early only works if you have liquidity and conviction.
- **Holding period:** 1+ year after exercise + 2+ year after grant = qualifying disposition = LTCG. Otherwise = disqualifying = ordinary income on the spread.
- **AMT:** ISO exercise can trigger AMT. You get a credit later, but it ties up cash now. In a year with big AMT, you might pay 26–28% on the "preference item."
- **Exit price:** The higher the exit, the more LTCG matters. At 2x, the difference between ISO and NSO might be $20K. At 10x, it could be $200K.

**What I modeled:**
- ISO vs NSO at exit prices from $10 to $100
- Tax at exercise (AMT for ISO, ordinary for NSO)
- Tax at sale (LTCG vs STCG)
- Net proceeds after tax

**Result:** ISO wins in most "hold for LTCG" scenarios. NSO wins if you're selling soon (no AMT, simpler). The break-even exit price depends on your strike, FMV, and bracket.

**For FIRE planning:** If options are a big part of your plan, model the after-tax proceeds. A $500K "paper" gain might be $350K after tax. That changes your FI number.

I built a free calculator that does this — ISO vs NSO, different exit prices, net proceeds. No sign-up. There's also an Excel version with exercise scenario tables. Happy to share if useful.

---

## Comment Template (for when people ask for the tool)

> Here's the free calculator: [APP_URL_PLACEHOLDER]
>
> No sign-up, no email — just runs in your browser. You can compare ISO vs NSO at different exit prices and see net proceeds.
>
> If you want a downloadable Excel version with exercise scenarios and full editability, I also made one: clearmetric.gumroad.com
>
> Happy to answer questions about the tax math or assumptions.

---

## Posting Schedule (Master — All Products)

| Day | Product | Subreddit |
|-----|---------|-----------|
| 1 | Rent vs Buy | r/RealEstate |
| 2 | Rent vs Buy | r/FirstTimeHomeBuyer |
| 3 | Rent vs Buy | r/personalfinance |
| 4 | Freelance Rate | r/freelance |
| 5 | Freelance Rate | r/Upwork |
| 6 | Freelance Rate | r/consulting |
| 7 | Startup Runway | r/startups |
| 8 | Startup Runway | r/SaaS |
| 9 | Startup Runway | r/Entrepreneur |
| 10 | Side Hustle Tax | r/sidehustle |
| 11 | Side Hustle Tax | r/personalfinance |
| 12 | Side Hustle Tax | r/tax |
| 13 | LLC vs S-Corp | r/smallbusiness |
| 14 | LLC vs S-Corp | r/tax |
| 15 | LLC vs S-Corp | r/Entrepreneur |
| 16 | Stock Options | r/cscareerquestions |
| 17 | Stock Options | r/stocks |
| 18 | Stock Options | r/financialindependence |
| 19 | Car Affordability | r/personalfinance |
| 20 | Car Affordability | r/askcarsales |
| 21 | Car Affordability | r/whatcarshouldIbuy |
| 22 | Wedding Budget | r/weddingplanning |
| 23 | Wedding Budget | r/Weddingsunder10k |
| 24 | Wedding Budget | r/personalfinance |
| 25 | Cost of Living | r/remotework |
| 26 | Cost of Living | r/SameGrassButGreener |
| 27 | Cost of Living | r/personalfinance |

**Rules:**
- One post per day. Wait for 2–3 upvotes before posting the comment with links.
- Engage genuinely with every reply.
- Never post two subreddits on the same day.
- If a post gets removed, don't repost — try a different angle next week.
