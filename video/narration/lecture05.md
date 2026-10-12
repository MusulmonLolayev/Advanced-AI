# Lecture 5 — video narration (draft 2, for approval)

**One video for the whole lecture**, in two parts like the slides: Part 0 (Markaziy limit teoremasi) = sections 1–5,
Part 1 (Maksimal haqiqatga oʻxshashlik usuli) = sections 6–10. Each section: problem first → concept as the answer →
one AI use → a hands-on pause → the question the next section answers. The coffee shop carries on: pastries per
order, office runs, 66 pastry orders in 200, and 40 espresso shots.

**Draft 2 (only the new lines need approval):** each concept explained from more than one side, and earlier ideas
recapped before they are used (instructor, after Lecture 4). New lines carry a letter after the number (**2a**, **7a**);
every approved line is unchanged. The added angles: how the mean and variance of the pastry order are computed
(recap of Lecture 3); where 0.28 comes from (the two customers either way round); why averaging shrinks the extremes (0.1 →
0.01); why the square root of n appears; sigma stays, the standard error shrinks; the quadratic cost in orders (30 →
120 → 3,000); the normal curve is fixed by two numbers; why every shape becomes a bell (all thirty taking two is
10⁻³⁰); what a broken independence does to the standard error; what "heavy tail" means (one order holds 60 % of the
coffee); how big each island is (0.21, 0.34, 0.26); the full gradient as mu; a big batch's cost against its noise (×32
vs ÷5.7); the multiplication rule behind the likelihood (recap of Lecture 1); why the product underflows (about half
per order, zero near 1,200 orders); more data sharpens the peak (0.66 → 0.015); checking p̂ by the derivative (200 −
200 = 0); the mean as Lecture 1's balance point; how large the n-versus-n − 1 bias is (39/40, 2.5 %); where the fitted
mu and sigma come from; a log gap of 15.5 is a likelihood ratio of about five million; where the square in squared
error comes from; a confident wrong answer costs over twenty times more. New numbers: `capture_l05.py` (the `depth`
block), tested in `test_l05.py` (`Draft2AddedLines`).

**Rules applied:** berilganlar (data) / belgilanganlar (labels); "we", never "you" (only *Videoni toʻxtating*);
Latin letters spoken by their English names (eks, en, pi, bi, el); Greek letters keep theirs (mu, sigma, teta);
numbers spelled for the ear, digits on screen. Screen labels are words only.
**Numbers:** every figure comes from `video/statistics/raw/l05_numbers.json` / `l05_figures.txt`
(`capture_l05.py`, unit-tested in `test_l05.py`). The sampling distributions are exact (no simulation); the 40
espresso shots are the figure script's own, regenerated from its seed.
**Slide fixed:** the espresso slide said "shift the centre to 28.6 and it falls to −81.8"; that candidate also has
σ = 1.5, so the slide now says so.

**Terms to confirm** (new in this lecture): tanlanma oʻrtachasining taqsimoti (sampling distribution of the mean) ·
tarafkash boʻlmagan baho (unbiased estimate; instructor’s term) · standart xato (standard error) · markaziy limit teoremasi (central limit
theorem) · katta sonlar qonuni (law of large numbers) · ogʻir dum (heavy tail) · mini-paket (mini-batch) · gradient ·
gradient tushishi (gradient descent) · haqiqatga oʻxshashlik funksiyasi (likelihood; approved in Lecture 2) ·
logarifmik haqiqatga oʻxshashlik (log-likelihood) · maksimal haqiqatga oʻxshashlik usuli (maximum likelihood
estimation) · baho (estimate) · kross-entropiya (cross-entropy) · oʻrtacha kvadratik xato (mean squared error) ·
qatlam / guruh normallashtirish (layer / group normalization).

Format per line: **UZ** (your voice) · *EN* (English track) · ▸ visual.

---

## Lecture opening
▸ title card "5-maʼruza" → the two parts
0. **Assalomu alaykum, aziz doʻstlar. Beshinchi maʼruzamizga xush kelibsiz. Bu maʼruza ham ikki qismdan iborat. Nolinchi qismda markaziy limit teoremasini oʻrganamiz, birinchi qismda esa maksimal haqiqatga oʻxshashlik usuli bilan tanishamiz.**
   *Hello, dear friends, and welcome to our fifth lecture. It also has two parts. In part zero we study the central limit theorem, and in part one we meet maximum likelihood estimation.*

## Part 0 — Markaziy limit teoremasi
▸ part card "0-qism · Markaziy limit teoremasi"

### 1-boʻlim · Section 1 — Tanlanma oʻrtachasining taqsimoti · The sampling distribution
1. **Hozirgacha hisoblagan har bir oʻrtachamiz bitta tanlanmadan olingan edi. Boshqa tanlanma olsak, oʻrtacha ham oʻzgaradi.**
   *Every average we have computed so far came from one sample. Take a different sample, and the average changes.*
2. **Qahvaxonada bitta buyurtmada nol, bir yoki ikki pishiriq boʻladi: nol butun oʻndan yetti, ikki va bir ehtimol bilan. Oʻrtacha nol butun oʻndan toʻrt, dispersiya nol butun yuzdan qirq toʻrt.**
   *In the coffee shop, an order holds zero, one or two pastries, with probabilities zero point seven, two and one. The mean is zero point four, the variance zero point four four.*
   ▸ the pastry bars of Lecture 3: 0.7, 0.2, 0.1
2a. **Eslaylik, uchinchi maʼruzada kutilmani shunday topgan edik: har bir qiymatni ehtimoliga koʻpaytirib, hammasini qoʻshamiz. Bir karra nol butun oʻndan ikki qoʻshuv ikki karra nol butun oʻndan bir — nol butun oʻndan toʻrt. Dispersiya esa kvadratlar kutilmasi minus kutilmaning kvadrati: nol butun oʻndan olti minus nol butun yuzdan oʻn olti.**
   *Recall how we found the expectation in Lecture 3: multiply each value by its probability and add them all. One times zero point two plus two times zero point one: zero point four. The variance is the expectation of the squares minus the square of the expectation: zero point six minus zero point one six.*
   ▸ 0·0.7 + 1·0.2 + 2·0.1 = 0.4;  E[x²] − μ² = 0.6 − 0.16 = 0.44
3. **Ikki mijozga xizmat qilamiz. Nol va nol chiqishi mumkin — oʻrtacha nol. Bir va ikki chiqishi ham mumkin — oʻrtacha bir butun oʻndan besh. Qahvaxona oʻsha, kun oʻsha, javob boshqa.**
   *We serve two customers. We might see zero and zero: an average of zero. Or one and two: an average of one point five. Same shop, same day, a different answer.*
4. **Demak, tanlanma oʻrtachasi aniq son emas, balki oʻz taqsimotiga ega tasodifiy miqdor. Tanlashni qayta-qayta takrorlasak, oʻrtachalarning gistogrammasi hosil boʻladi. Buni tanlanma oʻrtachasining taqsimoti deymiz.**
   *So the sample mean is not a fixed number but a random variable with a distribution of its own. Repeat the sampling again and again, and the averages form a histogram. We call it the sampling distribution of the mean.*
