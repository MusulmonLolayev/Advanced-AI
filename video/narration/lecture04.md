# Lecture 4 — video narration (draft 1, for approval)

**One video for the whole lecture**, in two parts like the slides: Part 0 (Uzluksiz tasodifiy miqdorlar) = sections
1–5, Part 1 (Normal taqsimot) = sections 6–10. Each section: problem first → concept as the answer → one AI use → a
hands-on pause → the question the next section answers. The coffee shop of Lecture 3 carries on: gaps between
customers, the delivery, the pastry rate, then the bakery's croissants and the hot days.

**Rules applied:** berilganlar (data) / belgilanganlar (labels); "we", never "you" (only *Videoni toʻxtating*);
Latin letters spoken by their English names (eks, ef, en, pi, ey, bi, zed); Greek letters keep theirs (mu, sigma,
lambda, alfa, beta); Euler's e is read «e» as in Uzbek textbooks; numbers spelled for the ear, digits on screen. Screen labels are words only.
**Numbers:** every figure comes from `video/statistics/raw/l04_numbers.json` / `l04_figures.txt`
(`capture_l04.py`, unit-tested in `test_l04.py`). The 20,000 gaps and the 300 trading days are the figure script's
simulations, regenerated from its seeds, and the narration calls them simulated.
**Slide fixed:** the multivariate slide said √31.9 = 5.7 °C; it is 5.65 (the correlation is 0.77 either way).

**Terms to confirm** (new in this lecture): uzluksiz tasodifiy miqdor (continuous random variable) · zichlik,
ehtimollik zichligi funksiyasi (density, pdf) · taqsimot funksiyasi (CDF) · integral · tekis taqsimot (uniform) ·
eksponensial taqsimot (exponential; textbooks also say «koʻrsatkichli») · xotirasizlik xossasi (memoryless
property) · teskari taqsimot funksiyasi (inverse CDF) · Beta taqsimoti · normal taqsimot, Gauss taqsimoti
(normal, Gaussian) · z-qiymat (z-score; spoken «zed-qiymat», the letter by its English name) · oʻrtachalar vektori (mean vector) · kovariatsiya, kovariatsiya
matritsasi (covariance, covariance matrix) · korrelyatsiya (correlation) · ellips (ellipse) · bosh komponentalar
tahlili (PCA) · Gauss aralashmasi modeli (GMM) · paketli normallashtirish (batch normalization) · diffuziya modeli
(diffusion model).

Format per line: **UZ** (your voice) · *EN* (English track) · ▸ visual.

---

## Lecture opening
▸ title card "4-maʼruza" → the two parts
0. **Assalomu alaykum, aziz doʻstlar. Toʻrtinchi maʼruzamizga xush kelibsiz. Bu maʼruza ham ikki qismdan iborat. Nolinchi qismda uzluksiz tasodifiy miqdorlarni oʻrganamiz, birinchi qismda esa normal taqsimot bilan tanishamiz.**
   *Hello, dear friends, and welcome to our fourth lecture. It also has two parts. In part zero we study continuous random variables, and in part one we meet the normal distribution.*

## Part 0 — Uzluksiz tasodifiy miqdorlar
▸ part card "0-qism · Uzluksiz tasodifiy miqdorlar"

### 1-boʻlim · Section 1 — Zichlik · Density
1. **Uchinchi maʼruzada tasodifiy miqdorning qiymatlarini sanab chiqdik. Endi qahvaxonaga ketma-ket kirgan ikki mijoz orasidagi vaqtni olaylik.**
   *In the third lecture we listed the values a random variable could take. Now take the time between two customers walking into the coffee shop.*
   ▸ a timeline; customers arrive as dots; the gap between two of them is measured
2. **Ikki va uch daqiqa orasida ham cheksiz koʻp javob bor: ikki butun oʻndan besh, ikki butun yuzdan ellik bir va hokazo. Ularni sanab chiqib boʻlmaydi. Bunday miqdorni uzluksiz deymiz.**
   *Between two and three minutes there are already infinitely many answers: two point five, two point five one, and so on. They cannot be listed. We call such a variable continuous.*
3. **Agar cheksiz koʻp qiymatning har biri noldan katta ehtimolga ega boʻlsa, yigʻindi birdan oshib ketardi. Shuning uchun aynan ikki butun oʻndan besh daqiqa chiqish ehtimoli nolga teng. Hech qaysi sekundomer aynan shu sonni koʻrsatmaydi.**
   *If each of infinitely many values had a probability above zero, the total would exceed one. So the chance of exactly two point five minutes is zero. No stopwatch ever reads exactly that.*
   ▸ P(X = 2.5) = 0
4. **Yechim: bitta qiymat emas, oraliq haqida soʻraymiz. Ikki va uch daqiqa orasida boʻlish ehtimoli — oddiy son.**
   *The fix: we stop asking about single values and ask about ranges. The chance of a gap between two and three minutes is a perfectly good number.*
5. **Yigirma ming tanaffusni simulyatsiya qildik va birinchi maʼruzadagidek gistogramma chizdik. Faqat vertikal oʻqni shunday tanladikki, ustunlarning umumiy yuzi bir boʻlsin.**
   *We simulated twenty thousand gaps and drew the histogram of the first lecture. Only the vertical axis is rescaled so that the total area of the bars is one.*
   ▸ the histogram with bins 2 minutes wide: six bars
