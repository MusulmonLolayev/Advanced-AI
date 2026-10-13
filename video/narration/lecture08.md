# Lecture 8 — video narration (draft 1, for approval)

**One video for the whole lecture**, in two parts like the slides: Part 0 (Eksponensial oila) = sections 1–6,
Part 1 (Yetarli statistikalar) = sections 7–10. Each section: problem first → concept as the answer → one AI use →
a hands-on pause → the question the next section answers. The running examples are the slides' own: the coffee shop
of Lecture 3 (pastry rate 0.3, cup shares 0.2 / 0.5 / 0.3, four arrivals per ten minutes and its 3,000 simulated
windows), Lecture 5's 66 pastry orders in 200 and its 40 espresso shots, the figure script's three ten-morning
records, and Lecture 6's bus.

**Depth from the start** (the instructor's rule after Lecture 4): each idea is explained from more than one side, and
Lectures 1–7 are recapped where they are used. The angles: every MLE of Lecture 5 as an average (a share is the mean
of 0/1 answers); the logit as the log of the odds, stretched over the whole line, symmetric about zero; the softmax
derived, then read as score differences (0.92 = log 2.5) and as the sigmoid when there are two classes; the
exponential form as "the data speaks to η only through T"; A(η) as the log of the total weight, and dividing by that
total gives the probability back; the slope of A checked without calculus; the Poisson's mean = variance seen in
Lecture 3's simulation (3.96 vs 3.84); why frameworks subtract the largest score (e¹⁰⁰⁰ overflows); the MLE
gradient as "observed minus expected" (66 seen, 60 expected); sufficiency counted: given the total, every one of the
C(200, 66) arrangements is equally likely whatever p is; Lecture 1's multiplication rule (the order of factors does
not matter); the variance from the two sums by Lecture 3's "mean of squares minus square of mean"; the two sums
cannot tell a bell from two spikes; all three conjugate pairs of Lecture 6 as "pretend count + real count";
streaming and federated totals on the figure's own records, and what a total hides (the building-up record goes
from 0.18 to 0.48).

**Rules applied:** berilganlar (data); "we", never "you" (only *Videoni toʻxtating*); Latin letters spoken by their
English names (eks, ti, ey, eych, pi, key, en, e); Greek letters keep theirs (eta, teta, mu, sigma, lambda, alfa);
numbers spelled for the ear, digits on screen. Screen labels are words only.
**Numbers:** every figure comes from `video/statistics/raw/l08_numbers.json` / `l08_figures.txt`
(`capture_l08.py`, unit-tested in `test_l08.py`). Lecture 3's arrivals and Lecture 5's espresso shots are regenerated
from their own seeds.