5. **Ikki mijozda oʻrtacha beshta qiymat oladi: nol, nol butun oʻndan besh, bir, bir butun oʻndan besh va ikki. Ehtimollari: nol butun yuzdan qirq toʻqqiz, yigirma sakkiz, oʻn sakkiz, toʻrt va bir.**
   *With two customers the average takes five values: zero, zero point five, one, one point five and two. Their probabilities: zero point four nine, two eight, one eight, zero four and zero one.*
   ▸ the table of five averages and their probabilities; then as bars
5a. **Bu sonlar qayerdan keldi? Oʻrtacha nol butun oʻndan besh ikki yoʻl bilan chiqadi: birinchi mijoz hech narsa olmaydi, ikkinchisi bitta oladi, yoki aksincha. Shuning uchun nol butun oʻndan yettini nol butun oʻndan ikkiga koʻpaytirib, ikki baravar olamiz: nol butun yuzdan yigirma sakkiz.**
   *Where do these numbers come from? An average of zero point five happens in two ways: the first customer takes nothing and the second takes one, or the other way round. So we multiply zero point seven by zero point two, and double it: zero point two eight.*
   ▸ the two orders (0, 1) and (1, 0), each 0.7 × 0.2 = 0.14, adding to 0.28
6. **Bu taqsimotning kutilmasi nol butun oʻndan toʻrt — xuddi bitta mijozdagidek. Tanlanma oʻrtachasi haqiqatga markazlashgan, yaʼni tarafkash boʻlmagan baho.**
   *The expectation of this distribution is zero point four, the same as for one customer. The sample mean is centred on the truth: it is an unbiased estimate.*
7. **Dispersiyasi esa nol butun yuzdan yigirma ikki: nol butun yuzdan qirq toʻrtning yarmi. Umumiy qoida: oʻrtachaning dispersiyasi — sigma kvadratni en ga boʻlganimiz.**
   *Its variance is zero point two two: half of zero point four four. The general rule: the variance of the mean is sigma squared divided by n.*
   ▸ E[x̄] = μ,  Var(x̄) = σ²/n;  0.44 / 2 = 0.22
7a. **Nega kamayadi? Bir mijoz koʻp olsa, ikkinchisi odatda kamroq oladi va oʻrtacha oʻrtaga qaytadi. Chetki holatlar kamdan-kam uchraydi: bitta mijoz ikki pishiriq olishi nol butun oʻndan bir, ikkala mijoz ham ikkitadan olishi esa bor-yoʻgʻi nol butun yuzdan bir.**
   *Why does it shrink? When one customer takes a lot, the other usually takes less, and the average comes back towards the middle. Extremes become rare: one customer taking two pastries has probability zero point one, both customers taking two each only zero point zero one.*
   ▸ the bar at 2 shrinking from 0.1 (one customer) to 0.01 (the average of two)
8. **Sunʼiy intellektda modelning test toʻplamidagi aniqligi ham tanlanma oʻrtachasi: boshqa test toʻplami boshqa aniqlik beradi.**
   *In AI, a model's accuracy on a test set is a sample mean too: a different test set gives a different accuracy.*
9. ⏸ **Keling, oʻzimiz sinab koʻraylik. Videoni toʻxtating. Ikki mijozning ikkalasi ham pishiriq olmasligi ehtimoli qancha?**
   *Let's try it ourselves. Pause the video. What is the chance that neither of two customers buys a pastry?*
10. **Nol butun oʻndan yetti karra nol butun oʻndan yetti: nol butun yuzdan qirq toʻqqiz. Jadvaldagi birinchi son.**
    *Zero point seven times zero point seven: zero point four nine. The first number in the table.*
11. **Oʻrtacha haqiqatdan odatda qanchalik uzoqda turadi? Keyingi boʻlimda.**
    *How far does an average typically sit from the truth? The next section.*

### 2-boʻlim · Section 2 — Standart xato · The standard error
1. **Tanlanma oʻrtachasining standart chetlanishini standart xato deymiz: sigmani en ning kvadrat ildiziga boʻlamiz.**
   *The standard deviation of the sample mean is called the standard error: sigma divided by the square root of n.*
   ▸ SE = σ / √n
1a. **Nega en emas, balki en ning kvadrat ildizi? Oldingi boʻlimda oʻrtachaning dispersiyasi en ga boʻlinishini koʻrdik. Standart chetlanish esa dispersiyaning kvadrat ildizi, shuning uchun en ham ildiz ostiga kiradi.**
   *Why the square root of n and not n itself? In the previous section the variance of the mean was divided by n. The standard deviation is the square root of the variance, so n goes under the root as well.*
   ▸ Var(x̄) = σ²/n → SE = √(σ²/n) = σ/√n
2. **Bu sigma bilan bir xil emas. Sigma bitta mijoz qanchalik oʻzgarishini aytadi, standart xato esa en ta mijoz oʻrtachasi qanchalik oʻzgarishini.**
   *It is not the same as sigma. Sigma says how much one customer varies; the standard error says how much an average of n customers varies.*
2a. **Boshqacha aytganda: berilganlar koʻpaysa, sigma oʻzgarmaydi — qahvaxona oʻsha qahvaxona, mijozlar oʻsha mijozlar. Standart xato esa kichrayadi, chunki koʻproq buyurtmaga qarab, oʻrtachani aniqroq bilamiz.**
   *In other words: with more data, sigma stays the same — the shop is the same shop, the customers the same customers. The standard error shrinks, because looking at more orders we know the average more precisely.*
   ▸ two lines against n: σ flat at 0.663, the SE falling
3. **Qahvaxonada sigma nol butun mingdan olti yuz oltmish uch. Bitta buyurtmani oldindan aytib boʻlmaydi, lekin oʻttizta buyurtma oʻrtachasining standart xatosi nol butun mingdan bir yuz yigirma bir — besh marta barqarorroq.**
   *In the coffee shop, sigma is zero point six six three. One order is unpredictable, but the average of thirty has a standard error of zero point one two one: five times steadier.*
4. **Oʻnta buyurtmada standart xato nol butun mingdan ikki yuz oʻn, qirqtada nol butun mingdan bir yuz besh, bir yuz oltmishtada nol butun mingdan ellik ikki.**
   *At ten orders the standard error is zero point two one zero; at forty, zero point one zero five; at one hundred and sixty, zero point zero five two.*
   ▸ the SE curve against n; the three read-offs marked
5. **Har qadamda berilganlar toʻrt baravar oshadi, xato esa ikki baravar kamayadi. Egri chiziq hech qachon yana tik boʻlmaydi.**
   *Each step quadruples the data and halves the error. There is no sample size at which the curve becomes steep again.*
6. **Demak, aniqlik kvadratik narxda sotib olinadi: xatoni bir foizdan nol butun oʻndan bir foizga tushirish uchun yuz baravar koʻp berilganlar kerak.**
   *So accuracy is bought at quadratic cost: taking the error from one percent to zero point one percent needs a hundred times the data.*