6. **Ustunlar ikki daqiqalik boʻlsa, oltita ustun chiqadi. Chorak daqiqalik boʻlsa — qirq sakkizta. Ustunlarni toraytirib borsak, ularning uchlari silliq egri chiziqqa aylanadi. Bu egri chiziqni zichlik deymiz.**
   *With bins two minutes wide there are six bars. A quarter of a minute wide, forty-eight. Keep narrowing them, and the bar tops turn into a smooth curve. That curve is the density.*
   ▸ the bins narrow to 0.25 minutes; the curve f(x) = 0.4 e^(−0.4x) draws over the bar tops
7. **Ehtimollik zichligi funksiyasi ehtimolni yuz sifatida beradi: ey va bi orasida boʻlish ehtimoli — egri chiziq ostidagi shu oraliqdagi yuz. Butun yuz esa bir.**
   *A probability density function gives probability as area: the chance of landing between a and b is the area under the curve over that range. The whole area is one.*
   ▸ P(a < X < b) = ∫ f(x) dx over [a, b]; the area shaded
8. **Integral belgisi — uchinchi maʼruzadagi yigʻindi belgisining oʻzi, faqat ustunlari cheksiz ingichka: yuzlarni qoʻshib chiqamiz.**
   *The integral sign is the sum sign of the third lecture with the bars made infinitely thin: we add up the area.*
9. **Zichlik ehtimol emas va birdan katta boʻlishi ham mumkin. U bir daqiqaga toʻgʻri keladigan ehtimol, xuddi tezlik bir soatga toʻgʻri keladigan masofa boʻlgani kabi.**
   *A density is not a probability, and it can be larger than one. It is probability per minute, the way speed is distance per hour.*
10. **Sunʼiy intellektda rasm yoki matn yaratadigan modellar aynan zichlikni oʻrganadi: qanday berilganlar koʻp uchrashini, qandayi kam uchrashini.**
    *In AI, models that generate images or text learn exactly this: a density, saying which data is common and which is rare.*
11. ⏸ **Keling, oʻzimiz sinab koʻraylik. Videoni toʻxtating. Yetkazib berish oʻttiz soniyalik oynaning istalgan paytida bir xil ehtimol bilan keladi. Bir daqiqaga toʻgʻri keladigan zichlik qancha?**
    *Let's try it ourselves. Pause the video. A delivery lands anywhere in a thirty-second window, every moment equally likely. What is its density per minute?*
12. **Oyna yarim daqiqa, yuz bir boʻlishi kerak. Demak, balandlik ikki: bir daqiqaga ikki. Zichlik birdan katta, lekin hech qanday ehtimol birdan oshmadi.**
    *The window is half a minute and the area must be one. So the height is two: two per minute. The density is above one, yet no probability exceeded one.*
13. **Yuzni har safar hisoblash noqulay. Uni bir marta yigʻib qoʻysak-chi? Keyingi boʻlimda.**
    *Computing an area every time is awkward. What if we add it up once and keep it? The next section.*

### 2-boʻlim · Section 2 — Taqsimot funksiyasi · The CDF
1. **Uchinchi maʼruzada oʻn daqiqada oʻrtacha toʻrtta mijoz kelardi. Demak, mijozlar orasidagi oʻrtacha tanaffus ikki butun oʻndan besh daqiqa, uning zichligi esa nol butun oʻndan toʻrt karra e ning minus nol butun oʻndan toʻrt eks darajasi.**
   *In the third lecture, four customers arrived per ten minutes on average. So the average gap is two point five minutes, and its density is zero point four times e to the minus zero point four x.*
   ▸ f(x) = 0.4 e^(−0.4x)
2. **Keyingi mijoz ikki daqiqa ichida keladimi? Noldan ikkigacha boʻlgan yuzni boʻyaymiz: nol butun yuzdan ellik besh.**
   *Will the next customer arrive within two minutes? We shade the area from zero to two: zero point five five.*
   ▸ the area from 0 to 2 fills; P(X < 2) = 1 − e^(−0.8) = 0.55
3. **Endi shu yuzni chapdan oʻngga yurib yigʻib boramiz. Hosil boʻlgan egri chiziq ikki nuqtada xuddi nol butun yuzdan ellik beshga teng. Bu taqsimot funksiyasi: eks dan oshmaslik ehtimoli.**
   *Now we gather that area as we sweep from left to right. The curve we get stands at exactly zero point five five at two. This is the cumulative distribution function: the chance of being at most x.*
   ▸ the lower panel: F(x) rises from 0 to 1; at x = 2 it reads 0.55
4. **Taqsimot funksiyasi noldan boshlanadi, birda tugaydi va hech qachon kamaymaydi. Tanaffuslarning ellik besh foizi ikki daqiqadan qisqa.**
   *The CDF starts at zero, ends at one, and never decreases. Fifty-five percent of gaps are shorter than two minutes.*
5. **Besh daqiqa yoki undan uzun tinch tanaffus ham oʻn uch butun oʻndan besh foiz hollarda boʻladi. Demak, sokinlik tirbandlik tugaganini bildirmaydi.**
   *A quiet stretch of five minutes or more still happens thirteen point five percent of the time. So a lull is no sign the rush is over.*
6. **Har qanday oraliq savoli — ikki qiymatni oʻqish va ayirish: ey va bi orasida boʻlish ehtimoli bi dagi qiymat minus ey dagi qiymat.**
   *Every range question is two lookups and a subtraction: the chance of landing between a and b is F at b minus F at a.*
   ▸ P(a < X < b) = F(b) − F(a)
7. **Shuning uchun jadvallar va dasturlar zichlikni emas, taqsimot funksiyasini beradi: savollarga aynan u javob beradi.**
   *That is why tables and software report the CDF, not the density: it is the CDF that answers questions.*