**Slide discrepancy (slides not edited):** *Worked Example: What a Gaussian Needs* gives Σxᵢ = 1195.2 and
Σxᵢ² = 35777.1. Those are 40 × 29.88 and 40 × (29.88² + 1.27²), rebuilt from the rounded estimates. The 40 shots
themselves (Lecture 5's seed 11) give **Σxᵢ = 1195.09** and **Σxᵢ² = 35770.56**; the narration uses these, and they
still return x̄ = 29.88 and σ̂ = 1.27. The second sum is too far off (6.5) to blame on rounding alone, so the slide
should take the computed values.

**Terms to confirm** (new in this lecture; proposed, for the instructor):
- **eksponensial oila** (exponential family). Kept apart from the approved «eksponensial taqsimot» (Lecture 4): one is
  a family, the other one member of it.
- **tabiiy parametr** (natural parameter) · **yetarli statistika** (sufficient statistic) · **normallovchi funksiya**
  (log-partition function A(η); the screen keeps "log-partition") · **asosiy oʻlchov** (base measure h(x))
- **logit**, **sigmoid** (kept international) · **nisbat** for odds («pishiriqli buyurtmalarning pishiriqsizlarga
  nisbati»); a fixed term could be «imkoniyatlar nisbati»
- **bitta birlik vektor** (one-hot vector: "one 1, the rest 0") · **ball** (score, an unnormalized logit)
- **log-sum-eksp** (log-sum-exp) · **oʻrtachalarni tenglashtirish** (moment matching)
- **Fisher–Neyman faktorizatsiya testi** (factorization theorem) · **koʻpaytuvchi** (factor)
- **log-chiziqli model** (log-linear model) · **energiyaga asoslangan model** (energy-based model)
- **umumlashgan chiziqli model** (GLM) · **bogʻlovchi funksiya** (link function) · **ayniy bogʻlanish** (identity
  link) · **logistik regressiya** · **Puasson regressiyasi** · **eng kichik kvadratlar usuli** (least squares)
- **berilganlar bazasi** (database; «maʼlumotlar bazasi» is the common term, but maʼlumot is reserved for information)
- **federativ oʻqitish** (federated learning) · **variatsion xulosa** (variational inference) · **variatsion avtokoder**
  (VAE) · **Styudent taqsimoti** (Student's t) · **Kulbak–Leybler divergensiyasi** (KL divergence; matches
  Lecture 7's wording)

Format per line: **UZ** (your voice) · *EN* (English track) · ▸ visual.

---

## Lecture opening
▸ title card "8-maʼruza" → the two parts
0. **Assalomu alaykum, aziz doʻstlar. Sakkizinchi maʼruzamizga xush kelibsiz. Bu maʼruza ham ikki qismdan iborat. Nolinchi qismda eksponensial oilani oʻrganamiz, birinchi qismda esa yetarli statistikalar bilan tanishamiz.**
   *Hello, dear friends, and welcome to our eighth lecture. It also has two parts. In part zero we study the exponential family, and in part one we meet sufficient statistics.*

## Part 0 — Eksponensial oila
▸ part card "0-qism · Eksponensial oila"

### 1-boʻlim · Section 1 — Nega taqsimotlar bir-biriga oʻxshaydi · Why so many distributions look alike
1. **Beshinchi maʼruzada ikkita bahoni hisoblagan edik. Bernulli uchun pi bahosi — key ni en ga boʻlganimiz: ikki yuzdan oltmish olti, yaʼni nol butun yuzdan oʻttiz uch. Gauss uchun mu bahosi — tanlanma oʻrtachasi.**
   *In Lecture 5 we computed two estimates. For the Bernoulli, the estimate of p is k divided by n: sixty-six out of two hundred, that is zero point three three. For the Gaussian, the estimate of mu is the sample mean.*
   ▸ p̂ = k/n = 66/200 = 0.33 beside μ̂ = x̄
2. **Ikkala javob ham nimaningdir oʻrtachasi. Pi bahosi ham oʻrtacha: har bir buyurtmaga pishiriq boʻlsa bir, boʻlmasa nol yozsak, shu nol va birlarning oʻrtachasi aynan nol butun yuzdan oʻttiz uch.**
   *Both answers are the average of something. The estimate of p is an average too: if we write one for every order with a pastry and zero for every order without, the average of those zeros and ones is exactly zero point three three.*
   ▸ a strip of 200 zeros and ones, its mean 0.33
3. **Puasson taqsimotini ham shunday moslasak, lambda bahosi yana oʻrtacha chiqadi: har oʻn daqiqada kelgan mijozlar sonining oʻrtachasi. Uchinchi maʼruzadagi uch mingta oraliqda bu uch butun yuzdan toʻqson olti.**
   *Fit a Poisson the same way and the estimate of lambda is an average once more: the mean number of customers per ten minutes. Over Lecture 3's three thousand windows that is three point nine six.*
   ▸ λ̂ = k̄ = 3.96
4. **Oltinchi maʼruzada xuddi shunday holni boshqa tomondan koʻrdik: har bir qoʻshma aprior taqsimotni yangilash — aprior taqsimotga sanoqlarni qoʻshish edi.**
   *Lecture 6 showed the same thing from the other side: every conjugate update was adding counts to the prior.*
5. **Softmaks esa ikki marta chiqdi: uchinchi maʼruzada kategorial taqsimot sifatida, beshinchi maʼruzada kross-entropiya ichida. Lekin u qayerdan kelishini hali aytmadik.**
   *And the softmax has appeared twice: as a categorical distribution in Lecture 3, and inside cross-entropy in Lecture 5. But we have not yet said where it comes from.*
6. **Bu uchta tasodif emas. Bernulli, Puasson, Gauss, kategorial, Beta va Dirixle — bitta oila, faqat har xil kiyimda. Bu maʼruzada ularni shu kiyimdan yechib koʻramiz.**
   *These are not three coincidences. Bernoulli, Poisson, Gaussian, categorical, Beta and Dirichlet are one family in different clothes. In this lecture we take the clothes off.*
   ▸ six distribution cards slide into one row under a single formula, still blank
7. **Sunʼiy intellekt uchun buning foydasi katta: klassifikatorning oxirgi qatlami, uning yoʻqotish funksiyasi va gradienti — hammasi shu bitta oiladan kelib chiqadi.**
   *For AI this pays off directly: a classifier's last layer, its loss and its gradient all come out of this one family.*
8. ⏸ **Keling, oʻzimiz sinab koʻraylik. Videoni toʻxtating. Ikki yuzta buyurtmani nol va birlar bilan yozdik. Ularning yigʻindisi qancha, oʻrtachasi-chi?**
   *Let's try it ourselves. Pause the video. We wrote the two hundred orders as zeros and ones. What is their sum, and their average?*
9. **Yigʻindi — oltmish olti, chunki har bir pishiriqli buyurtma bitta bir qoʻshadi. Oʻrtacha — oltmish oltini ikki yuzga boʻlamiz: nol butun yuzdan oʻttiz uch, pi bahosining oʻzi.**
   *The sum is sixty-six, because each order with a pastry adds a one. The average is sixty-six divided by two hundred: zero point three three, the estimate of p itself.*
10. **Bu oilaning umumiy shaklini qanday topamiz? Eng tanish taqsimotdan — Bernullidan boshlaymiz. Keyingi boʻlimda.**
    *How do we find the family's common form? We start from the most familiar member, the Bernoulli. The next section.*

### 2-boʻlim · Section 2 — Bernullini qayta yozamiz: logit · Rewriting the Bernoulli: the logit
1. **Uchinchi maʼruzadagi Bernulli taqsimotini olamiz: pi darajasi eks, karra bir minus pi darajasi bir minus eks. Eslab olaylik: eks bir boʻlsa, pi qoladi, eks nol boʻlsa — bir minus pi.**
   *We take Lecture 3's Bernoulli: p to the power x, times one minus p to the power one minus x. Recall: if x is one, p is left; if x is zero, one minus p.*
   ▸ p^x (1 − p)^(1−x); x = 1 → p, x = 0 → 1 − p
2. **Hech narsa faraz qilmaymiz, faqat algebra. Logarifm olib, yana eksponentaga qaytaramiz: eks karra pi ning logarifmi, qoʻshuv bir minus eks karra bir minus pi ning logarifmi.**
   *We assume nothing; it is only algebra. We take a logarithm and put it back inside an exponential: x times the log of p, plus one minus x times the log of one minus p.*
   ▸ exp( x log p + (1 − x) log(1 − p) )
3. **Eks qatnashgan hadlarni yigʻamiz. Shunda pi ning bitta birikmasi oʻz-oʻzidan ajralib chiqadi: pi ni bir minus pi ga boʻlib, logarifm olganimiz. Uni eta deb belgilaymiz.**
   *We collect the terms in x. One particular combination of p then appears on its own: p divided by one minus p, and its logarithm. We call it eta.*
   ▸ exp( x · log p/(1 − p) + log(1 − p) ), the bracketed log p/(1 − p) labelled η
4. **Bu birikmaning nomi bor — logit. Pi ni bir minus pi ga boʻlganimiz — pishiriqli buyurtmalarning pishiriqsizlarga nisbati, logit esa shu nisbatning logarifmi.**
   *This combination has a name: the logit. p over one minus p is the ratio of orders with a pastry to orders without, and the logit is the logarithm of that ratio.*
5. **Qahvaxonada pi nol butun oʻndan uch. Nisbat — uchga yetti, yaʼni nol butun yuzdan qirq uch. Uning logarifmi — minus nol butun yuzdan sakson besh. Manfiy, chunki pishiriqli buyurtmalar ozchilik. Eta nol boʻlsa, pi aynan yarim boʻlardi.**
   *In the coffee shop p is zero point three. The ratio is three to seven, that is zero point four three. Its logarithm is minus zero point eight five. Negative, because orders with a pastry are the minority. An eta of zero would mean p is exactly one half.*
   ▸ p = 0.3 → 3/7 = 0.43 → η = −0.85
6. **Logitga ikkinchi tomondan qaraylik: u noldan birgacha boʻlgan oraliqni butun son oʻqiga choʻzadi. Pi nol butun yuzdan toʻqson toʻqqiz boʻlsa, eta taxminan toʻrt butun oʻndan olti, nol butun mingdan toʻqqiz yuz toʻqson toʻqqiz boʻlsa — olti butun oʻndan toʻqqiz. Ishonch ortgan sari eta cheksizlik tomon ketadi.**
   *Let's look at the logit from a second side: it stretches the interval from zero to one over the whole number line. A p of zero point nine nine gives an eta of about four point six, zero point nine nine nine gives six point nine. As certainty grows, eta runs off towards infinity.*
   ▸ the figure's top panel: the logit curve, dots at 0.99 → 4.6 and 0.999 → 6.9
7. **Teskari yoʻl ham bor: eta dan pi ga qaytish uchun birni bir qoʻshuv e darajasi minus eta ga boʻlamiz. Bu sigmoid. Minus nol butun yuzdan sakson beshni sigmoiddan oʻtkazsak, yana nol butun oʻndan uch chiqadi.**
   *There is a way back too: to return from eta to p we divide one by one plus e to the minus eta. That is the sigmoid. Put minus zero point eight five through the sigmoid and zero point three comes out again.*
   ▸ the figure's bottom panel: p = σ(η) = 1/(1 + e^(−η)); the orange dot on both panels
8. **Sunʼiy intellektda klassifikatorning oxirgi qatlami aynan eta ni chiqaradi, sigmoiddan oldin. Nega? Qatlam istalgan haqiqiy sonni chiqara oladi. Ehtimolni noldan birgacha oraliqda majburan ushlab turish kerak boʻlardi, logitni esa nazorat qilish shart emas.**
   *In AI, a classifier's last layer outputs exactly eta, before any sigmoid. Why? A layer can output any real number it likes. A probability would have to be held inside zero to one by force; a logit needs no policing.*
9. ⏸ **Keling, oʻzimiz sinab koʻraylik. Videoni toʻxtating. Pi nol butun oʻndan yetti boʻlsa, eta qancha?**
   *Let's try it ourselves. Pause the video. If p is zero point seven, what is eta?*
10. **Nisbat agʻdariladi: yettiga uch. Uning logarifmi — plyus nol butun yuzdan sakson besh. Logit nol atrofida simmetrik: pi ni bir minus pi ga almashtirsak, faqat ishorasi oʻzgaradi.**
    *The ratio turns over: seven to three. Its logarithm is plus zero point eight five. The logit is symmetric about zero: swap p for one minus p and only the sign changes.*
11. **Javoblar ikkitadan koʻp boʻlsa-chi? Keyingi boʻlimda.**
    *What if there are more than two answers? The next section.*

### 3-boʻlim · Section 3 — Kategorial taqsimot: softmaks · Rewriting the categorical: the softmax
1. **Stakan oʻlchami uchta: kichik, oʻrta va katta. Uni bitta birlik vektor bilan yozamiz: tanlangan oʻlcham oʻrnida bir, qolganlarida nol. Masalan, oʻrta stakan — nol, bir, nol.**
   *There are three cup sizes: small, medium and large. We write a size as a one-hot vector: a one in the chosen size's place, zeros elsewhere. A medium cup, for example, is zero, one, zero.*
   ▸ one-hot vectors (1, 0, 0), (0, 1, 0), (0, 0, 1) under three cups
2. **Uchinchi maʼruzadagi kategorial taqsimot: har bir ulush darajasi oʻz eks i, va hammasi koʻpaytiriladi. Logarifm olsak, yigʻindi chiqadi: eks lar karra ulushlarning logarifmi. Demak bu yerda eta — har bir ulushning logarifmi.**
   *Lecture 3's categorical distribution: each share raised to its own x, all multiplied together. Take the logarithm and a sum comes out: the x's times the logs of the shares. So here eta is the logarithm of each share.*
   ▸ Π p_c^(x_c) = exp(Σ x_c log p_c),  η_c = log p_c
3. **Kichik stakan ulushi nol butun oʻndan ikki, oʻrtasiniki nol butun oʻndan besh, kattasiniki nol butun oʻndan uch. Ularning logarifmlari: minus bir butun yuzdan oltmish bir, minus nol butun yuzdan oltmish toʻqqiz va minus bir butun oʻndan ikki.**
   *The small cup's share is zero point two, the medium's zero point five, the large's zero point three. Their logarithms: minus one point six one, minus zero point six nine and minus one point two.*
   ▸ (0.2, 0.5, 0.3) → (−1.61, −0.69, −1.20)
4. **Endi bir hiyla. Ulushlar yigʻindisi bir, uning logarifmi esa nol. Shuning uchun eksponentadan ey ni — e darajasi eta lar yigʻindisining logarifmini — ayirsak, hech narsa oʻzgarmaydi. Lekin endi barcha eta larga bir xil son qoʻshish zararsiz: ey uni yutib yuboradi.**
   *Now a trick. The shares add up to one, and its logarithm is zero. So subtracting A, the log of the sum of e to the eta's, changes nothing. But now adding the same number to every eta is harmless: A absorbs it.*
   ▸ A(η) = log Σ e^(η_c) = 0
5. **Demak eta lar endi logarifmik ehtimollar emas, oddiy ballar. Ulushlarni qaytarish uchun har bir e darajasi eta ni hammasining yigʻindisiga boʻlamiz. Bu softmaks: biz uni oʻylab topmadik, u oʻz-oʻzidan keltirib chiqarildi.**
   *So the eta's are no longer log-probabilities, just scores. To get the shares back, we divide each e to the eta by the sum of them all. That is the softmax: we did not invent it, it was derived.*
   ▸ p_c = e^(η_c) / Σ_j e^(η_j)
6. **Tekshiramiz: uchta ball softmaksdan oʻtib, aynan nol butun oʻndan ikki, nol butun oʻndan besh va nol butun oʻndan uchni qaytaradi. Har bir ballga ikki qoʻshsak — nol butun yuzdan oʻttiz toʻqqiz, bir butun yuzdan oʻttiz bir va nol butun oʻndan sakkiz — ulushlar yana oʻsha-oʻsha.**
   *We check: the three scores go through the softmax and return exactly zero point two, zero point five and zero point three. Add two to every score, giving zero point three nine, one point three one and zero point eight, and the shares are the same again.*
   ▸ two rows of scores, the same three bars under both
7. **Nega? Har bir ballga ikki qoʻshish suratni ham, maxrajni ham e kvadratga koʻpaytiradi, va u qisqarib ketadi. Demak ballarning oʻzi emas, ular orasidagi farq muhim. Oʻrta va kichik stakan ballari orasidagi farq nol butun yuzdan toʻqson ikki, bu ikki yarimning logarifmi: oʻrta stakan kichigidan ikki yarim baravar koʻp olinadi.**
   *Why? Adding two to every score multiplies both the numerator and the denominator by e squared, and it cancels. So what matters is not the scores themselves but the gaps between them. The gap between the medium and small scores is zero point nine two, the logarithm of two and a half: a medium cup is ordered two and a half times as often as a small one.*
   ▸ gap 0.92 = log 2.5;  bars 0.5 / 0.2 = 2.5
8. **Bernulli ham shu yerda yashiringan. Ikkita javob boʻlsa va bittasining ballini nol desak, softmaks aynan sigmoidga aylanadi: minus nol butun yuzdan sakson besh va nol ballari yana nol butun oʻndan uchni beradi. Sigmoid — ikki javobli softmaks.**
   *The Bernoulli is hiding here too. With two answers, and one score set to zero, the softmax turns into the sigmoid exactly: the scores minus zero point eight five and zero give zero point three again. The sigmoid is a two-answer softmax.*
   ▸ softmax(η, 0) = σ(η);  (−0.85, 0) → 0.3
9. **Sunʼiy intellektda klassifikator har bir sinfga bitta ball chiqaradi va uni softmaksdan oʻtkazadi. Ballarga bir xil son qoʻshilsa javob oʻzgarmasligidan freymvorklar foydalanadi: hisoblashdan oldin eng katta ballni ayirib qoʻyadi.**
   *In AI, a classifier outputs one score per class and passes them through the softmax. Frameworks use the fact that adding the same number changes nothing: they subtract the largest score before computing.*
10. ⏸ **Keling, oʻzimiz sinab koʻraylik. Videoni toʻxtating. Uchala ball ham nol boʻlsa, softmaks qanday ulushlar beradi?**
    *Let's try it ourselves. Pause the video. If all three scores are zero, what shares does the softmax give?*
11. **Har biri e darajasi nol, yaʼni bir. Yigʻindisi uch. Har bir ulush uchdan bir: ballar teng boʻlsa, ulushlar ham teng.**
    *Each is e to the zero, that is one. The sum is three. Each share is one third: equal scores, equal shares.*
12. **Bernulli va kategorial taqsimotda bir xil shakl chiqdi. Uni umumiy koʻrinishda yozamiz. Keyingi boʻlimda.**
    *The Bernoulli and the categorical gave the same shape. We write it in general. The next section.*

### 4-boʻlim · Section 4 — Eksponensial oila · The exponential family
1. **Taqsimot eksponensial oilaga kiradi, agar uni shunday yozish mumkin boʻlsa: eych eks, karra e darajasi eta karra ti eks minus ey eta.**
   *A distribution is in the exponential family if it can be written like this: h of x, times e to the eta times T of x, minus A of eta.*
   ▸ p(x | η) = h(x) exp( η T(x) − A(η) )
2. **Unda toʻrtta boʻlak bor. Ti eks — yetarli statistika: berilganlarning aytadigan yagona gapi. Bernullida u eks ning oʻzi.**
   *It has four pieces. T of x is the sufficient statistic: the only thing the data gets to say. For the Bernoulli it is x itself.*
3. **Eta — tabiiy parametr: oila aynan shu koordinatada toʻgʻri chiziqdek sodda koʻrinadi. Bernullida u logit.**
   *Eta is the natural parameter: the coordinate in which the family looks as simple as a straight line. For the Bernoulli it is the logit.*
4. **Ey eta — normallovchi funksiya: umumiy ehtimolni birga keltirish uchun nima kerak boʻlsa, oʻsha. Bernullida u bir qoʻshuv e darajasi eta ning logarifmi. Eych eks esa eta ga umuman tegmaydigan qolgan hisob-kitob. Bernullida u bir.**
   *A of eta is the log-partition function: whatever it takes to make the total probability one. For the Bernoulli it is the log of one plus e to the eta. And h of x is the leftover bookkeeping that never touches eta. For the Bernoulli it is one.*
   ▸ the four pieces, each with its Bernoulli value: T = x, η = logit, A = log(1 + e^η), h = 1
5. **Butun mazmun shaklda: eks bilan eta faqat bitta joyda — eta karra ti eks koʻpaytmasida uchrashadi. Maʼruzaning qolgan hamma qismi shu bitta cheklovdan kelib chiqadi.**
   *The shape is the whole content: x and eta meet in only one place, the product eta times T of x. Everything else in this lecture follows from that one restriction.*
6. **Shu cheklovga boshqa tomondan qaraylik. Berilganlar eta bilan faqat ti eks orqali gaplashadi. Ti eks ga kirmagan hech narsa — tartib, vaqt, ismlar — eta haqida hech narsa demaydi. Ikkinchi qismda buning foydasini ham, narxini ham koʻramiz.**
   *Let's look at that restriction from another side. The data talks to eta only through T of x. Nothing left out of T of x, whether order, time or names, says anything about eta. In part one we see both the benefit and the price of that.*
7. **Toʻrtta tanish taqsimot jadvalda. Puassonda ti — sanoq, eta — lambda ning logarifmi, ey — e darajasi eta. Sigmasi maʼlum Gaussda ti — eks, eta — mu ni sigma kvadratga boʻlganimiz. Kategorialda ti — bitta birlik vektor, eta — ballar, ey — log-sum-eksp.**
   *Four familiar distributions in a table. For the Poisson, T is the count, eta is the log of lambda, and A is e to the eta. For a Gaussian with known sigma, T is x and eta is mu over sigma squared. For the categorical, T is the one-hot vector, eta the scores, and A the log-sum-exp.*
   ▸ the table: T(x), η, A(η) for Bernoulli, Poisson, Gaussian (σ known), Categorical
8. **Beta va Dirixle ham shu oilada, faqat rollar almashgan: ularda ehtimolning oʻzi berilgan, ti esa pi ning logarifmi va bir minus pi ning logarifmi.**
   *The Beta and the Dirichlet are in it too, with the roles swapped: there the probability itself is the data, and T is the log of p and the log of one minus p.*
9. **Lekin hamma taqsimot ham bu oilaga kirmaydi. Styudent taqsimotini yoki toʻrtinchi maʼruzadagi ikki Gauss aralashmasini bu shaklga sigʻdirib boʻlmaydi. Aynan shuning uchun ularni moslash qiyinroq.**
   *But not every distribution is in it. A Student's t, or a mixture of two Gaussians from Lecture 4, cannot be squeezed into this shape. That is exactly why they are harder to fit.*
10. **Sunʼiy intellektda Gauss aralashmasi modelini moslash uchun alohida, qadam-baqadam ishlaydigan algoritm kerak boʻladi: aralashmaning oʻzi bu oilaga kirmaydi, uning har bir komponentasi esa kiradi.**
    *In AI, fitting a Gaussian mixture model needs a separate, step-by-step algorithm: the mixture itself is not in this family, while each of its components is.*
11. ⏸ **Keling, oʻzimiz sinab koʻraylik. Videoni toʻxtating. Uchinchi maʼruzadagi qahvaxonaga oʻn daqiqada oʻrtacha toʻrtta mijoz kiradi. Puassonning tabiiy parametri eta qancha?**
    *Let's try it ourselves. Pause the video. In Lecture 3's coffee shop, four customers come in per ten minutes on average. What is the Poisson's natural parameter eta?*
12. **Toʻrtning logarifmi: taxminan bir butun yuzdan oʻttiz toʻqqiz.**
    *The logarithm of four: about one point three nine.*
13. **Ey eta hisob-kitobga oʻxshaydi. Aslida u nimani biladi? Keyingi boʻlimda.**
    *A of eta looks like bookkeeping. What does it really know? The next section.*

### 5-boʻlim · Section 5 — Ey eta va uning qiyaligi · A(η) and its slope
1. **Nega ey eta kerak? Eych eks karra e darajasi eta karra ti eks — yaxshi shakl, lekin uning yigʻindisi bir emas. Ey eta — shu yigʻindining logarifmi, va biz uni ayirib, yigʻindini birga keltiramiz.**
   *Why do we need A of eta? h of x times e to the eta T of x is a fine shape, but its total is not one. A of eta is the logarithm of that total, and subtracting it brings the total to one.*
   ▸ A(η) = log Σₓ h(x) e^(η T(x))
2. **Bernullida ikkita normallanmagan ogʻirlik bor. Eks nol uchun e darajasi nol, yaʼni bir. Eks bir uchun e darajasi eta, yaʼni nol butun yuzdan qirq uch — qahvaxonadagi nisbatning oʻzi. Yigʻindisi bir butun yuzdan qirq uch, logarifmi esa nol butun mingdan uch yuz ellik yetti. Bu aynan minus nol butun oʻndan yettining logarifmi.**
   *The Bernoulli has two unnormalized weights. For x equal to zero, e to the zero, that is one. For x equal to one, e to the eta, that is zero point four three, the coffee shop's ratio itself. Their total is one point four three, and its logarithm is zero point three five seven. That is exactly minus the log of zero point seven.*
   ▸ weights 1 and 0.43, total 1.43;  log 1.43 = 0.357 = −log 0.7
3. **Ogʻirliklarni yigʻindiga boʻlsak, ehtimollar qaytadi: nol butun yuzdan qirq uchni bir butun yuzdan qirq uchga boʻlsak — nol butun oʻndan uch. Normallash — aynan shu boʻlish.**
   *Divide the weights by their total and the probabilities come back: zero point four three divided by one point four three is zero point three. Normalizing is exactly that division.*
4. **Kategorialda ey — log-sum-eksp: ballar eksponentalari yigʻindisining logarifmi. Har bir chuqur oʻqitish freymvorki softmaksni normallash uchun aynan shuni hisoblaydi.**
   *For the categorical, A is the log-sum-exp: the log of the sum of the scores' exponentials. Every deep learning framework computes exactly this to normalize a softmax.*
5. **Lekin ey shunchaki hisob-kitob emas. Uni bir marta differensiallasak, ti ning oʻrtachasi chiqadi, ikki marta differensiallasak — dispersiyasi.**
   *But A is not mere bookkeeping. Differentiate it once and the mean of T comes out; twice, and its variance.*
   ▸ A′(η) = E[T],  A″(η) = Var(T)
6. **Bernullida eta minus nol butun yuzdan sakson besh boʻlganda ey ning qiyaligi nol butun oʻndan uch, yaʼni pi ning oʻzi. Ikkinchi hosilasi — pi karra bir minus pi, nol butun yuzdan yigirma bir. Bu uchinchi maʼruzadagi Bernulli dispersiyasi.**
   *For the Bernoulli at eta minus zero point eight five, the slope of A is zero point three, p itself. Its second derivative is p times one minus p, zero point two one. That is Lecture 3's Bernoulli variance.*
   ▸ the figure: A(η) with its tangent, slope 0.30; below it A′(η) = σ(η) at 0.30
7. **Qiyalikni hosilasiz ham tekshirsa boʻladi: eta ni nol butun yuzdan birga oshirib va kamaytirib, ey ning oʻzgarishini qadamga boʻlamiz. Yana nol butun oʻndan uch chiqadi.**
   *We can check the slope without calculus too: raise and lower eta by zero point zero one and divide the change in A by the step. Zero point three comes out again.*
   ▸ (A(η + 0.01) − A(η − 0.01)) / 0.02 = 0.30
8. **Puassonda ey — e darajasi eta. Eksponentaning hosilasi oʻzi, shuning uchun birinchi hosila ham, ikkinchisi ham lambda. Puassonda oʻrtacha dispersiyaga teng boʻlishining sababi shu. Uchinchi maʼruzadagi uch mingta oraliqda oʻrtacha uch butun yuzdan toʻqson olti, dispersiya esa uch butun yuzdan sakson toʻrt chiqqan edi — xuddi shu qoida aytgandek, bir-biriga yaqin.**
   *For the Poisson, A is e to the eta. The exponential is its own derivative, so the first derivative and the second are both lambda. That is why the Poisson's mean equals its variance. Over Lecture 3's three thousand windows the mean came out at three point nine six and the variance at three point eight four: close, just as the rule says.*
   ▸ A = A′ = A″ = e^η = λ;  Lecture 3's simulation: mean 3.96, variance 3.84
9. **Sunʼiy intellektda klassifikatorning oxirgi qatlami chiqaradigan logitlar — kategorial taqsimotning tabiiy parametrlari. Sigmoid va softmaks esa dizayn tanlovi emas: ular eta dan ehtimolga qaytadigan teskari yoʻl.**
   *In AI, the logits a classifier's last layer produces are the natural parameters of a categorical. The sigmoid and the softmax are not design choices: they are the way back from eta to probabilities.*
10. **Shuning uchun freymvorklar logitlarni toʻgʻridan-toʻgʻri yoʻqotish funksiyasiga beradi: log-sum-eksp — bu ey eta, va uni bir marta, ehtiyot boʻlib hisoblash barqarorroq. Masalan, ballar ming va toʻqqiz yuz toʻqson toʻqqiz boʻlsa, e darajasi ming kompyuterda cheksizlikka toʻlib ketadi. Eng katta ballni oldin ayirsak, javob bemalol chiqadi: ming butun yuzdan oʻttiz bir.**
    *That is why frameworks hand the logits straight to the loss: the log-sum-exp is A of eta, and computing it once, carefully, is more stable. If the scores are one thousand and nine hundred ninety-nine, for example, e to the thousand overflows to infinity on a computer. Subtract the largest score first and the answer comes out calmly: one thousand point three one.*
    ▸ e¹⁰⁰⁰ → ∞;  1000 + log(1 + e^(−1)) = 1000.31
11. ⏸ **Keling, oʻzimiz sinab koʻraylik. Videoni toʻxtating. Puasson uchun lambda toʻrt. Ey ning birinchi va ikkinchi hosilasi qancha?**
    *Let's try it ourselves. Pause the video. For a Poisson, lambda is four. What are the first and second derivatives of A?*
12. **Ey — e darajasi eta, eta esa toʻrtning logarifmi. Ikkala hosila ham e darajasi eta, yaʼni toʻrt: oʻrtacha ham, dispersiya ham toʻrt.**
    *A is e to the eta, and eta is the logarithm of four. Both derivatives are e to the eta, that is four: the mean is four and so is the variance.*
13. **Ey ning qiyaligi oʻrtacha boʻlsa, maksimal haqiqatga oʻxshashlik nimaga aylanadi? Keyingi boʻlimda.**
    *If the slope of A is the mean, what does maximum likelihood turn into? The next section.*

### 6-boʻlim · Section 6 — Maksimal haqiqatga oʻxshashlik — oʻrtachalarni tenglashtirish · MLE is moment matching
1. **Beshinchi maʼruzadan eslaylik: mustaqil kuzatuvlarda haqiqatga oʻxshashlik koʻpaytma, uning logarifmi esa yigʻindi. Eng yaxshi parametrni topish uchun hosilani nolga tenglaymiz.**
   *Recall from Lecture 5: for independent observations the likelihood is a product and its logarithm a sum. To find the best parameter, we set the derivative to zero.*
2. **Eksponensial oilada bu yigʻindi juda sodda: eta karra ti lar yigʻindisi minus en karra ey eta. Hosilasi — ti lar yigʻindisi minus en karra ey ning qiyaligi.**
   *In the exponential family this sum is very simple: eta times the sum of the T's, minus n times A of eta. Its derivative is the sum of the T's minus n times the slope of A.*
   ▸ ℓ(η) = η Σ T(xᵢ) − n A(η) + const;  ∂ℓ/∂η = Σ T(xᵢ) − n A′(η)
3. **Nolga tenglab, en ga boʻlamiz. Ey ning qiyaligi ti ning kutilmasi edi. Demak, model kutgan ti ning oʻrtachasi berilganlardagi ti ning oʻrtachasiga teng boʻlishi kerak.**
   *We set it to zero and divide by n. The slope of A was the expectation of T. So the average of T the model expects must equal the average of T in the data.*
   ▸ boxed: E_η̂[T(X)] = (1/n) Σ T(xᵢ)
4. **Soʻz bilan aytsak: modelning oʻrtachasi berilganlarning oʻrtachasiga mos keladigan parametrni tanlaymiz. Bu oilada maksimal haqiqatga oʻxshashlikning butun mazmuni shu.**
   *In words: we pick the parameter whose average matches the data's average. That is all of maximum likelihood for this family.*
5. **Bernulli: sigmoid eta bahosi eks chiziqchaga teng, demak pi bahosi key ni en ga boʻlganimiz. Gauss: mu bahosi eks chiziqcha. Puasson: lambda bahosi sanoqlar oʻrtachasi. Beshinchi maʼruzadagi uchta alohida hisob — bitta qatorda.**
   *Bernoulli: the sigmoid of the estimated eta equals x bar, so the estimate of p is k over n. Gaussian: the estimate of mu is x bar. Poisson: the estimate of lambda is the mean count. Lecture 5's three separate derivations, in one line.*
   ▸ σ(η̂) = x̄ → p̂ = k/n;  μ̂ = x̄;  e^η̂ = k̄ → λ̂ = k̄
6. **Rasmda koʻraylik. Qizil chiziq — berilganlar oʻrtachasi, egri chiziq — modelning oʻrtachasi, ular kesishgan joyda baho turadi. Bernullida ikki yuzdan oltmish olti: chiziq nol butun yuzdan oʻttiz uchda, eta bahosi minus nol butun yuzdan yetmish bir. Puassonda oʻrtacha uch butun yuzdan toʻqson olti, eta bahosi uning logarifmi — bir butun yuzdan oʻttiz sakkiz.**
   *Let's see it in the figure. The red line is the data's average, the curve is the model's average, and the estimate sits where they cross. For the Bernoulli, sixty-six out of two hundred: the line is at zero point three three and the estimated eta is minus zero point seven one. For the Poisson, the average is three point nine six and the estimated eta is its logarithm, one point three eight.*
   ▸ the figure: moment matching, Bernoulli and Poisson panels
7. **Gradientni boshqa tomondan oʻqiylik: u kuzatilgan ti minus kutilgan ti. Agar pi nol butun oʻndan uch boʻlsa, model ikki yuzta buyurtmada oltmishta pishiriq kutadi, biz esa oltmish oltitasini koʻrdik. Farq — plyus olti: gradient eta ni yuqoriga suradi va farq nolga tushguncha surishda davom etadi.**
   *Let's read the gradient from another side: it is observed T minus expected T. If p were zero point three, the model would expect sixty pastries in two hundred orders, while we saw sixty-six. The difference is plus six: the gradient pushes eta up, and keeps pushing until the difference is zero.*
   ▸ observed 66 − expected 60 = +6 → η moves right
8. **Sunʼiy intellektda log-chiziqli va energiyaga asoslangan modellar aynan shu signal bilan oʻqitiladi: kuzatilgan statistika minus kutilgan statistika. Qiyin joyi — kutilgan statistikani hisoblash. Softmaks bilan kross-entropiyaning gradienti ham shu: bashorat qilingan ulushlar minus bitta birlik vektor.**
   *In AI, log-linear and energy-based models are trained on exactly this signal: observed statistic minus expected statistic. The hard part is computing the expected one. The gradient of softmax with cross-entropy is the same thing: predicted shares minus the one-hot vector.*
9. ⏸ **Keling, oʻzimiz sinab koʻraylik. Videoni toʻxtating. Uchinchi maʼruzadagi simulyatsiyaning birinchi oʻnta oraligʻida jami oʻttiz uchta mijoz keldi. Puasson uchun eta bahosi qancha?**
   *Let's try it ourselves. Pause the video. In the first ten windows of Lecture 3's simulation, thirty-three customers arrived in all. What is the estimated eta for a Poisson?*
10. **Oʻrtacha — oʻttiz uchni oʻnga boʻlamiz: uch butun oʻndan uch. Eta bahosi uning logarifmi: taxminan bir butun yuzdan oʻn toʻqqiz.**
    *The average is thirty-three divided by ten: three point three. The estimated eta is its logarithm: about one point one nine.*
11. **Mana shu bilan nolinchi qismni tugatamiz. Maksimal haqiqatga oʻxshashlik berilganlardan faqat ti lar yigʻindisini ishlatdi. Qolgan hammasini tashlab yuborsak, biror narsa yoʻqotamizmi? Birinchi qismda.**
    *That brings us to the end of part zero. Maximum likelihood used only the sum of the T's from the data. If we throw everything else away, do we lose anything? Part one.*

## Part 1 — Yetarli statistikalar
▸ part card "1-qism · Yetarli statistikalar"

### 7-boʻlim · Section 7 — Yetarli statistika · The sufficient statistic
1. **Beshinchi maʼruzada pi ni ikki yuzta qahva buyurtmasidan baholadik va javob ikki yuzdan oltmish olti chiqdi. Ikki yuzta yozuv kirdi, bitta son chiqdi.**
   *In Lecture 5 we estimated p from two hundred coffee orders and the answer was sixty-six out of two hundred. Two hundred records went in; one number came out.*
2. **Noqulay savol: oʻsha ikki yuzta yozuv hali qoʻlimizda — kim nima olgani, qaysi tartibda, qaysi tongda. Ularni tashlab yuborsak, pi haqida biror narsa yoʻqotamizmi?**
   *The uncomfortable question: we still hold those two hundred records, who bought what, in which order, on which morning. If we throw them away, do we lose anything about p?*
3. **Javob — yoʻq, va bu taxminiy emas, aniq. Jami oltmish olti boʻlgan har qanday ikki yozuv bir xil haqiqatga oʻxshashlik egri chizigʻini beradi, demak bir xil bahoni, bir xil oraliqni va bir xil aposterior taqsimotni.**
   *The answer is no, and it is exact, not approximate. Any two records with the same total of sixty-six give the same likelihood curve, and so the same estimate, the same interval and the same posterior.*
4. **Taʼrif shunday: agar ti ni bilganimizdan keyin berilganlar teta haqida boshqa hech narsa aytmasa, ti statistika teta uchun yetarli.**
   *The definition: a statistic T is sufficient for theta if, once we know T, the data says nothing more about theta.*
   ▸ T is sufficient: p(x | T(x), θ) does not depend on θ
5. **Buni sanab ham koʻrsa boʻladi. Ikki yuzta buyurtma ichida oltmish olti pishiriqni joylashtirishning juda koʻp usuli bor — ellik toʻrt xonali son. Jami oltmish olti ekanini bilsak, bu usullarning har biri bir xil ehtimolli, va bu ehtimolda pi yoʻq. Pi nol butun oʻndan ikki boʻlsin yoki yarim — farqi yoʻq. Demak, tartib pi haqida hech narsa aytmaydi.**
   *We can count it too. There are very many ways to place sixty-six pastries among two hundred orders: a number fifty-four digits long. Once we know the total is sixty-six, each of these ways is equally likely, and that likelihood contains no p. Whether p is zero point two or a half makes no difference. So the order says nothing about p.*
   ▸ C(200, 66), a 54-digit number; given the total, each arrangement has probability 1/C(200, 66) for p = 0.2, 0.33 and 0.5 alike
6. **Birinchi maʼruzadagi koʻpaytirish qoidasidan ham shu kelib chiqadi: bitta ketma-ketlikning ehtimoli — pi darajasi oltmish olti, karra bir minus pi darajasi bir yuz oʻttiz toʻrt. Koʻpaytuvchilarning oʻrni almashsa, koʻpaytma oʻzgarmaydi.**
   *Lecture 1's multiplication rule says the same: one sequence has probability p to the sixty-six, times one minus p to the one hundred thirty-four. Swapping the factors around does not change the product.*
   ▸ p⁶⁶ (1 − p)¹³⁴ for any order of the 200 orders
7. **Uchta oʻn tonglik yozuvni olaylik, har tongda yigirmatadan buyurtma. Birinchisi bir tekis, ikkinchisida bitta katta kun bor, uchinchisi asta-sekin oʻsib boradi. Uchalasining ham jami ikki yuzdan oltmish olti.**
   *Take three ten-morning records, twenty orders a morning. The first is steady, the second has one big day, the third builds up slowly. All three total sixty-six out of two hundred.*
   ▸ the figure's top panel: the three records
8. **Pastki rasmda uchala logarifmik haqiqatga oʻxshashlik chizilgan. Bitta egri chiziq koʻrinadi, chunki ular haqiqatan bitta: oltmish olti karra pi ning logarifmi qoʻshuv bir yuz oʻttiz toʻrt karra bir minus pi ning logarifmi. Choʻqqisi ham, egriligi ham bir xil.**
   *The lower panel plots all three log-likelihoods. We see one curve because they really are one: sixty-six times the log of p, plus one hundred thirty-four times the log of one minus p. Same peak, same curvature.*
   ▸ the figure's bottom panel: one curve, p̂ = 0.33
9. **Bernullida yetarli statistika — muvaffaqiyatlar soni, Puassonda — jami sanoq, Gaussda esa ikkita yigʻindi: eks larning yigʻindisi va eks kvadratlarning yigʻindisi. Nolinchi qism buni butun oila uchun allaqachon koʻrsatdi: berilganlar eta ga faqat ti lar yigʻindisi orqali yetib boradi.**
   *For the Bernoulli the sufficient statistic is the number of successes, for the Poisson the total count, and for the Gaussian two sums: the sum of the x's and the sum of the x's squared. Part zero already showed it for the whole family: the data reaches eta only through the sum of the T's.*
10. **Sunʼiy intellektda bu katta tejash: milliardlab misoldan bitta Bernulli parametrini baholash uchun ikkita son — muvaffaqiyatlar soni va jami misollar soni — yetarli.**
    *In AI this is a big saving: to estimate one Bernoulli parameter from billions of examples, two numbers are enough, the number of successes and the total number of examples.*
11. ⏸ **Keling, oʻzimiz sinab koʻraylik. Videoni toʻxtating. «Bitta katta kun» yozuvida birinchi tongda yigirmata buyurtmaning hammasida pishiriq bor edi. Bu yozuv uchun pi bahosi bir tekis yozuvnikidan farq qiladimi?**
    *Let's try it ourselves. Pause the video. In the "one big day" record, all twenty orders on the first morning had a pastry. Is this record's estimate of p different from the steady record's?*
12. **Farq qilmaydi. Jami yana ikki yuzdan oltmish olti, baho nol butun yuzdan oʻttiz uch. Katta kun qachon boʻlgani pi haqida hech narsa demaydi.**
    *No. The total is again sixty-six out of two hundred, and the estimate zero point three three. When the big day happened says nothing about p.*
13. **Taqsimot formulasiga qarab, yetarli statistikani qanday topamiz? Keyingi boʻlimda.**
    *How do we find the sufficient statistic just by looking at a distribution's formula? The next section.*

### 8-boʻlim · Section 8 — Faktorizatsiya testi va Gauss · The factorization test, and what a Gaussian needs
1. **Fisher–Neyman testi: zichlikni ikki koʻpaytuvchiga ajratish mumkin boʻlsa, ti teta uchun yetarli. Birinchi koʻpaytuvchi teta ga tegadi, lekin berilganlarni faqat ti orqali koʻradi. Ikkinchisida teta umuman yoʻq.**
   *The Fisher–Neyman test: T is sufficient for theta when the density splits into two factors. The first touches theta but sees the data only through T. The second has no theta at all.*
   ▸ p(x | θ) = g(T(x), θ) × h(x)
2. **Oʻqish oson: teta ning har bir uchrashgan joyini berilganlarni faqat ti orqali koʻradigan koʻpaytuvchiga oʻtkaza olsak, ti hamma axborotni olib yuradi.**
   *Reading it is easy: if we can move every appearance of theta into a factor that sees the data only through T, then T carries all the information.*
3. **Eksponensial oilaning taʼrifi aynan shu ajratish: eych eks — ikkinchi koʻpaytuvchi, e darajasi eta karra ti eks minus ey eta — birinchisi. Shuning uchun oilaga kirish yetarli statistikani tekin beradi: ti ni oʻqib olamiz, xolos.**
   *The exponential family's definition is exactly this split: h of x is the second factor, and e to the eta T of x minus A of eta is the first. So membership in the family hands us the sufficient statistic for free: we just read off T.*
   ▸ h(x) · exp(η T(x) − A(η)), the two factors boxed as h and g
4. **Beshinchi maʼruzadagi qirqta espressoni olaylik: mu bahosi yigirma toʻqqiz butun yuzdan sakson sakkiz, sigma bahosi bir butun yuzdan yigirma yetti millilitr. Zichlikdagi kvadratni ochsak, berilganlar faqat ikki joyda qoladi: eks lar yigʻindisi va eks kvadratlar yigʻindisi.**
   *Take Lecture 5's forty espresso shots: the estimate of mu is twenty-nine point eight eight and of sigma one point two seven millilitres. Expand the square in the density and the data is left in only two places: the sum of the x's and the sum of the x's squared.*
   ▸ the expanded exponent, Σxᵢ and Σxᵢ² highlighted
5. **Bu yerda ular bir ming bir yuz toʻqson besh butun oʻndan bir va oʻttiz besh ming yetti yuz yetmish butun oʻndan olti. Qirqta oʻlchov oʻrniga ikkita son. Qirq ming oʻlchov boʻlsa ham, yana ikkita son: yetarli statistika tanlanma bilan birga oʻsmaydi.**
   *Here they are one thousand one hundred ninety-five point one and thirty-five thousand seven hundred seventy point six. Two numbers instead of forty measurements. Forty thousand measurements would still be two numbers: the sufficient statistic does not grow with the sample.*
   ▸ Σx = 1195.1, Σx² = 35770.6; forty dots collapse into two counters
6. **Ikki yigʻindidan bahoni qanday qaytaramiz? Oʻrtacha — birinchi yigʻindini qirqqa boʻlganimiz. Dispersiya uchun esa uchinchi maʼruzadagi qoida: kvadratlar oʻrtachasi minus oʻrtachaning kvadrati. Kvadratlar oʻrtachasi sakkiz yuz toʻqson toʻrt butun yuzdan yigirma olti, oʻrtachaning kvadrati sakkiz yuz toʻqson ikki butun yuzdan oltmish besh. Ayirmasi bir butun yuzdan oltmish bir, uning ildizi bir butun yuzdan yigirma yetti — beshinchi maʼruzadagi sigmaning oʻzi.**
   *How do we get the estimates back from the two sums? The mean is the first sum divided by forty. For the variance, Lecture 3's rule: the mean of the squares minus the square of the mean. The mean of the squares is eight hundred ninety-four point two six, the square of the mean eight hundred ninety-two point six five. Their difference is one point six one, and its square root one point two seven: Lecture 5's sigma itself.*
   ▸ 894.26 − 892.65 = 1.61,  √1.61 = 1.27
7. **Lekin nima uchun yetarli ekaniga ehtiyot boʻlaylik. Bu ikki son mu va sigmani belgilaydi, lekin espressolar normal taqsimlanganmi yoki yoʻqmi — bu haqda hech narsa demaydi. Yigirmata espresso yigirma sakkiz butun yuzdan oltmish bir, yigirmatasi oʻttiz bir butun yuzdan oʻn besh millilitr boʻlsa ham, ikkala yigʻindi aynan oʻsha chiqadi. Bu ikki ustun qoʻngʻiroqqa umuman oʻxshamaydi. Modelni tekshirish uchun xom berilganlar yana kerak.**
   *But let's be careful about what they are sufficient for. These two numbers fix mu and sigma, but say nothing about whether the shots are normally distributed at all. If twenty shots were twenty-eight point six one and twenty were thirty-one point one five millilitres, both sums would come out exactly the same. Those two spikes look nothing like a bell. Checking the model needs the raw data back.*
   ▸ the 40 shots' histogram beside two spikes at 28.61 and 31.15; the same Σx and Σx² under both
8. **Sunʼiy intellektda paketli normallashtirish aynan shu ikki kattalikni — oʻrtacha va dispersiyani — yuritib boradi, oʻqitish berilganlarini qayta koʻrib chiqmaydi.**
   *In AI, batch normalization keeps exactly these two quantities running, the mean and the variance, rather than replaying the training data.*
9. ⏸ **Keling, oʻzimiz sinab koʻraylik. Videoni toʻxtating. Eks lar yigʻindisi bir ming bir yuz toʻqson besh butun oʻndan bir, espressolar soni qirqta. Oʻrtacha hajm qancha?**
   *Let's try it ourselves. Pause the video. The sum of the x's is one thousand one hundred ninety-five point one, and there are forty shots. What is the mean volume?*
10. **Qirqqa boʻlamiz: yigirma toʻqqiz butun yuzdan sakson sakkiz millilitr. Mu bahosi — xom berilganlarga qaramasdan.**
    *We divide by forty: twenty-nine point eight eight millilitres. The estimate of mu, without looking at the raw data.*
11. **Oltinchi maʼruzada qoʻshma aprior taqsimotni yangilash nega sanash boʻlgan edi? Keyingi boʻlimda.**
    *Why was updating a conjugate prior just counting in Lecture 6? The next section.*

### 9-boʻlim · Section 9 — Qoʻshma aprior taqsimot nega ishladi · Why conjugacy worked
1. **Oltinchi maʼruzada Beta va Dirixleni yangilash oddiy sanash ekanini koʻrdik, lekin sababini ochiq qoldirdik. Mana u.**
   *Lecture 6 showed that updating a Beta or a Dirichlet is plain counting, and left the reason open. Here it is.*
2. **Aposterior taqsimot — aprior taqsimot karra haqiqatga oʻxshashlik. Haqiqatga oʻxshashlik esa eksponensial shaklda: e darajasi eta karra ti lar yigʻindisi minus en karra ey eta.**
   *The posterior is the prior times the likelihood. And the likelihood has the exponential form: e to the eta times the sum of the T's, minus n times A of eta.*
   ▸ p(η | x₁, …, xₙ) ∝ p(η) exp( η Σ T(xᵢ) − n A(η) )
3. **Berilganlar aynan ikkita son orqali kiradi: ti lar yigʻindisi va en. Aprior taqsimot ham goʻyo koʻrilgan ti lar yigʻindisini va goʻyo koʻrilgan en ni saqlasa, yangilash shunchaki ularga qoʻshishdan iborat. Aposterior taqsimot esa oʻsha oilada qoladi.**
   *The data enters through exactly two numbers: the sum of the T's and n. If the prior also stores a pretend sum of T's and a pretend n, updating is just adding to them. And the posterior stays in the same family.*
   ▸ two counters: pretend Σ T + real Σ T, pretend n + real n
4. **Demak, «aprior taqsimot en ta kuzatuvga teng» degan gap oʻxshatish emas, tom maʼnodagi gap edi. Beta sakkiz, ikki oʻnta tongdan sakkizta muvaffaqiyatni saqlaydi. Oʻttiz tongdagi yigirma ikkita oʻz vaqtida kelish shunchaki qoʻshiladi: Beta oʻttiz, oʻn, oʻrtachasi nol butun yuzdan yetmish besh.**
   *So "a prior is worth n observations" was not an analogy; it was literal. Beta eight, two stores eight successes out of ten mornings. The twenty-two on-time arrivals in thirty mornings simply add: Beta thirty, ten, with mean zero point seven five.*
   ▸ Beta(8, 2) + 22 on time, 8 late → Beta(30, 10), mean 0.75
5. **Dirixle uchun ham xuddi shunday: toʻrtta buyurtmaga teng aprior taqsimot — nol butun oʻndan sakkiz, ikki va bir butun oʻndan ikki. Unga qirqta buyurtmadagi yetti, yigirma bir va oʻn ikki sanoqlari qoʻshiladi: yetti butun oʻndan sakkiz, yigirma uch va oʻn uch butun oʻndan ikki.**
   *The Dirichlet works just the same: a prior worth four orders, zero point eight, two and one point two. The counts seven, twenty-one and twelve from forty orders are added to it: seven point eight, twenty-three and thirteen point two.*
   ▸ Dir(0.8, 2, 1.2) + (7, 21, 12) → Dir(7.8, 23, 13.2)
6. **Bekatgacha yoʻldagi Gauss misolida ham shunday edi: aprior taxmin bitta oʻlchovga teng edi va toʻrtta oʻlchov yoniga beshinchi boʻlib qoʻshildi. Uchta misol, bitta qoida: goʻyo koʻrilgan sanoq qoʻshuv haqiqiy sanoq.**
   *The Gaussian walk to the station was the same: the prior guess was worth one timing, and joined the four timings as a fifth. Three examples, one rule: pretend count plus real count.*
   ▸ three rows: Beta, Dirichlet, Gaussian, each "prior count + data count"
7. **Sunʼiy intellektda shuning uchun tavsiya yoki reklama tizimi millionlab variant uchun aposterior taqsimotni har soniyada yangilay oladi: integral emas, ikkita hisoblagichga qoʻshish.**
   *That is why, in AI, a recommender or ad system can update the posteriors of millions of options every second: not an integral, just adding to two counters.*
8. ⏸ **Keling, oʻzimiz sinab koʻraylik. Videoni toʻxtating. Pishiriq ulushi uchun aprior taqsimotimiz Beta uch, yetti: goʻyo oʻnta buyurtmadan uchtasida pishiriq koʻrgandekmiz. Keyin ikki yuzta buyurtmadan oltmish oltitasida pishiriq boʻldi. Aposterior taqsimot qanday va uning oʻrtachasi qancha?**
   *Let's try it ourselves. Pause the video. Our prior for the pastry share is Beta three, seven: as if we had seen a pastry in three orders out of ten. Then sixty-six of two hundred orders had a pastry. What is the posterior, and what is its mean?*
9. **Uch qoʻshuv oltmish olti va yetti qoʻshuv bir yuz oʻttiz toʻrt: Beta oltmish toʻqqiz, bir yuz qirq bir. Oʻrtachasi — oltmish toʻqqizni ikki yuz oʻnga boʻlamiz: nol butun mingdan uch yuz yigirma toʻqqiz.**
   *Three plus sixty-six and seven plus one hundred thirty-four: Beta sixty-nine, one hundred forty-one. Its mean is sixty-nine divided by two hundred ten: zero point three two nine.*
10. **Agar yigʻindi va en hamma narsani aytsa, berilganlarni saqlash shartmi? Keyingi boʻlimda.**
    *If the sum and n say everything, do we need to keep the data at all? The next section.*

### 10-boʻlim · Section 10 — Berilganlar toʻplami oʻrniga hisoblagich · A counter instead of a dataset
1. **Har qanday baho faqat ti lar yigʻindisi va en dan foydalansa, berilganlarni saqlash shart emas. Yigʻindilarni yuritib boramiz, har bir yozuvni oʻtishi bilan tashlaymiz, va javob butun arxivdan olinadigan javob bilan aynan bir xil boʻladi.**
   *If every estimate uses only the sum of the T's and n, we need not keep the data. We keep running totals, discard each record as it passes, and the answer is identical to the one from the whole archive.*
2. **Bir tekis yozuvni tongma-tong oʻqiylik: yetti, oʻn uch, yigirma va hokazo, oʻninchi tongda ikki yuz buyurtmadan oltmish olti. Qahvaxona berilganlar bazasini emas, ikkita butun sonni saqlaydi. Diski yoʻq sensorda ham xuddi shu usul ishlaydi.**
   *Let's read the steady record morning by morning: seven, thirteen, twenty and so on, until sixty-six out of two hundred on the tenth morning. The coffee shop keeps two integers, not a database. The same trick runs on a sensor with no disk.*
   ▸ two counters ticking morning by morning: 7/20, 13/40, 20/60, …, 66/200
3. **Sunʼiy intellektda federativ oʻqitish shu faktga tayanadi: qurilma yozuvlarning oʻzini emas, ti lar yigʻindisi va en ni yuboradi. «Bitta katta kun» yozuvining birinchi besh tongi bitta qurilmada, oxirgi beshtasi boshqasida boʻlsin. Biri yuzdan oʻttiz beshni, ikkinchisi yuzdan oʻttiz birni yuboradi. Server ularni qoʻshib, ikki yuzdan oltmish oltini oladi — nol butun yuzdan oʻttiz uch, hech narsa yoʻqotmasdan.**
   *In AI, federated learning rests on this fact: a device sends the sum of the T's and n instead of the records. Let the first five mornings of the "one big day" record sit on one device and the last five on another. One sends thirty-five out of a hundred, the other thirty-one out of a hundred. The server adds them and gets sixty-six out of two hundred, zero point three three, losing nothing.*
   ▸ two devices → server: 35/100 + 31/100 = 66/200 = 0.33
4. **Lekin chegara ham bor: yetarlilik doim maʼlum bir model uchun. Asta-sekin oʻsib boruvchi yozuvga qaraylik: birinchi besh tongda yuzdan oʻn sakkiz, oxirgi beshtasida yuzdan qirq sakkiz. Ulush nol butun yuzdan oʻn sakkizdan nol butun yuzdan qirq sakkizga oʻsgan. Jami oltmish olti buni butunlay yashiradi.**
   *But there is a limit: sufficiency is always for a particular model. Look at the building-up record: eighteen out of a hundred in the first five mornings, forty-eight out of a hundred in the last five. The share grew from zero point one eight to zero point four eight. The total of sixty-six hides that completely.*
   ▸ the building-up record: 0.18 → 0.48, beside one counter showing only 66/200
5. **Bernulli modeli ulush oʻzgarmaydi deb faraz qiladi, shuning uchun uning hisoblagichi siljishni koʻrmaydi. Savol oʻzgarsa — chetga chiqqan qiymatlar, taqsimot siljishi, boshqa oila — kechagi hisoblagichlar unga javob bera olmaydi.**
   *The Bernoulli model assumes the share does not change, so its counter cannot see a shift. Change the question, to outliers, distribution shift or a different family, and yesterday's counters cannot answer it.*
6. **Endi nega sunʼiy intellekt kursida bu oilani oʻrganganimizni yigʻaylik. Birinchidan, u chiqish qatlamini tushuntiradi: sigmoid va softmaks — eta dan ehtimolga qaytish yoʻli, logit esa tabiiy parametrning haqiqiy nomi.**
   *Now let's gather why an AI course teaches this family. First, it explains the output layer: the sigmoid and the softmax are the way back from eta to probabilities, and "logit" is the natural parameter's real name.*
7. **Ikkinchidan, u oʻqitish signalini tushuntiradi: moslash — kutilgan statistikani kuzatilganiga tenglashtirish, gradient esa kuzatilgan minus kutilgan.**
   *Second, it explains the training signal: fitting is matching the expected statistic to the observed one, and the gradient is observed minus expected.*
8. **Uchinchidan, bu umumlashgan chiziqli modelning taʼrifi: eta ni kirishlarning chiziqli funksiyasi bilan bashorat qilamiz va teskari yoʻl bilan qaytamiz. Ayniy bogʻlanish chiziqli regressiyani, logit logistik regressiyani, logarifm esa Puasson regressiyasini beradi. Bitta retsept, uchta tanish usul.**
   *Third, it is the definition of a generalized linear model: we predict eta with a linear function of the inputs and map back. The identity link gives linear regression, the logit gives logistic regression, and the logarithm gives Poisson regression. One recipe, three familiar methods.*
   ▸ η = wᵀx → identity / logit / log → linear, logistic, Poisson regression
9. **Toʻrtinchidan, u variatsion xulosani hisoblab boʻladigan qiladi: taxminiy aposterior taqsimotni shu oila bilan cheklasak, maqsad funksiyasi differensiallash mumkin boʻlgan arifmetikaga aylanadi.**
   *Fourth, it makes variational inference tractable: restrict the approximate posterior to this family, and its objective becomes arithmetic we can differentiate.*
10. **Bu gʻoyalar keyin ham kerak boʻladi. Toʻqqizinchi maʼruzada eng kichik kvadratlar usuli — eta si kirishlarning chiziqli funksiyasi boʻlgan Gauss. Yettinchi maʼruzadagi Kulbak–Leybler divergensiyasi bitta oilaning ikki aʼzosi uchun faqat ey orqali, integralsiz yoziladi. Birinchi moduldagi logistik regressiya — eta si vaznlar karra eks boʻlgan Bernulli, ikkinchi moduldagi variatsion avtokoderlar esa aynan shu oilaga tayanadi.**
    *We will need these ideas again. In Lecture 9, least squares is the Gaussian whose eta is a linear function of the inputs. Lecture 7's Kullback–Leibler divergence between two members of one family is written through A alone, with no integral. Module 1's logistic regression is the Bernoulli with eta equal to the weights times x, and Module 2's variational autoencoders rest on this very family.*
11. ⏸ **Keling, oʻzimiz sinab koʻraylik. Videoni toʻxtating. Bir tekis yozuvning birinchi uch tongida pishiriqli buyurtmalar yetti, olti va yetti. Hisoblagichlar nimani koʻrsatadi va pi bahosi qancha?**
    *Let's try it ourselves. Pause the video. In the steady record's first three mornings, the orders with a pastry were seven, six and seven. What do the counters show, and what is the estimate of p?*
12. **Yigʻindi — yigirma, buyurtmalar — oltmish. Pi bahosi — yigirmani oltmishga boʻlamiz: uchdan bir. Yozuvlarning oʻzi endi kerak emas.**
    *The sum is twenty, the orders sixty. The estimate of p is twenty divided by sixty: one third. The records themselves are no longer needed.*
13. **Keling, maʼruzani yakunlaylik. Taqsimotni eych eks karra e darajasi eta karra ti eks minus ey eta deb yozish mumkin boʻlsa, u eksponensial oilaga kiradi. Bernulli, Puasson, Gauss, kategorial, Beta va Dirixle kiradi, aralashma kirmaydi.**
    *Let's wrap up the lecture. A distribution is in the exponential family if it can be written as h of x times e to the eta T of x minus A of eta. The Bernoulli, Poisson, Gaussian, categorical, Beta and Dirichlet are in it; a mixture is not.*
14. **Bernullining tabiiy parametri — logit, kategorialning teskari yoʻli — softmaks. Ey ning birinchi hosilasi ti ning oʻrtachasini, ikkinchisi dispersiyasini beradi. Maksimal haqiqatga oʻxshashlik esa oʻrtachalarni tenglashtirishdir.**
    *The Bernoulli's natural parameter is the logit, and the categorical's way back is the softmax. The first derivative of A gives the mean of T, the second its variance. And maximum likelihood is matching averages.*
15. **Yetarli statistika — berilganlar teta haqida aytadigan hamma narsa. U qoʻshma aprior taqsimot nega sanash ekanini va nega hisoblagich arxivning oʻrnini bosa olishini tushuntiradi — shu model uchun, boshqasi uchun emas.**
    *A sufficient statistic is everything the data can say about theta. It explains why conjugate updating is counting, and why a running total can replace an archive: for that model, and no other.*
16. **Mana shu bilan sakkizinchi maʼruzamizni tugatamiz. Keyingi maʼruzada korrelyatsiya, regressiya va koʻp oʻlchovli taqsimotlar bilan tanishamiz.**
    *That brings our eighth lecture to an end. In the next lecture we meet correlation, regression and multivariate distributions.*