6a. **Qahvaxonada buni shunday koʻramiz: oʻttizta buyurtmadagi xatoni yarmiga tushirish uchun bir yuz yigirmata buyurtma kerak, oʻn baravar kamaytirish uchun esa uch mingta.**
   *In the coffee shop it looks like this: to halve the error at thirty orders we need one hundred and twenty orders, and to cut it tenfold, three thousand.*
   ▸ 30 → 120 (SE ÷ 2),  30 → 3,000 (SE ÷ 10)
7. **Sunʼiy intellektda modellarni baholash ham shuning uchun qimmat: eʼlon qilingan aniqlik atrofidagi xatoni ikki baravar kamaytirish uchun test toʻplamini toʻrt baravar oshirish kerak.**
   *In AI, that is why evaluating models is expensive: halving the error around a reported accuracy takes four times the test set.*
8. ⏸ **Keling, oʻzimiz sinab koʻraylik. Videoni toʻxtating. Olti yuz qirqta buyurtmada standart xato qancha?**
   *Let's try it ourselves. Pause the video. What is the standard error at six hundred and forty orders?*
9. **Bir yuz oltmishdan toʻrt baravar koʻp, demak xato ikki baravar kam: nol butun mingdan yigirma olti.**
   *Four times one hundred and sixty, so half the error: zero point zero two six.*
10. **Biz oʻrtachaning qanchalik tarqoqligini bildik. Uning shakli qanday? Keyingi boʻlimda.**
    *We now know how spread out the average is. What shape does it have? The next section.*

### 3-boʻlim · Section 3 — Markaziy limit teoremasi · The central limit theorem
1. **Istalgan taqsimotdan, oʻrtachasi mu va dispersiyasi chekli boʻlgan, mustaqil qiymatlar olamiz. En oshgan sari tanlanma oʻrtachasining taqsimoti normal taqsimotga yaqinlashadi: oʻrtachasi mu, dispersiyasi sigma kvadratni en ga boʻlganimiz.**
   *Take independent draws from any distribution with mean mu and finite variance. As n grows, the sampling distribution of the mean approaches a normal one: mean mu, variance sigma squared over n.*
   ▸ x̄ ≈ N(μ, σ²/n)
1a. **Eslaylik, normal taqsimotni ikki son toʻliq aniqlaydi: oʻrtacha va standart chetlanish. Demak, katta en da oʻrtacha haqida bilishimiz kerak boʻlgan hamma narsa ikki sonda: mu va standart xato.**
   *Recall that a normal distribution is fixed completely by two numbers: its mean and its standard deviation. So for a large n, everything we need to know about the average is in two numbers: mu and the standard error.*
   ▸ N(μ, SE²): μ marks the centre, SE the width
2. **Eng hayratlanarlisi: dastlabki shakl ahamiyatsiz. Tanga, kubik, kutish vaqti va pishiriqlar — hammasining oʻrtachasi qoʻngʻiroqsimon boʻladi.**
   *The striking part: the original shape does not matter. Coins, dice, waiting times and pastries all have bell-shaped averages.*
2a. **Nega shunday? Oʻrtachada chetki qiymatlar bir-birini yopadi. Oʻttizta mijozning hammasi ikkitadan pishiriq olishi ehtimoli oʻnning minus oʻttizinchi darajasi — deyarli imkonsiz. Kutilma atrofidagi aralashmalar esa juda koʻp usulda chiqadi, shuning uchun oʻrtacha kutilma atrofiga yigʻiladi.**
   *Why? In an average, extreme values cancel each other. The chance that all thirty customers take two pastries each is ten to the minus thirty: practically impossible. Mixtures near the expectation can happen in a huge number of ways, so the average piles up around the expectation.*
   ▸ the n = 30 bars; the right end marked 0.1³⁰ = 10⁻³⁰, the bars around 0.4 lit
3. **Katta sonlar qonuni oʻrtacha qayerga borishini aytgan edi. Markaziy limit teoremasi esa yoʻl-yoʻlakay butun taqsimot qanday koʻrinishini aytadi.**
   *The law of large numbers said where the average lands. The central limit theorem says what its whole distribution looks like on the way.*
4. **Pishiriqlarda: en bir boʻlsa — uchta ustun, qoʻngʻiroqqa umuman oʻxshamaydi. En ikki — qiyshiq. En besh boʻlganda shakl tanish boʻladi, en oʻttizda esa egri chiziqqa juda yaqin.**
   *For pastries: at n equal to one, three bars, nothing like a bell. At two, lopsided. By five the shape is recognisable, and at thirty it tracks the curve closely.*
   ▸ the exact distributions at n = 1, 2, 5, 30, each with the curve N(0.4, 0.44/n)
5. **Bu ustunlar simulyatsiya emas: ular har bir mumkin boʻlgan buyurtmalar toʻplamini hisoblab chiqilgan aniq taqsimot.**
   *These bars are not a simulation: they are the exact distribution, computed from every possible set of orders.*
6. **Sonlar bilan tekshiramiz: oʻrtacha bir standart xato ichida boʻlish ehtimoli nol butun yuzdan toʻqson, yetmish yetti, oltmish yetti va oltmish olti. Normal taqsimot oltmish sakkiz deydi.**
   *We check it in numbers: the chance the average lands within one standard error runs zero point nine zero, seven seven, six seven and six six. The normal distribution says six eight.*
7. **Uchta shart bor: qiymatlar mustaqil, bitta taqsimotdan olingan va dispersiyasi chekli.**
   *There are three conditions: the draws are independent, from the same distribution, with finite variance.*
7a. **Mustaqillik buzilsa nima boʻladi? Masalan, bitta ofis xodimlari birgalikda buyurtma bersa, ularning buyurtmalari bir-biriga oʻxshaydi va oʻttizta buyurtma oʻttizta mustaqil dalil boʻlmay qoladi. Unda standart xato formulasi xatoni haqiqatdagidan kichik koʻrsatadi.**
   *What if independence fails? Say the staff of one office order together: their orders resemble each other, and thirty orders are no longer thirty independent pieces of evidence. Then the standard-error formula shows the error smaller than it really is.*
   ▸ thirty order cards, a cluster of look-alike cards circled
8. **Sunʼiy intellektda aniqlik atrofidagi ishonch oraligʻi aynan shu teoremaga tayanadi: test toʻplamidagi oʻrtacha normal taqsimotga yaqin.**
   *In AI, the confidence interval around an accuracy rests on exactly this theorem: the average over a test set is close to normal.*
9. ⏸ **Keling, oʻzimiz sinab koʻraylik. Videoni toʻxtating. En oʻttiz boʻlganda oʻrtacha ikki standart xato ichida boʻlish ehtimolini normal taqsimot qancha deydi?**
   *Let's try it ourselves. Pause the video. At n equal to thirty, what does the normal distribution say about the chance the average lands within two standard errors?*