8. **Sunʼiy intellektda chegaralar ham shunday tanlanadi: masalan, eng sekin bir foiz soʻrovlar uchun ogohlantirish — taqsimot funksiyasi nol butun yuzdan toʻqson toʻqqizga yetgan nuqta.**
   *In AI, thresholds are chosen the same way: for example, an alert for the slowest one percent of requests sits where the CDF reaches zero point nine nine.*
9. ⏸ **Keling, oʻzimiz sinab koʻraylik. Videoni toʻxtating. Tanaffus ikki va besh daqiqa orasida boʻlish ehtimoli qancha?**
   *Let's try it ourselves. Pause the video. What is the chance that a gap lasts between two and five minutes?*
10. **Beshdagi qiymat nol butun mingdan sakkiz yuz oltmish besh, ikkidagi qiymat nol butun mingdan besh yuz ellik bir. Ayirmasi nol butun mingdan uch yuz oʻn toʻrt — uchdan birdan sal kam.**
    *F at five is zero point eight six five, F at two is zero point five five one. The difference is zero point three one four: just under a third.*
11. **Bu egri chiziq qayerdan keldi va boshqa shakllar ham bormi? Keyingi boʻlimda.**
    *Where did this curve come from, and are there other shapes? The next section.*

### 3-boʻlim · Section 3 — Tekis va eksponensial taqsimot · Uniform and exponential
1. **Eng oddiy shakl — tekis taqsimot: oraliqdagi hech bir qiymat boshqasidan ajralib turmaydi, zichlik tekis.**
   *The simplest shape is the uniform distribution: no value in the range is special, and the density is flat.*
2. **Yetkazib berish «oʻn daqiqa ichida» deb vaʼda qilingan. Zichlik — oʻndan bir. Birinchi uch daqiqada kelish ehtimoli — oʻndan uch.**
   *A delivery is promised "within ten minutes". The density is one tenth. The chance it lands in the first three minutes is three in ten.*
   ▸ a flat line at 0.1 over 0 to 10; the first 3 minutes shaded: 0.3
3. **Ikkinchi shakl — eksponensial taqsimot: hodisalar lambda tezlikda kelganda keyingisigacha kutish vaqti. Oʻrtacha kutish — birni lambdaga boʻlganimiz.**
   *The second shape is the exponential distribution: the wait until the next event, when events arrive at rate lambda. The average wait is one over lambda.*
   ▸ f(x) = λ e^(−λx), mean 1/λ
4. **Ikki shakl qarama-qarshi narsani aytadi: tekisda hech bir lahza alohida emas, eksponensialda esa qisqa kutish doim eng koʻp uchraydi.**
   *The two shapes say opposite things: under the uniform no moment is special; under the exponential, short waits are always the commonest.*
5. **Eksponensial va Puasson — bitta jarayonning ikki koʻrinishi. Puasson oʻn daqiqada nechta mijoz kelishini sanaydi, eksponensial esa ketma-ket ikki mijoz orasidagi vaqtni oʻlchaydi.**
   *The exponential and the Poisson are two views of one process. The Poisson counts how many customers arrive in ten minutes; the exponential measures the time between consecutive arrivals.*
   ▸ the same timeline: counts per window above, gaps between dots below
6. **Uch daqiqa kutdik va hech kim kelmadi. Yana ikki daqiqadan koʻp kutish ehtimoli qancha? Nol butun mingdan toʻrt yuz qirq toʻqqiz — kutishni endi boshlagandagi bilan aynan bir xil.**
   *We have waited three minutes and nobody came. What is the chance of waiting more than two minutes longer? Zero point four four nine: exactly the same as when we started.*
   ▸ P(X > 5 | X > 3) = e^(−2)/e^(−1.2) = e^(−0.8) = 0.449 = P(X > 2)
7. **Buni xotirasizlik xossasi deymiz: navbat sokin oʻtgan vaqtni eslamaydi. Uchinchi maʼruzadagi Puasson ham aynan shunday mustaqillikni faraz qilgan edi.**
   *We call this the memoryless property: the queue does not remember the quiet stretch. The Poisson of the third lecture assumed exactly this independence.*
8. **Lekin bu dunyo haqida kuchli daʼvo. Haqiqatda tushlik paytida mijozlar toʻda boʻlib keladi, va unda ikkala model ham toʻgʻri kelmaydi.**
   *But that is a strong claim about the world. Real customers cluster at lunchtime, and then neither model fits.*
9. **Sunʼiy intellektda bu farazni tekshirish muhim: model serveriga soʻrovlar toʻlqin-toʻlqin kelsa, eksponensial faraz bilan rejalashtirilgan quvvat yetmaydi.**
   *In AI it pays to check this assumption: if requests reach a model server in waves, capacity planned on the exponential assumption falls short.*
10. ⏸ **Keling, oʻzimiz sinab koʻraylik. Videoni toʻxtating. «Oʻn daqiqa ichida» vaʼda qilingan yetkazib berish oxirgi ikki daqiqada kelish ehtimoli qancha?**
    *Let's try it ourselves. Pause the video. A delivery promised "within ten minutes": what is the chance it lands in the last two minutes?*
11. **Oʻndan ikki, yaʼni nol butun oʻndan ikki. Tekis taqsimotda faqat oraliqning uzunligi muhim.**
    *Two in ten: zero point two. Under the uniform, only the length of the range matters.*
12. **Kompyuter shunday tasodifiy sonlarni qanday yaratadi? Keyingi boʻlimda.**
    *How does a computer produce random numbers like these? The next section.*