10. **Toʻrtinchi maʼruzadagi qoida boʻyicha taxminan toʻqson besh foiz. Aniq hisob toʻqson olti foiz beradi — juda yaqin.**
    *By the rule of the fourth lecture, about ninety-five percent. The exact count gives ninety-six: very close.*
11. **Lekin oʻttizta har doim yetarlimi? Keyingi boʻlimda.**
    *But is thirty always enough? The next section.*

### 4-boʻlim · Section 4 — Ogʻir dum · When the CLT is slow
1. **Oʻsha qahvaxonada har yigirmata buyurtmaning oʻn ikkitasi bitta qahva, oltitasi ikkita, bittasi uchta, va bittasi butun ofis uchun qirqta qahva.**
   *At the same coffee shop, out of every twenty orders, twelve are one coffee, six are two, one is three, and one is an office run of forty.*
   ▸ twenty order cards; one of them a tall stack of 40
2. **Oddiy buyurtma, yaʼni ofis buyurtmasi boʻlmagani, oʻrtacha bir butun oʻndan toʻrt qahva.**
   *An ordinary order, any order that is not an office run, averages one point four coffees.*
2a. **Bitta ofis buyurtmasi qanchalik ogʻir? Yigirmata buyurtmada jami oltmish yetti qahva bor, shundan qirqtasi oʻsha bitta buyurtmada — taxminan oltmish foiz. Kamdan-kam uchraydigan bitta qiymat yigʻindining katta qismini bersa, bunday taqsimotni ogʻir dumli deymiz.**
   *How heavy is a single office run? The twenty orders hold sixty-seven coffees in all, and forty of them are in that one order: about sixty percent. When one rare value carries a large share of the total, we call the distribution heavy-tailed.*
   ▸ the 20 order cards → 67 coffees, the stack of 40 shaded: 40/67 ≈ 60 %
3. **Endi oʻttizta buyurtma olamiz va ular orasida nechta ofis buyurtmasi borligini sanaymiz. Birorta ham boʻlmasa, oʻrtacha bir butun oʻndan toʻrt. Bitta boʻlsa — ikki butun oʻndan yetti. Ikkita boʻlsa — toʻrt.**
   *Now take thirty orders and count the office runs among them. With none, the average is one point four. With one, two point seven. With two, four.*
   ▸ the table: runs 0, 1, 2 → totals 43, 81, 120 → averages 1.4, 2.7, 4.0
4. **Har bir ofis buyurtmasi oʻrtachani taxminan bir butun oʻndan uchga oshiradi, yarimta buyurtma esa boʻlmaydi. Shuning uchun bir butun oʻndan toʻrt va ikki butun oʻndan yetti orasida hech qanday oʻrtacha yoʻq.**
   *Each office run raises the average by about one point three, and there is no half a run. So no average exists between one point four and two point seven.*
5. **Oʻttizta buyurtma oʻrtachasining aniq taqsimoti silliq qoʻngʻiroq emas, balki orolchalar: har biri ichidagi ofis buyurtmalari soni bilan. Pishiriqlarda esa oʻsha en oʻttizda qoʻngʻiroq allaqachon tayyor.**
   *The exact distribution of the average of thirty orders is not a smooth bell but islands, one for each number of office runs inside. For pastries, at the same n of thirty, the bell is already there.*
   ▸ two panels at n = 30: pastries (a bell) and coffees (islands), each against the promised curve
5a. **Orolchalar qanchalik katta? Oʻttizta buyurtmada birorta ham ofis buyurtmasi boʻlmasligi ehtimoli nol butun yuzdan yigirma bir, bitta boʻlishi — oʻttiz toʻrt, ikkitasi — yigirma olti. Oʻrtacha qaysi orolchaga tushishini aynan shu bitta son hal qiladi.**
   *How big are the islands? Among thirty orders, the chance of no office run at all is zero point two one, of one, three four, of two, two six. Which island the average lands on is decided by that one count.*
   ▸ the islands labelled 0.21, 0.34, 0.26
6. **Demak, «en oʻttizdan katta» — bu teorema emas, tajribadan kelgan qoida. Kam uchraydigan katta qiymat uni buzadi.**
   *So "n at least thirty" is a rule of thumb, not a theorem. A rare huge value is what breaks it.*
7. **Sunʼiy intellektda ham kamdan-kam juda katta xato yoki gradient oʻrtachani sakratib yuboradi. Gradientni kesish shuning uchun kerak.**
   *In AI, too, a rare very large loss or gradient makes the average jump. That is why gradients are clipped.*
8. ⏸ **Keling, oʻzimiz sinab koʻraylik. Videoni toʻxtating. Oʻttizta buyurtma orasida uchta ofis buyurtmasi boʻlsa, oʻrtacha qancha boʻladi?**
   *Let's try it ourselves. Pause the video. If three of the thirty orders are office runs, what is the average?*
9. **Yana bitta qadam yuqoriga: taxminan besh butun oʻndan uch.**
   *One more step up: about five point three.*
10. **Bu teoremaning sunʼiy intellektdagi eng muhim qoʻllanishi qayerda? Keyingi boʻlimda.**
    *Where does this theorem matter most in AI? The next section.*

### 5-boʻlim · Section 5 — Mini-paket gradientlari · Mini-batch gradients
1. **Neyron tarmoqni oʻqitish gradientni hisoblashni talab qiladi. Haqiqiy gradient barcha oʻqitish misollari boʻyicha oʻrtacha, lekin bu juda sekin. Shuning uchun bir nechta misoldan iborat mini-paket boʻyicha oʻrtacha olinadi.**
   *Training a neural network means computing a gradient. The honest one averages over all training examples, but that is far too slow. So we average over a mini-batch of a few examples instead.*
   ▸ the full data set; a small batch lifted out of it
1a. **Bogʻlanishni koʻraylik: barcha oʻqitish misollari — bosh toʻplam, mini-paket esa undan olingan tanlanma. Toʻliq gradient mu ning oʻrnida turadi: biz bilmoqchi boʻlgan, lekin hisoblash qimmat boʻlgan son.**
   *Let's see the link: all the training examples are the population, and a mini-batch is a sample drawn from it. The full gradient plays the role of mu: the number we want, but which is costly to compute.*
   ▸ bosh toʻplam ↔ all examples,  tanlanma ↔ mini-batch,  μ ↔ full gradient
2. **Mini-paket gradienti — tanlanma oʻrtachasining oʻzi. Demak, u tarafkash emas: toʻliq gradientga markazlashgan. Uning shovqini esa gradient sigmasini paket hajmining kvadrat ildiziga boʻlganimizga teng.**
   *A mini-batch gradient is a sample mean. So it is unbiased, centred on the full gradient, and its noise is the gradient's sigma divided by the square root of the batch size.*
   ▸ SE = σ_g / √B
3. **Oʻqitish umuman ishlashining sababi shu.**
   *That is why training works at all.*
4. **Takrorlaymiz: paket hajmini toʻrt baravar oshirish shovqinni ikki baravar kamaytiradi. Shuning uchun ikki ming qirq sakkizlik paket oltmish toʻrtlikdan oʻttiz ikki baravar emas, bor-yoʻgʻi besh butun oʻndan yetti baravar kam shovqinli.**
   *Let's repeat it: quadrupling the batch size halves the gradient noise. That is why a batch of two thousand and forty-eight is not thirty-two times better than sixty-four: it is only five point seven times less noisy.*
4a. **Narxini ham hisobga olaylik: ikki ming qirq sakkizlik paketda har bir qadam oltmish toʻrtlikdan oʻttiz ikki baravar qimmat, shovqin esa atigi besh butun oʻndan yetti baravar kam. Shuning uchun koʻpincha kichikroq paket bilan koʻproq qadam tashlash foydaliroq.**
   *Let's count the cost too: with a batch of two thousand and forty-eight, each step costs thirty-two times as much as with sixty-four, while the noise is only five point seven times smaller. That is why many steps with a smaller batch often pay off better.*
   ▸ two bars: cost × 32, noise ÷ 5.7
5. **Paketli normallashtirish ham shunga tayanadi: u paketdan baholangan oʻrtacha va dispersiyadan foydalanadi. Paket ikki yoki toʻrtta misoldan iborat boʻlsa, bu baholar shovqinli — qatlam va guruh normallashtirish shuning uchun bor.**
   *Batch normalization rests on it too: it uses a mean and variance estimated from the batch. With two or four examples those estimates are noisy, which is one reason layer and group normalization exist.*
6. ⏸ **Keling, oʻzimiz sinab koʻraylik. Videoni toʻxtating. Paket hajmini oltmish toʻrtdan ikki yuz ellik oltiga oshirsak, gradient shovqini necha marta kamayadi?**
   *Let's try it ourselves. Pause the video. If the batch grows from sixty-four to two hundred and fifty-six, how many times smaller does the gradient noise get?*
7. **Paket toʻrt baravar oshdi, demak shovqin ikki baravar kamayadi.**
   *The batch grew four times, so the noise halves.*
8. **Mana shu bilan nolinchi qismni tugatamiz. Lekin bu gradient qaysi funksiyaning gradienti? Modelni nima uchun oʻqitamiz? Birinchi qismda.**
   *That completes part zero. But whose gradient is it? What are we training the model for? In part one.*

## Part 1 — Maksimal haqiqatga oʻxshashlik usuli
▸ part card "1-qism · Maksimal haqiqatga oʻxshashlik usuli"

### 6-boʻlim · Section 6 — Haqiqatga oʻxshashlik funksiyasi · The likelihood function
1. **Hozirgacha har bir taqsimot parametrlari tayyor holda keldi: pi nol butun oʻndan uch, lambda toʻrt, mu va sigma. Bu sonlar qayerdan kelgani hech qachon aytilmadi.**
   *So far every distribution came with its parameters filled in: p zero point three, lambda four, mu and sigma. Nobody ever said where those numbers came from.*
2. **Savol: berilganlar boʻyicha qaysi parametr qiymati bu berilganlarni eng kam ajablanarli qiladi?**
   *The question: given the data, which parameter value makes that data least surprising?*
3. **Ikki yuzta buyurtmaning oltmish oltitasida pishiriq bor edi. Pi nol butun yuzdan yigirma besh boʻlganmi? Mumkin, lekin unda oltmish olti biroz tasodif boʻlib qoladi. Pi nol butun yuzdan oʻttiz uch esa koʻrganimizni eng oddiy holga aylantiradi.**
   *Of two hundred orders, sixty-six contained a pastry. Was p zero point two five? Possible, but then sixty-six would be a bit of a fluke. A p of zero point three three makes what we saw the most ordinary thing in the world.*
   ▸ 200 order cards, 66 lit
4. **Haqiqatga oʻxshashlik — kuzatilgan berilganlarning ehtimoli, faqat berilganlarning emas, nomaʼlum parametrning funksiyasi sifatida oʻqiladi.**
   *The likelihood is the probability of the data we actually observed, read as a function of the unknown parameter rather than of the data.*
   ▸ L(θ) = ∏ p(xᵢ | θ)
5. **Har bir buyurtmada pishiriq boʻlsa uning ehtimoli pi, boʻlmasa bir minus pi. Buyurtmalar mustaqil, shuning uchun ikki yuzta ehtimol koʻpaytiriladi, va bir xil asosning darajalari qoʻshiladi.**
   *Each order with a pastry contributes p, each without contributes one minus p. The orders are independent, so the two hundred probabilities multiply, and powers of the same base add their exponents.*
5a. **Bu birinchi maʼruzadagi koʻpaytirish qoidasi: mustaqil hodisalarning birga roʻy berish ehtimoli ularning ehtimollari koʻpaytmasiga teng. Masalan, ikki buyurtmaning ikkalasida ham pishiriq boʻlishi — pi karra pi.**
   *This is the multiplication rule from Lecture 1: the chance that independent events all happen is the product of their chances. For example, both of two orders containing a pastry: p times p.*
   ▸ two lit order cards: p · p
6. **Natija: pi ning oltmish oltinchi darajasi karra bir minus pi ning bir yuz oʻttiz toʻrtinchi darajasi.**
   *The result: p to the sixty-six, times one minus p to the one hundred and thirty-four.*
   ▸ L(p) = p⁶⁶ (1 − p)¹³⁴
7. **Faqat sonlar qoldi: qaysi buyurtmada pishiriq boʻlgani yoʻqoldi. Pi haqidagi butun dalil — oltmish olti va bir yuz oʻttiz toʻrt.**
   *Only the counts survived: which orders had pastries vanished. All the evidence about p is sixty-six and one hundred and thirty-four.*
8. **Parametr belgilangan boʻlsa, bu berilganlar ustidagi taqsimot. Berilganlar belgilangan boʻlsa, bu parametr ustidagi egri chiziq, va u ehtimollik taqsimoti emas. Egri chiziqning choʻqqisi — maksimal haqiqatga oʻxshashlik bahosi.**
   *With the parameter fixed, this is a distribution over data. With the data fixed, it is a curve over the parameter, and that curve is not a probability distribution. Its peak is the maximum likelihood estimate.*
9. **Sunʼiy intellektda modelni oʻqitish aynan shu: oʻqitish berilganlarini eng kam ajablanarli qiladigan parametrlarni qidirish.**
   *In AI, training a model is exactly this: searching for the parameters that make the training data least surprising.*
10. ⏸ **Keling, oʻzimiz sinab koʻraylik. Videoni toʻxtating. Uchta buyurtma: pishiriq bor, yoʻq, bor. Haqiqatga oʻxshashlik funksiyasi qanday?**
    *Let's try it ourselves. Pause the video. Three orders: pastry, none, pastry. What is the likelihood?*
11. **Pi karra bir minus pi karra pi: pi kvadrat karra bir minus pi.**
    *p times one minus p times p: p squared times one minus p.*