### 4-boʻlim · Section 4 — Tasodifiy son qayerdan keladi · Where random numbers come from
1. **Kompyuter faqat bir xil tasodifiylikni bera oladi: nol va bir orasidagi tekis taqsimlangan son. Qolgan hamma narsa shundan quriladi.**
   *A computer can produce only one kind of randomness: a uniform number between zero and one. Everything else is built from it.*
   ▸ uniform draws u fall into [0, 1]
2. **Usul shunday: taqsimot funksiyasini teskari yuritamiz. Tekis son yu ni olamiz va taqsimot funksiyasi aynan yu ga teng boʻladigan eks ni topamiz.**
   *The method: we run the CDF backwards. We take a uniform number u and find the x at which the CDF equals u.*
   ▸ u on the vertical axis of F(x); a line across to the curve, then down to x
3. **Eksponensial uchun javob: eks teng minus logarifm bir minus yu, boʻlinsin lambda.**
   *For the exponential, the answer is: x equals minus the logarithm of one minus u, divided by lambda.*
   ▸ x = −ln(1 − u) / λ
4. **Yu nol butun oʻndan besh, lambda nol butun oʻndan toʻrt boʻlsa, eks bir butun yuzdan yetmish uch daqiqa. Haqiqatan ham, simulyatsiyadagi tanaffuslarning yarmi bundan qisqa.**
   *With u equal to zero point five and lambda zero point four, x is one point seven three minutes. And indeed, half of the simulated gaps are shorter than that.*
5. **Koʻp tekis sonni shu formuladan oʻtkazsak, ularning gistogrammasi eksponensial egri chiziqqa aylanadi.**
   *Pass many uniform numbers through this formula, and their histogram becomes the exponential curve.*
   ▸ a stream of u values maps to x values; their histogram grows into the curve
6. **Sunʼiy intellektda tanlab olish aynan shunday boshlanadi: dropout niqoblari, mini-paketlarni aralashtirish, berilganlarni koʻpaytirish va diffuziya modelining har qadamida qoʻshiladigan shovqin — hammasi tekis sondan boshlanadi.**
   *In AI, this is how sampling actually starts: dropout masks, shuffled mini-batches, data augmentation, and the noise a diffusion model adds at every step all begin as uniform numbers.*
7. ⏸ **Keling, oʻzimiz sinab koʻraylik. Videoni toʻxtating. Yu nol butun oʻndan toʻqqiz boʻlsa, qanday tanaffus chiqadi?**
   *Let's try it ourselves. Pause the video. If u is zero point nine, what gap comes out?*
8. **Minus logarifm nol butun oʻndan bir, boʻlinsin nol butun oʻndan toʻrt: besh butun yuzdan yetmish olti daqiqa. Katta yu uzun tanaffus beradi.**
   *Minus the logarithm of zero point one, divided by zero point four: five point seven six minutes. A large u gives a long gap.*
9. **Hozirgacha pishiriq olish ehtimolini nol butun oʻndan uch deb oldik. Bu son qayerdan keldi va unga qanchalik ishonamiz? Keyingi boʻlimda.**
   *So far we took the chance of buying a pastry to be zero point three. Where did that number come from, and how sure are we? The next section.*

### 5-boʻlim · Section 5 — Beta taqsimoti · The Beta distribution
1. **Uchinchi maʼruza Dirixle taqsimoti bilan tugadi: koʻp ulushlar ustidagi taqsimot. Ikki javobli holat oʻz nomiga ega.**
   *The third lecture ended with the Dirichlet: a distribution over many shares. The two-answer case has its own name.*
2. **Savol: mijozlarning qancha ulushi pishiriq oladi? Dastlabki oʻnta buyurtmaning uchtasida pishiriq bor edi. Toʻgʻridan-toʻgʻri oʻqisak, nol butun oʻndan uch. Lekin oʻnta buyurtmada nol butun oʻndan ikki yoki nol butun yuzdan qirq besh chiqsa ham ajablanmaymiz.**
   *The question: what share of customers buy a pastry? Three of the first ten orders had one. Read literally, that is zero point three. But on ten orders, zero point two or zero point four five would hardly surprise us.*
3. **Demak, ulushning oʻzi noldan birgacha boʻlgan nomaʼlum son, va bizga aynan shu oraliqdagi zichlik kerak. Bu Beta taqsimoti.**
   *So the share itself is an unknown number between zero and one, and we need a density over exactly that range. That is the Beta distribution.*
4. **Dirixle kabi, alfa va beta muvaffaqiyat va muvaffaqiyatsizliklarni sanaydi. Oʻntadan uchta — Beta toʻrt, sakkiz: oʻrtacha nol butun yuzdan oʻttiz uch, tarqoqligi nol butun yuzdan oʻn uch.**
   *Like the Dirichlet, alpha and beta count successes and failures. Three of ten gives Beta four, eight: mean zero point three three, spread zero point one three.*
   ▸ the Beta(4, 8) curve, wide
5. **Yuztadan oʻttizta — Beta oʻttiz bir, yetmish bir: oʻrtacha nol butun yuzdan oʻttiz, tarqoqligi bor-yoʻgʻi nol butun yuzdan besh. Berilganlar koʻpaygan sari egri chiziq toraydi.**
   *Thirty of a hundred gives Beta thirty-one, seventy-one: mean zero point three zero, spread only zero point zero five. The more data, the narrower the curve.*
   ▸ the Beta(31, 71) curve, narrow, over the same axis