12. **Bu koʻpaytma juda kichik son beradi. U bilan qanday ishlaymiz? Keyingi boʻlimda.**
    *This product gives a tiny number. How do we work with it? The next section.*

### 7-boʻlim · Section 7 — Nega logarifm · Why the logarithm
1. **Choʻqqida haqiqatga oʻxshashlik taxminan oʻnning minus ellik beshinchi darajasi: aynan bitta ikki yuz buyurtmalik ketma-ketlikning ehtimoli.**
   *At its peak the likelihood is about ten to the minus fifty-five: the chance of one exact sequence of two hundred orders.*
   ▸ L(p̂) ≈ 8 × 10⁻⁵⁶
2. **Agar faqat «ikki yuzdan oltmish olti» deb bilsak, uni nechta usulda boʻlishi mumkinligiga koʻpaytiramiz va nol butun yuzdan olti chiqadi. Bu koʻpaytuvchida pi yoʻq, shuning uchun choʻqqi joyidan qimirlamaydi.**
   *If we only knew "sixty-six of two hundred", we would multiply by the number of ways it could happen, and get zero point zero six. That factor has no p in it, so the peak does not move.*
3. **Logarifm olamiz. Birinchidan, choʻqqi joyidan qimirlamaydi: logarifm qatʼiy oʻsuvchi funksiya.**
   *We take the logarithm. First, it does not move the peak: the logarithm is strictly increasing.*
   ▸ the likelihood (rescaled) above, the log-likelihood below; both peak at 0.33
4. **Ikkinchidan, hisobni qutqaradi: bir necha ming misolda koʻpaytma kompyuterda aniq nolga aylanib qoladi va choʻqqi yoʻqoladi. Oʻsha sonning logarifmi esa oddiy son: minus bir yuz yigirma olti butun yuzdan sakson toʻrt.**
   *Second, it rescues the arithmetic: at a few thousand examples the product becomes exactly zero in the computer, and the peak is lost. The log of the same number is perfectly ordinary: minus one hundred twenty-six point eight four.*
4a. **Nega nolga aylanadi? Har bir buyurtma koʻpaytmani oʻrtacha hisobda taxminan ikki baravar kichraytiradi, kompyuter esa oʻnning minus uch yuz yigirma uchinchi darajasi atrofidagi sondan kichigini saqlay olmaydi. Bizning buyurtmalarda bu chegaraga taxminan bir ming ikki yuzta buyurtmada yetamiz.**
   *Why does it turn into zero? On average each order makes the product about half as large, and the computer cannot hold a number smaller than about ten to the minus three hundred and twenty-three. With orders like ours, we reach that limit at about one thousand two hundred orders.*
   ▸ the product halving order by order; at ≈ 1,200 orders it hits 0 (the float floor ≈ 5 × 10⁻³²⁴)
5. **Uchinchidan, koʻpaytmani yigʻindiga aylantiradi. Yigʻindini har bir had boʻyicha differensiallash oson, va oʻqitish sikli paket boʻyicha aynan yigʻindini jamlaydi.**
   *Third, it turns a product into a sum. A sum differentiates term by term, and a training loop accumulates exactly a sum over a batch.*
6. **Choʻqqi qanchalik keskin? Pi nol butun yuzdan oʻttiz uchga nisbatan pi nol butun oʻndan uch nol butun yuzdan oltmish olti marta, pi nol butun oʻndan toʻrt esa atigi nol butun yuzdan oʻn ikki marta ehtimolli.**
   *How sharp is the peak? Compared with zero point three three, a p of zero point three is zero point six six times as likely, and zero point four only zero point one two.*
   ▸ the relative likelihood read off at 0.30 and 0.40
6a. **Choʻqqining keskinligi berilganlarga bogʻliq. Buyurtmalar oʻn baravar koʻp boʻlsa — ikki mingtadan olti yuz oltmishtasida pishiriq — pi nol butun oʻndan uchning nisbiy haqiqatga oʻxshashligi nol butun yuzdan oltmish oltidan nol butun mingdan oʻn beshga tushadi. Ikkinchi boʻlimdagidek: berilganlar koʻpaysa, baho aniqlashadi.**
   *How sharp the peak is depends on the data. With ten times the orders — six hundred and sixty pastries in two thousand — the relative likelihood of zero point three falls from zero point six six to zero point zero one five. As in section two: more data, a sharper estimate.*
   ▸ the relative-likelihood curve for 200 orders, then the narrower one for 2,000; the read-off at 0.30
7. **Berilganlar bitta qiymatni tanlab, qolganini taqiqlamaydi — ularni baholaydi. Oltinchi maʼruzada bu baholash aposterior taqsimotga aylanadi.**
   *The data does not pick one value and forbid the rest: it grades them. In Lecture 6 that grading becomes a posterior distribution.*
8. **Sunʼiy intellektda shuning uchun har bir freymvork ehtimollarni emas, ularning logarifmini koʻpaytirmasdan qoʻshadi.**
   *In AI, that is why every framework adds up log-probabilities instead of multiplying probabilities.*
9. ⏸ **Keling, oʻzimiz sinab koʻraylik. Videoni toʻxtating. Pi nol butun yuzdan yigirma besh choʻqqiga nisbatan necha marta ehtimolli?**
   *Let's try it ourselves. Pause the video. How likely is p equal to zero point two five, relative to the peak?*
10. **Atigi nol butun yuzdan toʻrt marta. Boshida aytganimiz «biroz tasodif» shu.**
    *Only zero point zero four times. That is the "bit of a fluke" we started with.*
11. **Choʻqqini egri chiziq chizmasdan, formula bilan topsa boʻladimi? Keyingi boʻlimda.**
    *Can we find the peak with a formula instead of drawing the curve? The next section.*

### 8-boʻlim · Section 8 — Bernulli va Gauss uchun baho · The Bernoulli and Gaussian MLE
1. **En ta tajribada key ta muvaffaqiyat. Logarifm olamiz, differensiallaymiz va nolga tenglaymiz.**
   *k successes in n trials. We take the log, differentiate, and set it to zero.*
   ▸ ℓ(p) = k log p + (n − k) log(1 − p),  dℓ/dp = k/p − (n − k)/(1 − p) = 0
2. **Javob: pi bahosi key ni en ga boʻlganimiz. Bu shunchaki kuzatilgan ulush: ikki yuzdan oltmish olti, nol butun yuzdan oʻttiz uch. Hamma taxmin qiladigan javob, endi farazdan emas, hisobdan kelib chiqdi.**
   *The answer: the estimate of p is k over n. It is simply the observed share: sixty-six of two hundred, zero point three three. The answer everyone would guess, now derived rather than assumed.*
   ▸ p̂ = k / n = 66/200 = 0.33
2a. **Tekshirib koʻramiz. Oltmish oltini nol butun yuzdan oʻttiz uchga boʻlsak — ikki yuz. Bir yuz oʻttiz toʻrtni nol butun yuzdan oltmish yettiga boʻlsak — yana ikki yuz. Ayirmasi nol: hosila aynan shu nuqtada nolga teng.**
   *Let's check. Sixty-six divided by zero point three three: two hundred. One hundred and thirty-four divided by zero point six seven: two hundred again. The difference is zero: the derivative vanishes exactly here.*
   ▸ 66/0.33 − 134/0.67 = 200 − 200 = 0
3. **Gauss uchun ham xuddi shunday: logarifm koʻpaytmani yigʻindiga aylantiradi va eksponentani yoʻqotadi.**
   *The same works for the Gaussian: the log turns the product into a sum and cancels the exponential.*
   ▸ ℓ(μ, σ²) = −(n/2) log(2πσ²) − Σ(xᵢ − μ)² / (2σ²)
4. **Mu boʻyicha differensiallasak, chetlanishlar bir-birini yoʻq qilishi kerak, va bu aynan oʻrtachada boʻladi: mu bahosi — tanlanma oʻrtachasi.**
   *Differentiating in mu says the deviations must cancel, and that happens exactly at the average: the estimate of mu is the sample mean.*
4a. **Bu birinchi maʼruzadagi muvozanat nuqtasining oʻzi: chetlanishlar yigʻindisi nolga teng boʻladigan nuqta. Ikki xil yoʻl bitta javobga olib keldi.**
   *This is the balance point from Lecture 1: the point where the deviations add up to zero. Two different roads lead to the same answer.*
   ▸ the beam of Lecture 1, balancing at x̄
5. **Dispersiya boʻyicha differensiallasak: sigma kvadrat bahosi — chetlanishlar kvadratlarining yigʻindisi, boʻlinsin en.**
   *Differentiating in the variance: the estimate of sigma squared is the sum of squared deviations divided by n.*
   ▸ μ̂ = x̄,  σ̂² = (1/n) Σ(xᵢ − x̄)²
6. **Eʼtibor bersak, birinchi maʼruzada en minus birga boʻlgan edik. Maksimal haqiqatga oʻxshashlik bahosi biroz kichik chiqadi, chunki tarqoqlik oʻsha berilganlarga moslangan oʻrtacha atrofida oʻlchanadi.**
   *Note that in the first lecture we divided by n minus one. Maximum likelihood runs slightly small, because the spread is measured around an average fitted to the same data.*
6a. **Tarafkashlik qanchalik katta? En ga boʻlingan baho oʻrtacha hisobda haqiqiy dispersiyaning en minus bir boʻlinsin en qismini beradi. Keyingi boʻlimdagi qirqta espressoda bu oʻttiz toʻqqiz boʻlinsin qirq, yaʼni nol butun mingdan toʻqqiz yuz yetmish besh: farq atigi ikki yarim foiz. Berilganlar koʻpaygan sari bu farq yoʻqoladi.**
   *How large is the bias? On average, the estimate that divides by n gives n minus one over n of the true variance. For the forty espresso shots of the next section that is thirty-nine over forty, zero point nine seven five: only two and a half percent off. As the data grows, the gap disappears.*
   ▸ E[σ̂²] = (n − 1)/n · σ²;  39/40 = 0.975
7. **Sunʼiy intellektda sinflarning boshlangʻich ehtimollari ham shunday baholanadi: har bir sinfning oʻqitish berilganlaridagi ulushi.**
   *In AI, the starting probabilities of the classes are estimated this way too: each class's share of the training data.*
8. ⏸ **Keling, oʻzimiz sinab koʻraylik. Videoni toʻxtating. Bir yuz ellik buyurtmaning qirq beshtasida pishiriq bor. Pi bahosi qancha?**
   *Let's try it ourselves. Pause the video. Forty-five of one hundred and fifty orders had a pastry. What is the estimate of p?*
9. **Qirq beshni bir yuz ellikka boʻlamiz: nol butun oʻndan uch.**
   *Forty-five divided by one hundred and fifty: zero point three.*
10. **Bu baho haqiqatan eng yaxshi egri chiziqni beradimi? Keyingi boʻlimda tekshiramiz.**
    *Does this estimate really give the best curve? We check it in the next section.*

### 9-boʻlim · Section 9 — Qaysi egri chiziq mos keladi · Which bell curve fits
1. **Qirqta espresso hajmini millilitrda oʻlchadik. Oʻqdagi chiziqchalar — har bir espresso.**
   *We measured forty espresso shots in millilitres. The ticks on the axis are the individual shots.*
   ▸ the 40 shots as ticks and a histogram
2. **Maksimal haqiqatga oʻxshashlik bahosi: mu yigirma toʻqqiz butun yuzdan sakson sakkiz, sigma bir butun yuzdan yigirma yetti. Logarifmik haqiqatga oʻxshashlik minus oltmish olti butun oʻndan uch.**
   *The maximum likelihood fit: mu twenty-nine point eight eight, sigma one point two seven. The log-likelihood is minus sixty-six point three.*
   ▸ the fitted curve over the histogram
2a. **Bu sonlar oldingi boʻlim formulalaridan: mu — qirqta hajmning oʻrtachasi, sigma esa chetlanishlar kvadratlari yigʻindisini qirqqa boʻlib, kvadrat ildizini olganimiz.**
   *These numbers come straight from the previous section's formulas: mu is the average of the forty volumes, and sigma is the square root of the sum of squared deviations divided by forty.*
   ▸ μ̂ = x̄,  σ̂ = √((1/40) Σ(xᵢ − x̄)²)
3. **Markazni yigirma sakkiz butun oʻndan oltiga surib, sigmani bir butun oʻndan besh qilsak, natija minus sakson bir butun oʻndan sakkizga tushadi.**
   *Move the centre to twenty-eight point six with sigma one point five, and it falls to minus eighty-one point eight.*
4. **Markazni joyida qoldirib, sigmani uch butun oʻndan ikkiga kengaytirsak — minus sakson olti butun oʻndan toʻrt.**
   *Keep the centre and widen sigma to three point two: minus eighty-six point four.*
5. **Ikkalasi ham yomonroq, va sonlar qanchalik yomonligini aytadi: eng yaxshi egri chiziq keyingisidan oʻn besh butun oʻndan besh ochko oldinda.**
   *Both are worse, and the numbers say by how much: the best curve leads the next one by fifteen point five.*
   ▸ three curves with their scores: −66.3, −81.8, −86.4
5a. **Logarifmda oʻn besh butun oʻndan besh ochko — oddiy haqiqatga oʻxshashlikda taxminan besh million marta farq. Logarifmdagi ayirma haqiqatga oʻxshashliklar nisbatiga aylanadi.**
   *Fifteen point five points on the log scale is a factor of about five million in the likelihood itself. A difference of logs becomes a ratio of likelihoods.*
   ▸ e^15.5 ≈ 5,000,000
6. **Demak, maksimal haqiqatga oʻxshashlik — egri chiziqlar orasida qidiruv: har bir nomzod baho oladi, va gʻolib — eng yuqori bahoga ega.**
   *So maximum likelihood is literally a search over curves: every candidate gets a score, and the winner has the highest.*