6. **Yangilash — bu sanash: yana bitta pishiriq olinsa, alfaga bir qoʻshamiz.**
   *Updating is counting: one more pastry, and we add one to alpha.*
7. **Sunʼiy intellektda bosish ulushi yoki model aniqligi dalil kelgan sari shunday kuzatiladi: oʻn beshtadan oʻn ikkita toʻgʻri javob mingtadan sakkiz yuztasi bilan bir xil dalil emas. Oltinchi maʼruzada Beta Bernulli uchun aprior taqsimot boʻladi.**
   *In AI, a click rate or a model's accuracy is tracked this way as evidence arrives: twelve correct of fifteen is not the evidence that eight hundred of a thousand is. In Lecture 6, the Beta becomes the prior for a Bernoulli.*
   ▸ two Beta curves: 12 of 15 wide, 800 of 1000 a spike
8. ⏸ **Keling, oʻzimiz sinab koʻraylik. Videoni toʻxtating. Beta toʻrt, sakkizdan keyin navbatdagi buyurtmada pishiriq bor. Yangi taqsimot qanday va uning oʻrtachasi qancha?**
   *Let's try it ourselves. Pause the video. After Beta four, eight, the next order has a pastry. What is the new distribution, and what is its mean?*
9. **Beta besh, sakkiz. Oʻrtacha — beshni oʻn uchga boʻlamiz: taxminan nol butun yuzdan oʻttiz sakkiz.**
   *Beta five, eight. The mean is five divided by thirteen: about zero point three eight.*
10. **Mana shu bilan nolinchi qismni tugatamiz. Bitta shakl esa hamma joyda uchraydi: qoʻngʻiroqsimon egri chiziq. Birinchi qismda u bilan tanishamiz.**
    *That completes part zero. One shape turns up everywhere: the bell curve. In part one we meet it.*

## Part 1 — Normal taqsimot
▸ part card "1-qism · Normal taqsimot"

### 6-boʻlim · Section 6 — Normal taqsimot · The normal distribution
1. **Kruassanlarni tortamiz, odamlarning boʻyini oʻlchaymiz, termometrni ikki marta oʻqiymiz — har safar bir xil qoʻngʻiroqsimon shakl chiqadi.**
   *Weigh croissants, measure people's heights, read a thermometer twice: the same bell shape appears every time.*
2. **Sababi bitta: koʻp kichik mustaqil tebranishlarning yigʻindisi normal taqsimotga keladi. Kruassanning vazni — xamir boʻlagi, unning namligi, pechdagi joyi, koʻpchish vaqti va yana oʻnlab omillar yigʻindisi.**
   *The reason fits in one line: anything built by adding up many small independent wobbles ends up normal. A croissant's weight is the dough portion, plus the flour's moisture, plus its place in the oven, plus the rise time, plus a dozen others.*
3. **Bu markaziy limit teoremasi, uni beshinchi maʼruzada isbotlaymiz. Hozircha natijasini olamiz: yigʻindi va oʻrtachalar shu shaklga intiladi.**
   *That is the Central Limit Theorem, and we prove it in Lecture 5. For now we take its consequence: sums and averages drift toward this shape.*
4. **Normal taqsimotning ikki parametri bor: mu egri chiziqni yonga suradi, sigma uni choʻzadi. Novvoyxonadagi kruassanlar uchun mu oltmish gramm, sigma ikki gramm.**
   *The normal distribution has two parameters: mu slides the curve sideways, sigma stretches it. For the bakery's croissants, mu is sixty grams and sigma two grams.*
   ▸ the bell curve over grams; μ and σ marked
5. **Formulani qoʻlda hech qachon ishlatmaymiz, uning oddiy integrali yoʻq. Bizga undan kelib chiqadigan qoida kerak.**
   *We never need the formula by hand; it has no simple integral. What we need is the rule that follows from it.*
6. **Oltmish sakkiz, toʻqson besh, toʻqson toʻqqiz butun oʻndan yetti qoidasi: kruassanlarning taxminan oltmish sakkiz foizi oʻrtachadan bir sigma ichida, toʻqson besh foizi ikki sigma ichida, toʻqson toʻqqiz butun oʻndan yetti foizi uch sigma ichida.**
   *The sixty-eight, ninety-five, ninety-nine point seven rule: about sixty-eight percent of croissants lie within one sigma of the mean, ninety-five percent within two, and ninety-nine point seven percent within three.*
   ▸ the bands fill in turn: 68.27 %, 95.45 %, 99.73 %
7. **Grammlarda: oltmish sakkiz foizi ellik sakkiz va oltmish ikki gramm orasida, toʻqson besh foizi ellik olti va oltmish toʻrt orasida, deyarli hammasi ellik toʻrt va oltmish olti orasida.**
   *In grams: sixty-eight percent weigh between fifty-eight and sixty-two, ninety-five percent between fifty-six and sixty-four, and nearly all between fifty-four and sixty-six.*
8. **Demak, ikki son — markaz va tarqoqlik — butun partiya haqidagi deyarli har qanday savolga javob beradi.**
   *So two numbers, a centre and a spread, answer almost any question about the whole batch.*
9. **Sunʼiy intellektda modelning xatolari koʻpincha normal deb faraz qilinadi. Regressiyadagi kvadrat xato aynan shu farazdan kelib chiqadi, buni beshinchi maʼruzada koʻramiz.**
   *In AI, a model's errors are often assumed to be normal. The squared error of regression comes straight from that assumption, as we will see in Lecture 5.*