7. **Sunʼiy intellektda gradient tushishi ham aynan shu qidiruvni qadam-baqadam bajaradi.**
   *In AI, gradient descent runs exactly this search, step by step.*
8. ⏸ **Keling, oʻzimiz sinab koʻraylik. Videoni toʻxtating. Birinchi maʼruzadagi kabi en minus birga boʻlsak, sigma bir butun yuzdan yigirma yettidan kattami yoki kichikmi?**
   *Let's try it ourselves. Pause the video. Dividing by n minus one as in the first lecture, is sigma larger or smaller than one point two seven?*
9. **Kattaroq: bir butun yuzdan yigirma toʻqqiz. Kichikroq songa boʻlsak, natija kattaroq.**
   *Larger: one point two nine. Dividing by a smaller number gives a larger result.*
10. **Neyron tarmoqlar qanday yoʻqotish funksiyasi bilan oʻqitiladi va u qayerdan keladi? Keyingi boʻlimda.**
    *What loss are neural networks trained with, and where does it come from? The next section.*

### 10-boʻlim · Section 10 — Yoʻqotish funksiyalari · Losses are log-likelihoods
1. **Klassifikator har bir misol uchun birinchi sinf ehtimolini beradi, belgilanganlar esa nol yoki bir — Bernulli. Haqiqatga oʻxshashlikning minus logarifmini yozamiz.**
   *A classifier outputs, for each example, its chance of class one, and the labels are zero or one: Bernoulli. We write down minus the log-likelihood.*
   ▸ −ℓ = −Σ [ yᵢ log pᵢ + (1 − yᵢ) log(1 − pᵢ) ]
2. **Oʻng tomon — ikkilik kross-entropiya: har bir chuqur oʻqitish freymvorkida aynan shunday yozilgan. Taxminan emas, aynan.**
   *The right-hand side is binary cross-entropy, exactly as written in every deep learning framework. Not approximately: identically.*
3. **Key ta sinf boʻlsa, Bernulli kategorial taqsimotga aylanadi va kategorial kross-entropiya chiqadi.**
   *With k classes the Bernoulli becomes a categorical distribution, and the same step gives categorical cross-entropy.*
4. **Regressiya modeli uchun esa qoldiqlar normal deb faraz qilamiz. Minus logarifmik haqiqatga oʻxshashlik — oʻzgarmas son qoʻshuv oʻrtacha kvadratik xatoning musbat karralisi.**
   *For a regression model we assume the residuals are normal. Minus the log-likelihood is a constant plus a positive multiple of the mean squared error.*
   ▸ −ℓ = (n/2) log(2πσ²) + (1/2σ²) Σ (yᵢ − f(xᵢ))²
4a. **Kvadrat qayerdan keldi? Normal taqsimot zichligida eksponenta ichida chetlanishning kvadrati turadi. Logarifm eksponentani olib tashlaydi va faqat oʻsha kvadrat qoladi.**
   *Where does the square come from? Inside the exponential of the normal density sits the squared deviation. The log removes the exponential, and only that square remains.*
   ▸ exp(−(y − f(x))²/2σ²) → log → −(y − f(x))²/2σ²
5. **Demak, ikki asosiy yoʻqotish funksiyasi — bitta gʻoya: farazimizdagi taqsimotning minus logarifmik haqiqatga oʻxshashligi. Kvadratik xato normal qoldiqlarni faraz qiladi, shuning uchun u chetga chiqqan qiymatlar ortidan quvadi.**
   *So the two default losses are one idea: minus the log-likelihood of the distribution we assumed. Squared error assumes normal residuals, which is why it chases outliers.*
6. **Neyron tarmoq uchun formula yoʻq, lekin logarifmik haqiqatga oʻxshashlik baribir misollar boʻyicha yigʻindi. Shuning uchun gradient boʻylab qadam tashlaymiz, mini-paketda esa nolinchi qism ishlaydi: maksimal haqiqatga oʻxshashlik nimani optimallashtirishni aytadi, markaziy limit teoremasi esa nega buni bir necha misolda qilish mumkinligini.**
   *A neural network has no formula, but its log-likelihood is still a sum over examples. So we step along the gradient, and on a mini-batch part zero applies: maximum likelihood says what to optimise, and the central limit theorem says why we may do it a few examples at a time.*
7. ⏸ **Keling, oʻzimiz sinab koʻraylik. Videoni toʻxtating. Belgilangan sinf bir, model ehtimoli nol butun oʻndan toʻqqiz. Bu misolning kross-entropiyasi qancha?**
   *Let's try it ourselves. Pause the video. The label is one and the model says zero point nine. What is this example's cross-entropy?*
8. **Minus logarifm nol butun oʻndan toʻqqiz: taxminan nol butun mingdan bir yuz besh. Model ishonchli va toʻgʻri, shuning uchun yoʻqotish kichik.**
   *Minus the log of zero point nine: about zero point one zero five. The model is confident and right, so the loss is small.*
8a. **Model xato qilib, nol butun oʻndan bir desa-chi? Minus logarifm nol butun oʻndan bir — taxminan ikki butun yuzdan oʻttiz, yaʼni yigirma baravardan ham koʻp. Kross-entropiya ishonch bilan xato qilgan modelni qattiq jazolaydi.**
   *And if the model is wrong and says zero point one? Minus the log of zero point one is about two point three zero: more than twenty times as much. Cross-entropy punishes a model that is confidently wrong.*
   ▸ −log p against p: 0.9 → 0.105,  0.1 → 2.30
9. **Keling, maʼruzani yakunlaylik. Tanlanma oʻrtachasi tasodifiy miqdor: u mu ga markazlashgan, standart xatosi sigmani en ning ildiziga boʻlganimiz, shuning uchun toʻrt baravar berilganlar xatoni ikki baravar kamaytiradi. Markaziy limit teoremasi: chekli dispersiyali mustaqil qiymatlarning oʻrtachasi normal taqsimotga keladi, ogʻir dum esa buni sekinlashtiradi.**
   *Let's wrap up the lecture. The sample mean is a random variable: centred on mu, with standard error sigma over the root of n, so four times the data halves the error. The central limit theorem: averages of independent draws with finite variance become normal, and a heavy tail slows that down.*
10. **Haqiqatga oʻxshashlik — kuzatilgan berilganlarning parametr funksiyasi sifatidagi ehtimoli, va biz uning logarifmini maksimallashtiramiz. Bernulli uchun baho — kuzatilgan ulush, Gauss uchun — oʻrtacha va tarqoqlik. Kross-entropiya va kvadratik xato — minus logarifmik haqiqatga oʻxshashliklar.**
    *The likelihood is the probability of the observed data as a function of the parameter, and we maximise its log. For a Bernoulli the estimate is the observed share; for a Gaussian, the average and the spread. Cross-entropy and squared error are negative log-likelihoods.*
11. **Mana shu bilan beshinchi maʼruzamizni tugatamiz. Keyingi maʼruzada Bayes xulosasi bilan tanishamiz.**
    *That brings our fifth lecture to an end. In the next lecture, we meet Bayesian inference.*