10. ⏸ **Keling, oʻzimiz sinab koʻraylik. Videoni toʻxtating. Kruassanlarning toʻqson besh foizi qaysi ikki vazn orasida?**
    *Let's try it ourselves. Pause the video. Between which two weights do ninety-five percent of the croissants lie?*
11. **Oltmishdan ikki sigma, yaʼni toʻrt gramm pastga va yuqoriga: ellik olti va oltmish toʻrt gramm.**
    *Two sigma, four grams, either side of sixty: fifty-six and sixty-four grams.*
12. **Yorliqda esa «kamida ellik besh gramm» deb yozilgan. Bu vaʼda qanchalik tez-tez buziladi? Keyingi boʻlimda.**
    *The label, though, promises "fifty-five grams or more". How often is that promise broken? The next section.*

### 7-boʻlim · Section 7 — Yorliqdagi vaʼda · The label's promise
1. **Ellik besh gramm oʻrtachadan ikki butun oʻndan besh sigma pastda.**
   *Fifty-five grams sits two point five sigma below the mean.*
   ▸ a line at 55 g; the distance 2.5σ marked
2. **Uning chap tomonidagi yuz nol butun yuzdan oltmish ikki foiz: har ming kruassandan taxminan oltitasi vaʼdadan yengil chiqadi.**
   *The area to its left is zero point six two percent: about six croissants in every thousand come out lighter than promised.*
   ▸ the left tail shaded; 1000 croissants, 6 of them lit
3. **Endi oʻrtachani oʻzgartirmaymiz, faqat jarayonni aniqroq qilamiz: sigma bir butun oʻndan besh gramm boʻlsin.**
   *Now we leave the mean alone and only make the process more precise: sigma becomes one point five grams.*
4. **Unda ellik besh gramm uch butun oʻndan uch sigma uzoqda boʻladi, va kamchilik keskin kamayadi.**
   *Then fifty-five grams is three point three sigma away, and the shortfall falls sharply.*
   ▸ the curve narrows; the tail almost vanishes
5. **Xatolar ulushini oʻrtacha emas, tarqoqlik hal qiladi. Bu birinchi maʼruzadagi shisha toʻldirish liniyasining saboqi, endi uning ortida formula bor.**
   *Spread, not the average, decides the failure rate. That is the lesson of the first lecture's bottling line, now with a formula behind it.*
6. **Sunʼiy intellektda gʻayrioddiy holatlarni topish ham shunday: uch sigmadan uzoq qiymat signal beradi. Normal berilganlarda bunday qiymat mingtadan atigi uchtasida uchraydi.**
   *In AI, anomaly detection works the same way: a value more than three sigma away raises an alert. On normal data, that happens to only three readings in a thousand.*
7. ⏸ **Keling, oʻzimiz sinab koʻraylik. Videoni toʻxtating. Sigma bir butun oʻndan besh gramm boʻlsa, oʻn ming kruassandan nechtasi ellik besh grammdan yengil chiqadi?**
   *Let's try it ourselves. Pause the video. With sigma one point five grams, how many of ten thousand croissants come out lighter than fifty-five grams?*
8. **Uch butun oʻndan uch sigma chap tomondagi yuz: oʻn ming kruassandan taxminan toʻrttasi. Ilgari oltmish ikkita edi.**
   *The area beyond three point three sigma: about four in ten thousand. Before, it was sixty-two.*
9. **Kruassan va nonni qanday solishtiramiz? Ularning grammlari turlicha. Keyingi boʻlimda.**
   *How do we compare a croissant with a loaf, when their grams are so different? The next section.*

### 8-boʻlim · Section 8 — Z-qiymat · z-scores
1. **Oʻlchovning zed-qiymati — u oʻrtachadan nechta standart chetlanish uzoqda ekani: oʻrtachani ayiramiz va sigmaga boʻlamiz. Uning birligi yoʻq, shuning uchun gramm ham, daqiqa ham solishtiriladigan boʻladi.**
   *The z-score of a measurement is how many standard deviations it sits from the mean: subtract the mean and divide by sigma. It has no units, so grams and minutes become comparable.*
   ▸ z = (x − μ) / σ
2. **Ellik yetti grammli kruassan: minus uchni ikkiga boʻlamiz, minus bir butun oʻndan besh. Bir yarim standart chetlanish yengil.**
   *A fifty-seven-gram croissant: minus three divided by two, minus one point five. One and a half standard deviations light.*
3. **Bir kuni ertalab kruassan ellik yetti gramm, non esa toʻrt yuz sakson gramm chiqdi. Nonlar oʻrtacha besh yuz gramm, sigmasi oʻn besh gramm.**
   *One morning a croissant came out at fifty-seven grams and a loaf at four hundred and eighty. Loaves average five hundred grams, with sigma fifteen.*
4. **Non yigirma gramm, kruassan esa atigi uch gramm yengil. Lekin nonning zed-qiymati minus bir butun yuzdan oʻttiz uch, kruassanniki minus bir butun oʻndan besh.**
   *The loaf is twenty grams light and the croissant only three. Yet the loaf's z-score is minus one point three three, and the croissant's minus one point five.*
   ▸ the two curves on one z axis: −1.5 and −1.33
5. **Demak, gʻayrioddiyroq pishiriq — kruassan: kruassanlarning olti butun oʻndan yetti foizi shunchalik yengil chiqadi, nonlarning esa toʻqqiz butun oʻndan bir foizi. Xom farq chalgʻitadi, zed-qiymat esa yoʻq.**
   *So the more unusual bake is the croissant: six point seven percent of croissants come out that light, against nine point one percent of loaves. Raw differences mislead; z-scores do not.*
6. **Jadvalning har bir ustuniga shuni qilsak, buni standartlashtirish deymiz.**
   *Doing this to every column of a table is called standardizing.*
7. **Sunʼiy intellektda eng yaqin qoʻshnilar usuli masofani oʻlchaydi: grammdagi va kilogrammdagi ustunlar ming marta farqli hisoblanardi. Standartlashtirsak, bunday boʻlmaydi. Tarmoq ichida esa paketli normallashtirish har bir faollashuvning zed-qiymatini oladi.**
   *In AI, k nearest neighbours measures distances, so a column in grams and a column in kilograms would count a thousand times differently. Standardize first, and they do not. Inside a network, batch normalization takes the z-score of every activation.*
8. ⏸ **Keling, oʻzimiz sinab koʻraylik. Videoni toʻxtating. Oltmish uch grammli kruassanning zed-qiymati qancha?**
   *Let's try it ourselves. Pause the video. What is the z-score of a sixty-three-gram croissant?*
9. **Uchni ikkiga boʻlamiz: plyus bir butun oʻndan besh. Bir yarim standart chetlanish ogʻir.**
   *Three divided by two: plus one point five. One and a half standard deviations heavy.*
10. **Haqiqiy yozuvlarda esa sonlar bittadan emas, toʻda boʻlib keladi. Ularni birgalikda qanday tasvirlaymiz? Keyingi boʻlimda.**
    *Real records, though, come in bundles, not one number at a time. How do we describe them together? The next section.*

### 9-boʻlim · Section 9 — Koʻp oʻlchovli normal taqsimot · The multivariate Gaussian
1. **Har bir ish kunida qahvaxona havo haroratini va sotilgan muzli qahvalar sonini yozib boradi. Bu ikkisi bir-biriga bogʻliq: issiq kunlarda koʻproq sotiladi.**
   *Each trading day the shop records the high temperature and the iced coffees sold. The two are plainly linked: warm days sell more.*
   ▸ a scatter of the 300 simulated days: temperature against cups
2. **Ularni alohida tasvirlasak, eng muhimini yoʻqotamiz. Bizga birga oʻzgarishni oʻlchaydigan son kerak. Bu kovariatsiya.**
   *Describing them separately throws away the very thing worth knowing. We need a number for moving together. That number is the covariance.*
3. **Koʻp oʻlchovli normal taqsimotda mu oʻrniga oʻrtachalar vektori, sigma kvadrat oʻrniga kovariatsiya matritsasi turadi. Diagonalda har bir miqdorning dispersiyasi, diagonaldan tashqarida esa ularning kovariatsiyasi.**
   *A multivariate Gaussian replaces mu with a mean vector and sigma squared with a covariance matrix. On the diagonal sits each quantity's variance; off the diagonal, their covariance.*
   ▸ μ = (21.8, 39.5), Σ = [[31.9, 49.6], [49.6, 128.4]]
4. **Uch yuz kunlik simulyatsiyada oʻrtacha harorat yigirma bir butun oʻndan sakkiz daraja, oʻrtacha savdo oʻttiz toʻqqiz butun oʻndan besh stakan.**
   *Over the three hundred simulated days, the mean temperature is twenty-one point eight degrees and mean sales thirty-nine point five cups.*
5. **Harorat besh butun yuzdan oltmish besh daraja, savdo oʻn bir butun yuzdan oʻttiz uch stakan tarqoqlikka ega. Kovariatsiya qirq toʻqqiz butun oʻndan olti — musbat: issiq kunlarda koʻproq sotiladi. Ikki tarqoqlikka boʻlsak, korrelyatsiya chiqadi: nol butun yuzdan yetmish yetti.**
   *Temperature spreads by five point six five degrees, sales by eleven point three three cups. The covariance, forty-nine point six, is positive: warm days sell more. Dividing out both spreads gives the correlation: zero point seven seven.*
6. **Ellipslar — bir va ikki sigma konturlari. Ularning ogʻishi — kovariatsiya: nol boʻlsa oʻqlarga parallel, musbat boʻlsa yuqoriga qiyshaygan, korrelyatsiya kuchli boʻlsa ingichka.**
   *The ellipses are the one- and two-sigma contours. Their tilt is the covariance: zero lines them up with the axes, positive tips them upward, and a stronger correlation makes them thinner.*
   ▸ the 1σ and 2σ ellipses draw over the scatter
7. **Mana bu kun: yigirma sakkiz daraja, lekin atigi yigirma besh stakan. Harorat atigi bir butun oʻndan bir sigma issiq, savdo bir butun oʻndan uch sigma kam. Alohida qarasak, ikkalasi ham oddiy.**
   *Look at this day: twenty-eight degrees, but only twenty-five cups. The temperature is only one point one sigma warm, and sales one point three sigma light. Taken one at a time, both look ordinary.*
   ▸ the starred day, outside the 2σ ellipse
8. **Lekin juftlik sifatida u uch butun oʻndan besh standart chetlanish uzoqda — ellipsdan ancha tashqarida. Har bir ustunni alohida tekshirsak, buni koʻrmay qolardik.**
   *But as a pair it sits three point five standard deviations out, well outside the ellipse. Checking each column alone, we would have missed it.*
9. **Sunʼiy intellektda gʻayrioddiy holatni aniqlash tizimlari aynan shu ellipsga qaraydi, alohida ustunlarga emas.**
   *In AI, anomaly detectors look at exactly this ellipse, not at the columns one at a time.*
10. ⏸ **Keling, oʻzimiz sinab koʻraylik. Videoni toʻxtating. Yigirma sakkiz daraja oʻrtachadan nechta standart chetlanish issiq?**
    *Let's try it ourselves. Pause the video. How many standard deviations above the mean is twenty-eight degrees?*
11. **Yigirma sakkizdan yigirma bir butun oʻndan sakkizni ayirib, besh butun yuzdan oltmish beshga boʻlamiz: taxminan bir butun oʻndan bir.**
    *Twenty-eight minus twenty-one point eight, divided by five point six five: about one point one.*
12. **Nega sunʼiy intellekt kursi bitta egri chiziqqa butun maʼruzani bagʻishlaydi? Keyingi boʻlimda.**
    *Why does an AI course spend a whole lecture on one curve? The next section.*

### 10-boʻlim · Section 10 — Normal taqsimot sunʼiy intellektda · The Gaussian in AI
1. **Birinchidan, ellipsning uzun oʻqi — bosh komponentalar tahlili topadigan yoʻnalishning oʻzi. U kovariatsiya matritsasini diagonallashtiradi, va ellipsning oʻqlari uning bosh yoʻnalishlari.**
   *First, the long axis of that ellipse is what PCA finds. PCA diagonalizes the covariance matrix, and the ellipse's axes are its principal directions.*
   ▸ the ellipse's two axes drawn from the covariance matrix
2. **Ikkinchidan, klasterlash: Gauss aralashmasi modeli berilganlarni bir nechta shunday ellipslar bilan tasvirlaydi, har bir klasterga bittadan.**
   *Second, clustering: a Gaussian mixture model describes data as several such ellipses, one per cluster.*
3. **Uchinchidan, tarmoqni boshlash: vaznlar nol oʻrtachali normal taqsimotdan olinadi, sigmasi qatlam kengligiga qarab tanlanadi, shunda signallar yoʻqolib ham, portlab ham ketmaydi.**
   *Third, starting a network: weights are drawn from a normal distribution with mean zero, its sigma set by the layer width, so that signals neither vanish nor explode.*
4. **Toʻrtinchidan, regulyarizatsiya: vaznlar normal taqsimotdan kelgan deb faraz qilsak, eng ehtimolli vaznlar aynan el ikki jarimasini beradi. Buni oltinchi maʼruzada keltirib chiqaramiz.**
   *Fourth, regularization: assume the weights come from a normal distribution, and the most probable weights give exactly the L2 penalty. We derive it in Lecture 6.*
5. **Beshinchidan, generativ modellar: variatsion avtokodlovchining yashirin oʻzgaruvchisi koʻp oʻlchovli normal taqsimot, diffuziya modeli esa qadam-baqadam normal shovqin qoʻshadi.**
   *Fifth, generative models: a variational autoencoder's latent variable is a multivariate Gaussian, and a diffusion model adds normal noise step by step.*
6. ⏸ **Keling, oʻzimiz sinab koʻraylik. Videoni toʻxtating. Vaznlar nol oʻrtachali, sigmasi nol butun oʻndan bir boʻlgan normal taqsimotdan olinsa, ularning qanchasi minus nol butun oʻndan ikki va nol butun oʻndan ikki orasida boʻladi?**
   *Let's try it ourselves. Pause the video. If weights are drawn from a normal distribution with mean zero and sigma zero point one, what share of them lies between minus zero point two and zero point two?*
7. **Bu ikki sigma, demak taxminan toʻqson besh foiz. Oltmish sakkiz, toʻqson besh, toʻqson toʻqqiz butun oʻndan yetti qoidasi bu yerda ham ishlaydi.**
   *That is two sigma, so about ninety-five percent. The sixty-eight, ninety-five, ninety-nine point seven rule works here too.*
8. **Keling, maʼruzani yakunlaylik. Uzluksiz miqdorda har bir aniq qiymatning ehtimoli nol, shuning uchun ehtimolni zichlik tashiydi: oraliqdagi ehtimol — egri chiziq ostidagi yuz, butun yuz esa bir. Taqsimot funksiyasi har qanday oraliq savolini ikki qiymatning ayirmasiga aylantiradi.**
   *Let's wrap up the lecture. A continuous variable gives every exact value probability zero, so probability is carried by a density: the chance of a range is the area under the curve, and the whole area is one. The CDF turns every range question into a difference of two values.*
9. **Tekis taqsimot — hech bir qiymat alohida boʻlmaganda, eksponensial — keyingi hodisagacha kutish, xotirasiz va Puassonning juftligi. Beta — bitta ulush haqidagi ishonch. Normal taqsimot oltmish sakkiz, toʻqson besh, toʻqson toʻqqiz butun oʻndan yetti qoidasiga boʻysunadi, zed-qiymat esa turli oʻlchovlarni solishtirish imkonini beradi. Koʻp oʻlchovda oʻrtachalar vektori va kovariatsiya matritsasi ellipslarni chizadi.**
   *Uniform when no value is special; exponential for the wait until the next event, memoryless and the Poisson's partner. Beta for a belief about one share. The normal distribution follows the sixty-eight, ninety-five, ninety-nine point seven rule, and a z-score makes different scales comparable. In several dimensions, a mean vector and a covariance matrix draw the ellipses.*
10. **Mana shu bilan toʻrtinchi maʼruzamizni tugatamiz. Keyingi maʼruzada markaziy limit teoremasi va maksimal haqiqatga oʻxshashlik usuli bilan tanishamiz.**
    *That brings our fourth lecture to an end. In the next lecture, we meet the Central Limit Theorem and maximum likelihood estimation.*
