# Lecture 7 — video narration (draft 1, for approval)

**One video for the whole lecture**, in two parts like the slides: Part 0 (Entropiya va kross-entropiya) = sections
1–6, Part 1 (KL divergensiya va oʻzaro axborot) = sections 7–11. Each section: problem first → concept as the answer →
one AI use → a hands-on pause → the question the next section answers. The running example is the slides' own: one
town's weather over 360 logged days (sunny 180, cloudy 90, rain 45, storm 45), three forecasters, Lecture 6's 7:40 bus,
and three questions we could ask in the morning about rain.

**Written to the depth rule from the start** (explain each idea from more than one side, recap what it needs from
Lectures 1–6): entropy as the average number of yes/no questions, as the average surprise, and as how spread out a
distribution is; the surprise as Lecture 3's expectation and the log as Lecture 2's multiplication rule turned into a
sum; the binary entropy as the entropy of Lecture 3's Bernoulli; cross-entropy as the bill for the wrong question tree
and as Lecture 5's negative log-likelihood (in bits and in nats); the always-sunny forecaster winning on sunny days and
losing on the rest; the floor in 360-day totals; KL as the extra questions, as the cross-entropy minus the floor, and as
how far Lecture 6's posterior moved from its prior; the asymmetry shown by a pair where the two directions happen to be
equal and a pair where they are not; mutual information as the drop in uncertainty, read in both directions, as Lecture
2's independence test turned into an amount, and as a KL between the joint and the product of the marginals; Lecture
2's conditional probability recapped for P(wet | grey sky); information gain as the same formula.

**Rules applied:** berilganlar (data) / belgilanganlar (labels); "we", never "you" (only *Videoni toʻxtating*);
Latin letters spoken by their English names (eych, pi, kyu, eks, uay, ay, key el); numbers spelled for the ear, digits
on screen. Screen labels are words only.
**Numbers:** every figure comes from `video/statistics/raw/l07_numbers.json` / `l07_figures.txt`
(`capture_l07.py`, unit-tested in `test_l07.py`). The hundred bus mornings are Lecture 6's, regenerated from its seed.
**Slides:** every number the slides print agrees with the computation. One note on the figure script, not the slides:
`generate_information_theory_graphics.py` prints «KL(uniform ‖ p) = 0.2500 bits (asymmetric)», but KL(p ‖ uniform) is
also 0.25, so that pair is in fact symmetric. The slides use the always-sunny pair (0.82 vs 0.54), which is right;
section 9's pause uses the equal pair on purpose.

**Terms to confirm** (new in this lecture):
- **entropiya** (entropy) · **bit** / **nat** (bit / nat, the units) · **ikkilik entropiya** (binary entropy, as
  Lecture 5's «ikkilik kross-entropiya») · kross-entropiya is already approved (Lecture 5)
- **ajablanish** (surprise, log 1/p). Not «kutilmaganlik», which would sit next to «kutilma» (expectation).
- **savollar daraxti** (question tree) · **ikki asosli logarifm** (log base 2)
- **KL divergensiya** / **Kulbak–Leybler divergensiyasi** (KL divergence) — divergensiya kept, not «masofa», because
  the lecture's point is that it is not a distance
- **oʻzaro axborot** (mutual information), with L6's «axborot nazariyasi». Alternative: «oʻzaro maʼlumot», since
  maʼlumot is our word for information. Please choose.
- **shartli entropiya** (conditional entropy) · **axborot ortishi** (information gain)
- **sinoptik** (forecaster) · **yogʻinli kun** (wet day: rain or storm) · quyoshli / bulutli / yomgʻir / boʻron
- **qaror daraxti** (decision tree) · **belgilarni tanlash** (feature selection) · **bilim distillyatsiyasi** (knowledge
  distillation) · **variatsion avtokodlovchi** (VAE) · **inson fikri bilan kuchaytirib oʻrganish** (RLHF)
- **perpleksiya** (perplexity, named once in the closing outlook)

Format per line: **UZ** (your voice) · *EN* (English track) · ▸ visual.

---

## Lecture opening
▸ title card "7-maʼruza" → the two parts
0. **Assalomu alaykum, aziz doʻstlar. Yettinchi maʼruzamizga xush kelibsiz. Bu maʼruza ham ikki qismdan iborat. Nolinchi qismda entropiya va kross-entropiyani oʻrganamiz, birinchi qismda esa key el divergensiya va oʻzaro axborot bilan tanishamiz.**
   *Hello, dear friends, and welcome to our seventh lecture. It also has two parts. In part zero we study entropy and cross-entropy, and in part one we meet the KL divergence and mutual information.*

## Part 0 — Entropiya va kross-entropiya
▸ part card "0-qism · Entropiya va kross-entropiya"

### 1-boʻlim · Section 1 — Nega entropiya kerak · Why we need entropy
1. **Birinchi maʼruzada tarqoqlikni dispersiya bilan oʻlchadik. Lekin dispersiya uchun sonlar kerak: ularni qoʻshib, oʻrtachasini olamiz.**
   *In Lecture 1 we measured spread with the variance. But the variance needs numbers: we add them and take their mean.*
2. **Endi shunday savol beraylik: ertangi ob-havo qanchalik noaniq? Quyoshli, bulutli, yomgʻir, boʻron. Quyoshlidan yomgʻirni ayirib boʻlmaydi — bu son emas.**
   *Now let's ask: how uncertain is tomorrow's weather? Sunny, cloudy, rain, storm. We cannot subtract rain from sunny: it is not a number.*
   ▸ four weather cards; "quyoshli − yomgʻir = ?" crossed out
3. **Birinchi maʼruzadan eslaylik: kategorial berilganlar uchun bitta oʻlchov bor edi — mod, yaʼni eng koʻp uchraydigan qiymat. Lekin mod qaysi javob koʻp uchrashini aytadi, qanchalik ishonchsiz ekanimizni aytmaydi.**
   *Recall from Lecture 1: for categorical data we had one measure, the mode, the most frequent value. But the mode says which answer is common; it does not say how unsure we are.*
4. **Bir oʻyin oʻynaymiz. Doʻstimiz ertangi ob-havoni tanlab qoʻydi, biz esa uni faqat «ha» yoki «yoʻq» savollar bilan topishimiz kerak.**
   *Let's play a game. A friend has picked tomorrow's weather, and we must find it with yes-or-no questions only.*
   ▸ a sealed card with "?" and a "ha / yoʻq" counter
5. **Shaharda deyarli har kuni quyosh chiqsa, koʻpincha bitta savol yetadi. Toʻrtala javob bir xil ehtimolli boʻlsa, har doim ikki savol kerak.**
   *If the town is sunny almost every day, one question usually does it. If all four answers are equally likely, we always need two.*
6. **Mana shu farq — topish uchun oʻrtacha nechta savol kerakligi — kategoriyalar uchun ham ishlaydigan noaniqlik oʻlchovi. Uni entropiya deymiz, birligi esa bitta «ha yoki yoʻq» savoli: bit.**
   *That difference, how many questions the guessing costs on average, is a measure of uncertainty that works for categories too. We call it entropy, and its unit is one yes-or-no question: the bit.*
   ▸ "entropiya = oʻrtacha savollar soni", unit "bit"
7. **Sunʼiy intellektda ham shu muammo bor: rasm mushukmi, itmi yoki qushmi — modelning javobi kategoriya. Model qanchalik ikkilanayotganini oʻlchash uchun uning ehtimollari entropiyasini hisoblaymiz va eng ikkilangan misollarni odamga belgilashga beramiz.**
   *AI faces the same problem: whether an image is a cat, a dog or a bird, the model's answer is a category. To measure how torn the model is, we compute the entropy of its probabilities, and send the most uncertain examples to a person to label.*
8. ⏸ **Keling, oʻzimiz sinab koʻraylik. Videoni toʻxtating. Toʻrtala ob-havo bir xil ehtimolli. Javobni topish uchun nechta savol kerak?**
   *Let's try it ourselves. Pause the video. All four kinds of weather are equally likely. How many questions does it take to find the answer?*
9. **Ikkita. Avval «quyoshli yoki bulutlimi?» deb soʻraymiz va toʻrtta javobni ikkiga boʻlamiz. Keyin qolgan ikkitasidan birini soʻraymiz. Har safar aynan ikki savol.**
   *Two. First we ask "sunny or cloudy?", which splits the four answers in half. Then we ask about one of the two left. Exactly two questions every time.*
   ▸ the four cards split 2 | 2, then 1 | 1
10. **Javoblar bir xil ehtimolli boʻlmasa-chi? Qaysi savoldan boshlaymiz? Keyingi boʻlimda.**
    *And if the answers are not equally likely? Which question do we ask first? The next section.*

### 2-boʻlim · Section 2 — Ob-havo haqida yigirma savol · Twenty questions about tomorrow
1. **Bir shaharning uch yuz oltmish kunlik ob-havosi yozib olingan: bir yuz sakson kun quyoshli, toʻqson kun bulutli, qirq besh kun yomgʻir va qirq besh kun boʻron.**
   *One town's weather was logged over three hundred and sixty days: one hundred and eighty sunny, ninety cloudy, forty-five rain and forty-five storm.*
   ▸ four bars: 180, 90, 45, 45
2. **Ulushlarga aylantiramiz: quyoshli — yarim, bulutli — toʻrtdan bir, yomgʻir va boʻron — sakkizdan bir.**
   *As shares: sunny one half, cloudy one quarter, rain and storm one eighth each.*
   ▸ p = (1/2, 1/4, 1/8, 1/8)
3. **Eng koʻp uchraydigan javobdan boshlaymiz. Birinchi savol: «quyoshlimi?» Yarim kunlarda javob shu bilan topiladi — bitta savol.**
   *We start with the likeliest answer. First question: "sunny?" On half the days that settles it: one question.*
   ▸ the tree grows: "quyoshlimi?" → yes: sunny, 1 question
4. **Yoʻq boʻlsa: «bulutlimi?» — bulutli kun ikki savol turadi. Yana yoʻq boʻlsa: «yomgʻirmi?» — yomgʻir ham, boʻron ham uch savol turadi.**
   *If not: "cloudy?" A cloudy day costs two questions. If not again: "rain?" Rain and storm both cost three.*
   ▸ the full tree: sunny 1, cloudy 2, rain 3, storm 3
5. **Oʻrtachani uchinchi maʼruzadagi kutilma kabi hisoblaymiz: har bir savollar sonini ehtimoliga koʻpaytirib qoʻshamiz. Yarim karra bir, toʻrtdan bir karra ikki, sakkizdan bir karra uch, yana sakkizdan bir karra uch. Jami — bir butun yuzdan yetmish besh savol.**
   *We compute the average like Lecture 3's expectation: each number of questions times its probability, added up. A half times one, a quarter times two, an eighth times three, another eighth times three. In all, one point seven five questions.*
   ▸ ½·1 + ¼·2 + ⅛·3 + ⅛·3 = 1.75
6. **Uch yuz oltmish kunga qarasak ham shu chiqadi: bir yuz sakson kun bitta savol, toʻqson kun ikkita, toʻqson kun uchta. Jami olti yuz oʻttiz savol, kuniga bir butun yuzdan yetmish besh.**
   *Counting over the three hundred and sixty days gives the same: one hundred and eighty days at one question, ninety at two, ninety at three. Six hundred and thirty questions in all: one point seven five a day.*
   ▸ 180·1 + 90·2 + 90·3 = 630; 630 / 360 = 1.75
7. **Sirri oddiy: kamyob javob qimmat turadi, lekin u haqida kam soʻraymiz. Tez-tez uchraydigan javob arzon, va u haqida koʻp soʻraymiz.**
   *The secret is simple: a rare answer is expensive, but we seldom ask about it. A common answer is cheap, and we ask about it often.*
8. **Sunʼiy intellektda va har qanday kompyuterda fayllarni siqish shu gʻoyada ishlaydi: tez-tez uchraydigan belgiga qisqa kod, kamyob belgiga uzun kod beriladi. Bu Xaffman kodi deyiladi.**
   *In AI, and in every computer, file compression runs on this idea: a frequent symbol gets a short code and a rare one a long code. That is called Huffman coding.*
9. ⏸ **Keling, oʻzimiz sinab koʻraylik. Videoni toʻxtating. Savollarni teskari tartibda bersak-chi: avval «boʻronmi?», keyin «yomgʻirmi?», keyin «bulutlimi?». Oʻrtacha nechta savol kerak boʻladi?**
   *Let's try it ourselves. Pause the video. What if we ask in reverse order: first "storm?", then "rain?", then "cloudy?". How many questions does it take on average?*
10. **Boʻron — bitta savol, yomgʻir — ikkita, bulutli va quyoshli — uchta. Sakkizdan bir karra birga sakkizdan bir karra ikkini, toʻrtdan bir karra uchni va yarim karra uchni qoʻshamiz: ikki butun mingdan olti yuz yigirma besh. Deyarli bitta savolga qimmatroq — chunki eng koʻp uchraydigan javobni oxirida soʻradik.**
    *Storm one question, rain two, cloudy and sunny three. An eighth times one plus an eighth times two, plus a quarter times three, plus a half times three: two point six two five. Almost a whole question more, because we asked about the commonest answer last.*
    ▸ the reversed tree; 2.625 beside 1.75
11. **Bir butun yuzdan yetmish besh — eng arzon daraxtning narxi. Bu sonni daraxt chizmasdan, faqat ehtimollardan topsa boʻladimi? Keyingi boʻlimda.**
    *One point seven five is the price of the cheapest tree. Can we get this number from the probabilities alone, without drawing a tree? The next section.*

### 3-boʻlim · Section 3 — Entropiya · Entropy
1. **Daraxtga qaraylik: ehtimoli yarim boʻlgan javob bitta savol turdi, toʻrtdan bir — ikkita, sakkizdan bir — uchta. Ehtimol har safar ikki baravar kamayganda, bitta savol qoʻshiladi.**
   *Look at the tree: the answer with probability one half cost one question, one quarter two, one eighth three. Each time the probability halves, one more question is added.*
   ▸ 1/2 → 1, 1/4 → 2, 1/8 → 3
2. **Bu ikki asosli logarifmning oʻzi. Eslab olaylik: ikkini oʻziga uch marta koʻpaytirsak sakkiz chiqadi, shuning uchun sakkizning ikki asosli logarifmi — uch. Sakkizdan bir ehtimolli javob uchun birni pi ga boʻlamiz — sakkiz chiqadi, uning logarifmi esa uch savol.**
   *That is the base-two logarithm. Let's recall: two multiplied by itself three times gives eight, so the base-two log of eight is three. For an answer with probability one eighth we take one over p, which is eight, and its log is three questions.*
   ▸ 2 · 2 · 2 = 8 → log₂ 8 = 3; log₂(1/p)
3. **Bu sonni ajablanish deymiz: ehtimoli pi boʻlgan natija uchun birni pi ga boʻlamiz va ikki asosli logarifmini olamiz — shuncha bit ajablanish. Quyoshli kun — bir bit, boʻron — uch bit. Kamyob voqea koʻproq ajablantiradi.**
   *We call this number the surprise: an outcome of probability p brings the base-two log of one over p bits of surprise. A sunny day is one bit, a storm three. A rare event surprises more.*
   ▸ each weather bar labelled with its surprise: 1, 2, 3, 3 bits
4. **Nega aynan logarifm? Ikkinchi maʼruzadagi koʻpaytirish qoidasini eslaylik: bogʻliq boʻlmagan hodisalarning ehtimollari koʻpaytiriladi. Bugun quyoshli, ertaga boʻron boʻlsa — yarim karra sakkizdan bir, yaʼni oʻn oltidan bir. Logarifm koʻpaytmani yigʻindiga aylantiradi: bir bit qoʻshuv uch bit — toʻrt bit. Ajablanishlar ham qoʻshiladi.**
   *Why the logarithm? Recall Lecture 2's multiplication rule: the probabilities of independent events multiply. Sunny today and a storm tomorrow: a half times an eighth, one sixteenth. The log turns the product into a sum: one bit plus three bits, four bits. Surprises add up too.*
   ▸ ½ × ⅛ = 1/16 → 1 + 3 = 4 bits
5. **Entropiya — oʻrtacha ajablanish. Uchinchi maʼruzadagi kutilma kabi: har bir natijaning ajablanishini ehtimoliga koʻpaytirib qoʻshamiz. Formula: eych pi teng minus pi ay karra pi ay ning ikki asosli logarifmi yigʻindisi.**
   *Entropy is the average surprise. Like Lecture 3's expectation: each outcome's surprise times its probability, added up. The formula: H of p equals minus the sum of p i times the base-two log of p i.*
   ▸ H(p) = Σ pᵢ log₂(1/pᵢ) = −Σ pᵢ log₂ pᵢ
6. **Ob-havomizda entropiya — bir butun yuzdan yetmish besh bit. Daraxtning oʻrtachasi bilan aynan bir xil. Demak entropiya — eng yaxshi savollar daraxtining oʻrtacha narxi, uni chizmasdan topamiz.**
   *For our weather the entropy is one point seven five bits, exactly the tree's average. So entropy is the average cost of the best question tree, found without drawing it.*
   ▸ H(p) = 1.75 bits beside the tree's 1.75
7. **Ikki chekka holat. Bitta natijaning ehtimoli bir boʻlsa, entropiya nol: hech qanday savol kerak emas, aniqlik bepul. Toʻrtta natija bir xil ehtimolli boʻlsa, entropiya ikki bit — toʻrt javobli taqsimot uchun eng kattasi.**
   *Two extremes. If one outcome has probability one, the entropy is zero: no questions needed, certainty is free. If four outcomes are equally likely, the entropy is two bits, the most any four-answer distribution can have.*
   ▸ a single full bar (H = 0) and four equal bars (H = 2)
8. **Entropiyaga uchinchi tomondan ham qaraymiz: ehtimol bir joyga toʻplangan boʻlsa — entropiya kichik, hamma joyga yoyilgan boʻlsa — katta. Bu kategoriyalar uchun dispersiyaning oʻrnini bosadi.**
   *We can see entropy from a third side too: probability gathered in one place gives low entropy, probability spread everywhere gives high entropy. For categories it takes the place of the variance.*
9. **Ikki bit bilan bir butun yuzdan yetmish besh orasidagi farq — nol butun yuzdan yigirma besh bit. Iqlimni bilish bizga kuniga shuncha bit tejaydi, uch yuz oltmish kunda esa toʻqson bit.**
   *The gap between two bits and one point seven five is zero point two five bits. Knowing the climate saves us that much a day, and ninety bits over the three hundred and sixty days.*
   ▸ 2 − 1.75 = 0.25 bit / day; × 360 = 90 bits
10. **Sunʼiy intellektda til modeli har bir keyingi soʻz uchun ehtimollar taqsimotini beradi. Uning entropiyasi kichik boʻlsa, model ishonch bilan gapiryapti, katta boʻlsa — ikkilanyapti. Generatsiyadagi «harorat» sozlamasi aynan shu entropiyani oshiradi yoki kamaytiradi.**
    *In AI, a language model gives a probability distribution for each next word. Low entropy means the model speaks with confidence; high means it hesitates. The "temperature" setting in generation raises or lowers exactly this entropy.*
11. ⏸ **Keling, oʻzimiz sinab koʻraylik. Videoni toʻxtating. Uch javobli taqsimot: yarim, toʻrtdan bir, toʻrtdan bir. Uning entropiyasi qancha?**
    *Let's try it ourselves. Pause the video. A three-answer distribution: a half, a quarter, a quarter. What is its entropy?*
12. **Ajablanishlar: bir, ikki, ikki bit. Yarim karra birga toʻrtdan bir karra ikkini ikki marta qoʻshamiz: bir butun oʻndan besh bit. Daraxt bilan ham shu: «birinchisimi?», keyin «ikkinchisimi?».**
    *The surprises are one, two and two bits. A half times one, plus a quarter times two, twice: one point five bits. The tree agrees: "the first?", then "the second?".*
    ▸ ½·1 + ¼·2 + ¼·2 = 1.5
13. **Eng oddiy holat — faqat ikkita javob: yomgʻir yogʻadimi yoki yoʻqmi. Bashorat qachon eng noaniq boʻladi? Keyingi boʻlimda.**
    *The simplest case has only two answers: will it rain or not. When is a forecast most uncertain? The next section.*

### 4-boʻlim · Section 4 — Bashorat qachon eng noaniq · When is a forecast most uncertain
1. **Ikki javobli holat — uchinchi maʼruzadagi Bernulli taqsimoti: yomgʻir pi ehtimol bilan, yomgʻirsiz kun bir minus pi bilan. Uning entropiyasini pi ga qarab chizamiz. Buni ikkilik entropiya deymiz.**
   *The two-answer case is Lecture 3's Bernoulli distribution: rain with probability p, a dry day with one minus p. We plot its entropy against p. We call this the binary entropy.*
   ▸ the binary entropy curve over p from 0 to 1
2. **Choʻqqi pi nol butun oʻndan besh boʻlganda, entropiya bir bit. Adolatli tanga — eng noaniq ikkilik narsa: har doim bitta savol kerak.**
   *The peak is at p equals zero point five, where the entropy is one bit. A fair coin is the most uncertain two-way thing there is: one question is always needed.*
   ▸ the orange point at p = 0.5, H = 1
3. **Ishonch ikki tomonda ham arzon. Nol butun yuzdan oʻn bir ehtimolli bashorat nol butun oʻndan besh bit turadi, nol butun yuzdan sakson toʻqqiz ham xuddi shuncha. Yomgʻir aniq yogʻishini bilish ham, aniq yogʻmasligini bilish ham bir xil foydali.**
   *Confidence is cheap on both sides. A forecast of zero point one one costs zero point five bits, and so does zero point eight nine. Being sure it will rain is as informative as being sure it will not.*
   ▸ the red points at p = 0.11 and p = 0.89, both 0.50 bits; the curve's mirror line at 0.5
4. **Egri chiziq chetlarda tik. Bashoratni nol butun oʻndan beshdan nol butun oʻndan toʻrtga surish deyarli hech narsa bermaydi: entropiya birdan nol butun yuzdan toʻqson yettiga tushadi, nol butun yuzdan uch bit xolos. Nol butun oʻndan birdan nol butun yuzdan birga surish esa nol butun yuzdan qirq yettidan nol butun yuzdan sakkizga tushiradi — nol butun yuzdan oʻttiz toʻqqiz bit.**
   *The curve is steep at the ends. Moving a forecast from zero point five to zero point four buys almost nothing: the entropy drops from one to zero point nine seven, only zero point zero three bits. Moving it from zero point one to zero point zero one drops it from zero point four seven to zero point zero eight: zero point three nine bits.*
   ▸ two steps on the curve, 0.5 → 0.4 (−0.03) and 0.1 → 0.01 (−0.39)
5. **Demak, ikkilanish oʻrtada qimmat emas, chetga yaqinlashganda esa har bir qadam katta bilim beradi. «Deyarli aniq» bilan «aniq» orasidagi farq — haqiqiy farq.**
   *So near the middle a step of doubt costs little, while close to the edge every step brings a lot of knowledge. The gap between "almost certain" and "certain" is a real one.*
6. **Sunʼiy intellektda faol oʻrganish shu egri chiziqdan foydalanadi: belgilash uchun model ehtimoli nol butun oʻndan beshga yaqin, yaʼni entropiyasi eng katta boʻlgan misollar tanlanadi. Ular belgilansa, model eng koʻp narsa oʻrganadi.**
   *In AI, active learning uses this curve: for labelling it picks the examples where the model's probability is close to zero point five, where the entropy is largest. Labelling those teaches the model the most.*
7. ⏸ **Keling, oʻzimiz sinab koʻraylik. Videoni toʻxtating. Yomgʻir ehtimoli toʻrtdan bir. Bashoratning entropiyasi qancha?**
   *Let's try it ourselves. Pause the video. The chance of rain is one quarter. What is the forecast's entropy?*
8. **Yomgʻirning ajablanishi — ikki bit, yomgʻirsiz kunniki — toʻrtdan uchning logarifmi, taxminan nol butun mingdan toʻrt yuz oʻn besh. Toʻrtdan bir karra ikkiga toʻrtdan uch karra shuni qoʻshsak, taxminan nol butun yuzdan sakson bir bit. Bu sonni oʻninchi boʻlimda yana uchratamiz.**
   *The surprise of rain is two bits, of a dry day the log of four thirds, about zero point four one five. A quarter times two plus three quarters times that is about zero point eight one bits. We will meet this number again in section ten.*
   ▸ ¼·2 + ¾·0.415 ≈ 0.81
9. **Hozirgacha haqiqiy taqsimotni bilar edik. Sinoptik esa uni bilmaydi. Notoʻgʻri ishonch bizga qanchaga tushadi? Keyingi boʻlimda.**
   *Until now we knew the true distribution. A forecaster does not. What does a wrong belief cost us? The next section.*

### 5-boʻlim · Section 5 — Kross-entropiya · Cross-entropy
1. **Savollar daraxtimiz haqiqiy iqlimdan qurilgan edi. Hayotda haqiqiy iqlimni hech kim bermaydi: sinoptikning oʻz ishonchi bor, uni kyu deymiz, ob-havo esa pi boʻyicha keladi.**
   *Our question tree was built from the true climate. In real life no one hands us the true climate: a forecaster has their own belief, which we call q, while the weather follows p.*
   ▸ two bar sets side by side: the truth p and a belief q
2. **Tasavvur qilamiz: sinoptik toʻrtala ob-havo bir xil ehtimolli deb oʻylaydi. U savollarini har bir javob ikki bit turgandek beradi. Lekin haqiqatda yarim kunlar quyoshli, yaʼni bitta savol yetadigan kunda u ikki bit toʻlaydi.**
   *Imagine a forecaster who thinks all four kinds of weather are equally likely. They ask as if every answer cost two bits. But in reality half the days are sunny, so on a day that needed one question they pay two bits.*
3. **Hisob aralash chiqadi: har bir javob qanchalik tez-tez uchrashini haqiqat — pi belgilaydi, har bir javob qanchaga tushishini esa ishonch — kyu belgilaydi.**
   *The bill is a mixture: how often each answer comes is set by the truth, p; what each answer costs is set by the belief, q.*
4. **Shu hisob kross-entropiya deyiladi: eych pi, kyu teng minus pi ay karra kyu ay ning ikki asosli logarifmi yigʻindisi. Haqiqiy chastotalar, lekin notoʻgʻri savollar daraxti.**
   *That bill is called the cross-entropy: H of p, q equals minus the sum of p i times the base-two log of q i. Real frequencies, but the wrong question tree.*
   ▸ H(p, q) = −Σ pᵢ log₂ qᵢ, with "haqiqat" under p and "ishonch" under q
5. **Tekis ishongan sinoptik kuniga ikki bit toʻlaydi, haqiqat esa bir butun yuzdan yetmish besh bit turadi.**
   *The forecaster who believes the uniform pays two bits a day, where the truth costs one point seven five.*
   ▸ 2.00 vs 1.75
6. **Kross-entropiya hech qachon arzon chiqmaydi: u doim entropiyadan katta yoki teng, tenglik esa faqat kyu pi ga teng boʻlganda. Haqiqatni eng arzon tasvirlaydigan narsa — haqiqatning oʻzi.**
   *Cross-entropy is never a bargain: it is always at least the entropy, with equality only when q equals p. The cheapest description of the truth is the truth itself.*
   ▸ H(p, q) ≥ H(p), equality only at q = p
7. **Bu formulani biz allaqachon koʻrganmiz. Beshinchi maʼruzada kategorial kross-entropiyani minus logarifmik haqiqatga oʻxshashlik sifatida chiqargan edik: minus uay si karra pi si ning logarifmi yigʻindisi. Bunda uay — belgilangan sinf, pi esa modelning softmaks ehtimollari.**
   *We have seen this formula already. In Lecture 5 we derived categorical cross-entropy as the negative log-likelihood: minus the sum of y c times the log of p c, where y is the labelled class and p the model's softmax probabilities.*
   ▸ Lecture 5's −Σ y_c log p_c beside H(p, q)
8. **Belgilangan sinf ham taqsimot: butun ehtimol toʻgʻri sinfda, qolganlarida nol. Model ehtimollari esa baholanayotgan ishonch. Formula aynan bir xil, hech narsani oʻzgartirmaymiz.**
   *The labelled class is a distribution too: all the probability on the true class, zero elsewhere. The model's probabilities are the belief being scored. The formula is identical; we change nothing.*
   ▸ a one-hot bar set as p, the softmax bars as q
9. **Bitta son, ikki xil oʻqish. Beshinchi maʼruza soʻraydi: modelim boʻyicha berilganlar qanchalik ehtimolsiz edi? Bugungi maʼruza soʻraydi: ishonchim menga qancha ortiqcha bitga tushdi? Birini kamaytirsak, ikkinchisi ham kamayadi.**
   *One number, two readings. Lecture 5 asks: how improbable was the data under my model? Today's lecture asks: how many extra bits did my belief cost me? Minimising one minimises the other.*
10. **Bit yoki nat? Freymvorklar natural logarifmdan foydalanadi, shunda birlik nat boʻladi. Farq — oʻzgarmas koʻpaytuvchi, ikkining natural logarifmi, taxminan nol butun mingdan olti yuz toʻqson uch. Bizning bir butun yuzdan yetmish besh bitimiz — bir butun yuzdan yigirma bir nat. Hech bir qaror oʻzgarmaydi.**
    *Bits or nats? Frameworks use the natural logarithm, and then the unit is the nat. The difference is a fixed factor, the natural log of two, about zero point six nine three. Our one point seven five bits are one point two one nats. No decision changes.*
    ▸ 1 bit = ln 2 ≈ 0.693 nat; 1.75 bits = 1.21 nats
11. **Sunʼiy intellektda har bir klassifikator aynan shu kross-entropiyani minimallashtirib oʻqitiladi. PayTorch dagi kross-entropiya yoʻqotish funksiyasi natlarda hisoblaydi.**
    *In AI, every classifier is trained by minimising exactly this cross-entropy. The cross-entropy loss in PyTorch computes it in nats.*
12. ⏸ **Keling, oʻzimiz sinab koʻraylik. Videoni toʻxtating. Beshinchi maʼruzadagi misol: belgilangan sinf bir, model nol butun oʻndan toʻqqiz deydi. Kross-entropiya bitlarda va natlarda qancha?**
    *Let's try it ourselves. Pause the video. Lecture 5's example: the labelled class is one and the model says zero point nine. What is the cross-entropy in bits and in nats?*
13. **Butun ehtimol toʻgʻri sinfda, shuning uchun faqat bitta had qoladi: minus nol butun oʻndan toʻqqizning logarifmi. Bitlarda — nol butun mingdan bir yuz ellik ikki, natlarda — nol butun mingdan bir yuz besh, beshinchi maʼruzadagi sonning oʻzi.**
    *All the probability is on the true class, so only one term is left: minus the log of zero point nine. In bits, zero point one five two; in nats, zero point one zero five, the very number from Lecture 5.*
    ▸ −log₂ 0.9 = 0.152 bit; −ln 0.9 = 0.105 nat
14. **Bitta sinoptik ikki bit toʻladi. Turli sinoptiklarni solishtirsak-chi? Keyingi boʻlimda.**
    *One forecaster paid two bits. What if we compare different forecasters? The next section.*

### 6-boʻlim · Section 6 — Uchta sinoptik, bitta shahar · Three forecasters, one town
1. **Uchta sinoptik, bitta shahar, oʻsha uch yuz oltmish kun. Har bir ustunning koʻk asosi — entropiya, bir butun yuzdan yetmish besh. Ustidagi rangli qism — har bir sinoptik ortiqcha toʻlagan qism.**
   *Three forecasters, one town, the same three hundred and sixty days. The blue base of each bar is the entropy, one point seven five. The coloured cap is what each forecaster pays on top.*
   ▸ three stacked bars on the dashed line at 1.75
2. **Iqlimni biladigan sinoptik: bir butun yuzdan yetmish besh bit. Hech narsa isrof boʻlmadi — lekin baribir nol emas.**
   *The one who knows the climate: one point seven five bits. Nothing wasted, and still not zero.*
3. **Toʻrtalasini teng deb oʻylagan sinoptik: ikki bit, kuniga nol butun yuzdan yigirma besh bit isrof.**
   *The one who assumes all four equal: two bits, wasting zero point two five bits a day.*
4. **Uch yuz oltmish kunga qarasak, iqlimni biladigan sinoptik olti yuz oʻttiz bit, tekis ishongan esa yetti yuz yigirma bit toʻlaydi. Farq — toʻqson bit, uchinchi boʻlimda topgan sonimizning oʻzi.**
   *Over the three hundred and sixty days, the one who knows the climate pays six hundred and thirty bits, and the uniform one seven hundred and twenty. The difference is ninety bits, the very number we found in section three.*
   ▸ 630 vs 720 bits; 720 − 630 = 90
5. **Uchinchi sinoptik har doim «quyoshli» deydi: quyoshga nol butun oʻndan toʻqqiz ehtimol beradi, boʻronga esa bor-yoʻgʻi nol butun yuzdan bir. U ikki butun yuzdan ellik yetti bit toʻlaydi, nol butun yuzdan sakson ikki bit isrof.**
   *The third always says "sunny": they give the sun zero point nine and the storm only zero point zero one. They pay two point five seven bits, wasting zero point eight two.*
   ▸ the red cap: 2.57, +0.82
6. **Notoʻgʻri ishonch eng qattiq jazolanadi. Boʻron kelgan kuni bu sinoptik yuzning ikki asosli logarifmini, yaʼni olti butun oʻndan olti bit toʻlaydi. Haqiqat esa boʻron uchun bor-yoʻgʻi uch bit soʻraydi.**
   *Confidence that is wrong is punished hardest. On the day the storm arrives this forecaster pays the base-two log of a hundred, six point six bits. The truth asks only three bits for a storm.*
   ▸ the storm's cost: 3 bits (truth) vs 6.6 bits (always sunny)
7. **Entropiya — pol. U dunyoning oʻzi noaniq ekanidan keladi, modelimiz xato ekanidan emas. Uchala ustun ham shu poldan pastga tusha olmaydi.**
   *The entropy is a floor. It comes from the world being uncertain, not from our model being wrong. None of the three bars can go below it.*
   ▸ the dashed floor line highlighted
8. **Shuning uchun nol kross-entropiya maqsad emas. Bir xil pikselli ikkita rasm haqiqatan ham yetmish foiz holda bir sinfga, oʻttiz foiz holda boshqasiga tegishli boʻlsa, eng yaxshi model ham ularda nol butun yuzdan sakson sakkiz bit yoʻqotish toʻlaydi. Bu toʻrtinchi boʻlimdagi egri chiziqning nol butun oʻndan yettidagi qiymati.**
   *So a cross-entropy of zero is not the target. If two images with identical pixels truly carry one label seventy percent of the time and another thirty, even the best model pays zero point eight eight bits of loss on them. That is the curve of section four at zero point seven.*
   ▸ the binary entropy curve with p = 0.7 marked at 0.88
9. **Sunʼiy intellektda shovqinli belgilanganlarda oʻqitish yoʻqotishi nolga yaqin boʻlgan model oʻrganmagan, yodlab olgan. Yoʻqotishni berilganlarning oʻz noaniqligi bilan solishtiramiz.**
   *In AI, a model whose training loss is near zero on noisy labels has memorised, not learned. We compare the loss with the data's own uncertainty.*
10. ⏸ **Keling, oʻzimiz sinab koʻraylik. Videoni toʻxtating. «Har doim quyoshli» deydigan sinoptik quyoshli kunda nechta bit toʻlaydi? Haqiqiy iqlimni biladigan sinoptik-chi?**
    *Let's try it ourselves. Pause the video. How many bits does the always-sunny forecaster pay on a sunny day? And the one who knows the true climate?*
11. **Nol butun oʻndan toʻqqizning logarifmi: taxminan nol butun mingdan bir yuz ellik ikki bit. Iqlimni biladigan esa bir bit toʻlaydi. Quyoshli kunda «har doim quyoshli» yutadi! Lekin bulutli, yomgʻirli va boʻronli kunlarda u toʻrt bitdan oltidan ortiq bitgacha toʻlaydi, va oʻrtachada yutqazadi.**
    *The log of zero point nine: about zero point one five two bits. The one who knows the climate pays one bit. On a sunny day "always sunny" wins! But on cloudy, rainy and stormy days they pay from over four to over six bits, and lose on average.*
    ▸ per-day costs of the always-sunny forecaster: 0.15, 4.3, 4.6, 6.6 bits, against 1, 2, 3, 3
12. **Kross-entropiya ikki qismga boʻlinadi: dunyo bilmaydigan qism — entropiya, uni kamaytirib boʻlmaydi, va modelimiz xato qiladigan qism — rangli qopqoq. Faqat ikkinchisi bizning qoʻlimizda.**
    *Cross-entropy splits into two parts: what the world does not know, the entropy, which cannot be reduced, and what our model gets wrong, the coloured cap. Only the second is ours to reduce.*
    ▸ H(p, q) = H(p) + (rangli qism)
13. **Mana shu bilan nolinchi qismni tugatamiz. Rangli qopqoqning oʻz nomi va formulasi bor. Birinchi qismda.**
    *With this we finish part zero. The coloured cap has a name and a formula of its own. In part one.*

## Part 1 — KL divergensiya va oʻzaro axborot
▸ part card "1-qism · KL divergensiya va oʻzaro axborot"

### 7-boʻlim · Section 7 — KL divergensiya · KL divergence
1. **Nolinchi qismni eslaylik: tekis ishongan sinoptik kuniga ikki bit toʻladi, haqiqat esa bir butun yuzdan yetmish besh bit turadi. Bir butun yuzdan yetmish besh — ob-havoning aybi. Ortiqcha nol butun yuzdan yigirma besh esa — sinoptikning oʻz aybi.**
   *Let's recall part zero: the uniform forecaster paid two bits a day where the truth cost one point seven five. The one point seven five was the weather's fault. The extra zero point two five was the forecaster's own.*
   ▸ the uniform bar split: 1.75 "ob-havo" + 0.25 "sinoptik"
2. **Polni ayirsak, ishonch qanchalik xato ekanini oʻlchaydigan toza son qoladi, dunyoning oʻz noaniqligisiz. Bu Kulbak–Leybler divergensiyasi, qisqacha key el divergensiya.**
   *Subtracting the floor leaves a clean measure of how wrong the belief is, with the world's own uncertainty taken out. That is the Kullback–Leibler divergence, KL divergence for short.*
3. **Formula: Key el pi, kyu teng kross-entropiya minus entropiya, yaʼni pi ay karra pi ay ni kyu ay ga boʻlganimizning ikki asosli logarifmi yigʻindisi. Haqiqat pi boʻlganda kyu ga ishonishning ortiqcha narxi.**
   *The formula: KL of p, q equals the cross-entropy minus the entropy, that is the sum of p i times the base-two log of p i over q i. The extra cost of believing q when the truth is p.*
   ▸ D_KL(p ‖ q) = H(p, q) − H(p) = Σ pᵢ log₂(pᵢ / qᵢ)
4. **Ob-havoda: tekis sinoptik uchun ikki minus bir butun yuzdan yetmish besh — nol butun yuzdan yigirma besh bit. «Har doim quyoshli» uchun ikki butun yuzdan ellik yetti minus bir butun yuzdan yetmish besh — nol butun yuzdan sakson ikki bit.**
   *For the weather: for the uniform forecaster, two minus one point seven five, zero point two five bits. For "always sunny", two point five seven minus one point seven five, zero point eight two bits.*
   ▸ the three caps relabelled as KL: 0, 0.25, 0.82
5. **Uchta tomondan oʻqiymiz. Savollar tilida: notoʻgʻri daraxt tufayli kuniga beriladigan ortiqcha savollar. Ustunlar tilida: rangli qopqoqning balandligi. Formula tilida: har bir natijada ishonch haqiqatdan necha baravar adashganining logarifmi, haqiqiy chastotalar bilan oʻrtachalangan.**
   *We read it from three sides. In the language of questions: the extra questions a day caused by the wrong tree. In the language of bars: the height of the coloured cap. In the language of the formula: the log of how many times the belief misjudges each outcome, averaged with the real frequencies.*
6. **Key el hech qachon manfiy emas va faqat ishonch mukammal boʻlganda, yaʼni kyu pi ga teng boʻlganda nol. Bu oldingi qoidaning boshqacha aytilishi: haqiqatni eng arzon tasvirlaydigan narsa — haqiqatning oʻzi.**
   *KL is never negative, and it is zero only for a perfect belief, when q equals p. That is the earlier rule said another way: the cheapest description of the truth is the truth itself.*
   ▸ D_KL ≥ 0, = 0 only at q = p
7. **Kross-entropiyani minimallashtirish — key el ni minimallashtirish demak. Ular entropiya qadar farq qiladi, entropiya esa modelga umuman bogʻliq emas. Shuning uchun ikkalasining minimumi bitta nuqtada.**
   *Minimising cross-entropy is minimising KL. They differ by the entropy, and the entropy does not depend on the model at all. So both have their minimum at the same point.*
8. **Sunʼiy intellektda klassifikatorni oʻqitganimizda yoʻqotish funksiyasi kross-entropiya boʻlsa ham, amalda biz model taqsimotini haqiqiy taqsimotga key el boʻyicha yaqinlashtiryapmiz. Polni hech qanday model oʻzgartira olmaydi.**
   *In AI, when we train a classifier the loss is called cross-entropy, but in effect we are moving the model's distribution towards the true one in KL. No model can move the floor.*
9. ⏸ **Keling, oʻzimiz sinab koʻraylik. Videoni toʻxtating. Sinoptik bulutli va yomgʻirni almashtirib yubordi: yarim, sakkizdan bir, toʻrtdan bir, sakkizdan bir. Uning kross-entropiyasi va key el divergensiyasi qancha?**
   *Let's try it ourselves. Pause the video. A forecaster swapped cloudy and rain: a half, an eighth, a quarter, an eighth. What are their cross-entropy and KL divergence?*
10. **Bu sinoptik quyoshli kunga bir bit, bulutliga uch, yomgʻirga ikki, boʻronga uch bit sarflaydi. Haqiqiy ulushlar bilan oʻrtachalasak — bir butun mingdan sakkiz yuz yetmish besh bit. Key el — undan bir butun yuzdan yetmish beshni ayiramiz: nol butun mingdan bir yuz yigirma besh bit.**
    *This forecaster spends one bit on a sunny day, three on cloudy, two on rain and three on storm. Averaged with the true shares: one point eight seven five bits. The KL is that minus one point seven five: zero point one two five bits.*
    ▸ ½·1 + ¼·3 + ⅛·2 + ⅛·3 = 1.875; 1.875 − 1.75 = 0.125
11. **Key el ikki taqsimot orasidagi farqni oʻlchaydi. Oltinchi maʼruzadagi aprior va aposterior taqsimotlar orasida-chi? Keyingi boʻlimda.**
    *KL measures the gap between two distributions. What about between Lecture 6's prior and posterior? The next section.*

### 8-boʻlim · Section 8 — Yuz tong bizga qancha oʻrgatdi · How much did 100 mornings tell us
1. **Oltinchi maʼruzadagi soat yetti qirqdagi avtobusga qaytamiz. Aprior taqsimot — Beta sakkiz, ikki, va har tongni bittadan qoʻshib boramiz.**
   *We go back to Lecture 6's seven forty bus. The prior is Beta eight, two, and we add the mornings one at a time.*
2. **Eslab olaylik: Beta sakkiz, ikki oʻnta tongga teng edi. Oʻn tongdan keyin aposterior taqsimot Beta oʻn toʻrt, olti, yuz tongdan keyin esa Beta yetmish olti, oʻttiz toʻrt boʻlgan edi.**
   *Let's recall: Beta eight, two was worth ten mornings. After ten mornings the posterior was Beta fourteen, six, and after a hundred, Beta seventy-six, thirty-four.*
   ▸ Lecture 6's three curves: Beta(8, 2), Beta(14, 6), Beta(76, 34)
3. **Har tongdan keyin aposterior taqsimotning aprior taqsimotdan key el divergensiyasini hisoblaymiz. Bu son ishonchimiz boshlangʻich nuqtadan qanchalik uzoqlashganini bitlarda aytadi.**
   *After each morning we compute the KL divergence of the posterior from the prior. This number says, in bits, how far our belief has moved from where it started.*
   ▸ the KL(posterior ‖ prior) curve over the hundred mornings
4. **Bu — oʻrganishning oʻlchovi. Nolinchi tongda aposterior taqsimot aprior taqsimotning oʻzi, key el aniq nol. Oʻn tongdan keyin — nol butun yuzdan oltmish olti bit, yuz tongdan keyin — bir butun yuzdan yetmish olti bit.**
   *This is learning, measured. At zero mornings the posterior is the prior, and the KL is exactly zero. After ten mornings, zero point six six bits; after a hundred, one point seven six.*
   ▸ the green point at 10 (0.66) and the orange point at 100 (1.76)
5. **Egri chiziq tekis emas, va bu haqiqiy. Bir necha oʻz vaqtida kelgan tongdan keyin kechikkan avtobus aposterior taqsimotni aprior tomonga qaytaradi. Masalan, oʻttiz tongdan keyin key el bor-yoʻgʻi nol butun yuzdan oltmish toʻqqiz edi — oʻn tongdagidan sal koʻp xolos.**
   *The curve is jagged, and that is real. A late bus after a run of on-time ones pushes the posterior back towards the prior. After thirty mornings, for example, the KL was only zero point six nine: barely more than after ten.*
6. **Aprior taqsimot oʻnta tongga teng edi, shuning uchun birinchi oʻn tong bilganimizni taxminan ikki baravar oshirdi. Keyingi bir butun oʻndan bir bit uchun esa yana toʻqson tong kerak boʻldi. Har bir yangi bit avvalgisidan qimmatroq.**
   *The prior was worth ten mornings, so the first ten roughly doubled what we knew. The next one point one bits took ninety more mornings. Each new bit costs more than the one before.*
7. **Boshqacha aytganda: Key el nafaqat «model qanchalik xato» degan savolga, balki «dalil ishonchimizni qanchalik siljitdi» degan savolga ham javob beradi.**
   *Put another way: KL answers not only "how wrong is the model?" but also "how far did the evidence shift our belief?".*
8. **Sunʼiy intellektda tajribani rejalashtirishda shu son ishlatiladi: qaysi tajriba ishonchimizni eng koʻp siljitishi kutilsa, oʻshani birinchi oʻtkazamiz. Qoʻshimcha oʻqitilgan model asl modeldan qanchalik uzoqlashganini ham shunday oʻlchaymiz.**
   *In AI, this number is used to plan experiments: we run first the experiment expected to shift our belief the most. We measure how far a fine-tuned model has drifted from the original the same way.*
9. ⏸ **Keling, oʻzimiz sinab koʻraylik. Videoni toʻxtating. Oʻn tongdan keyin key el nol butun yuzdan oltmish olti, yuz tongdan keyin bir butun yuzdan yetmish olti. Keyingi toʻqson tong qancha bit qoʻshdi?**
   *Let's try it ourselves. Pause the video. After ten mornings the KL is zero point six six, after a hundred one point seven six. How many bits did the next ninety mornings add?*
10. **Bir butun yuzdan yetmish oltidan nol butun yuzdan oltmish oltini ayiramiz: bir butun oʻndan bir bit. Birinchi oʻn tong deyarli shuncha berdi, toʻqson tong esa bor-yoʻgʻi shuncha.**
    *One point seven six minus zero point six six: one point one bits. The first ten mornings gave almost as much, and ninety more gave only that.*
    ▸ 1.76 − 0.66 = 1.10
11. **Biz key el ni ikki taqsimot orasidagi «masofa» kabi ishlatyapmiz. Lekin u haqiqatan ham masofami? Keyingi boʻlimda.**
    *We are using KL like a "distance" between two distributions. But is it really a distance? The next section.*

### 9-boʻlim · Section 9 — KL masofa emas · Why KL is not a distance
1. **Masofa simmetrik: Toshkentdan Samarqandgacha qancha boʻlsa, Samarqanddan Toshkentgacha ham shuncha. Key el esa simmetrik emas.**
   *A distance is symmetric: from Tashkent to Samarkand is as far as from Samarkand to Tashkent. KL is not.*
2. **Oʻsha ikki ishonchni almashtiraylik. Pi — haqiqiy iqlim, kyu — «har doim quyoshli» sinoptik. Key el pi, kyu — nol butun yuzdan sakson ikki bit, key el kyu, pi esa — nol butun yuzdan ellik toʻrt bit.**
   *Let's swap the same two beliefs. P is the true climate, q the always-sunny forecaster. KL of p, q is zero point eight two bits, while KL of q, p is zero point five four bits.*
   ▸ D_KL(p ‖ q) = 0.82 vs D_KL(q ‖ p) = 0.54
3. **Nega tartib muhim? Key el pi, kyu haqiqatda roʻy beradigan natijalar boʻyicha oʻrtachalanadi, shuning uchun u haqiqiy boʻronni «deyarli imkonsiz» deb atagan kyu ni qattiq jazolaydi. Teskarisida esa oʻrtacha kyu boʻyicha olinadi, va boʻronli kunlar deyarli hisobga kirmaydi.**
   *Why does the order matter? KL of p, q averages over the outcomes that really happen, so it punishes a q that calls a real storm nearly impossible. Reversed, the average is taken under q, and the stormy days barely count.*
   ▸ the storm bar weighted by p (⅛) vs by q (0.01)
4. **Amaliy natijasi: Key el pi, kyu ni minimallashtirsak, kyu haqiqat ehtimol bergan hamma joyga ehtimol qoʻyishga majbur — ehtiyotkor, keng tarqalgan moslik chiqadi. Key el kyu, pi ni minimallashtirsak, kyu bitta choʻqqini tanlab, qolganini eʼtiborsiz qoldirishi mumkin. Bir xil ikki taqsimotdan ikki xil javob.**
   *The practical consequence: minimising KL of p, q forces q to put probability wherever the truth has any, giving a cautious, spread-out fit. Minimising KL of q, p lets q pick one peak and ignore the rest. Two different answers from the same two distributions.*
   ▸ a two-peaked truth; one q spread over both, another q sitting on one peak
5. **Sunʼiy intellektda key el — jilov. Inson fikri bilan kuchaytirib oʻrganishda sozlangan model bilan asl model orasiga key el jarimasi qoʻyiladi: model mukofot ortidan quvib, maʼnosiz gaplarga ketib qolmasligi uchun. Jarimaning kuchini biz tanlaymiz — beshinchi modulda.**
   *In AI, KL is a leash. In reinforcement learning from human feedback, a KL penalty is put between the tuned model and the original one, so that chasing reward does not drag the model into gibberish. We choose the penalty's strength: Module 5.*
6. **Bilim distillyatsiyasida kichik model katta modelning faqat eng yaxshi javobini emas, butun taqsimotini takrorlashga oʻrgatiladi. Maqsad — ular orasidagi key el. Variatsion avtokodlovchida esa key el hadi yashirin fazoni standart Gauss taqsimoti yaqinida ushlab turadi.**
   *In knowledge distillation, a small model is trained to match a large model's whole distribution, not just its top answer. The objective is the KL between them. In a variational autoencoder, a KL term keeps the latent space near a standard Gaussian.*
7. **Buni eslab qolamiz: yoʻqotish funksiyasidagi key el hadi doim jilov. U «berilganlarga moslash, lekin mana shu taqsimotdan uzoqlashma» deydi.**
   *Remember this one: a KL term in a loss is always a leash. It says "fit the data, but do not wander far from this distribution".*
8. ⏸ **Keling, oʻzimiz sinab koʻraylik. Videoni toʻxtating. Haqiqiy iqlim va tekis sinoptik uchun ikkala yoʻnalishni hisoblang: Key el pi, kyu va key el kyu, pi.**
   *Let's try it ourselves. Pause the video. For the true climate and the uniform forecaster, compute both directions: KL of p, q and KL of q, p.*
9. **Ikkalasi ham nol butun yuzdan yigirma besh bit chiqadi! Bu tasodif: bu juftlikda ikki yoʻnalish teng boʻlib qoldi. Bitta misol simmetriyani isbotlamaydi — «har doim quyoshli» juftligida nol butun yuzdan sakson ikki va nol butun yuzdan ellik toʻrt koʻrdik.**
   *Both come out at zero point two five bits! That is a coincidence: for this pair the two directions happen to be equal. One example does not prove symmetry: for the always-sunny pair we saw zero point eight two and zero point five four.*
   ▸ 0.25 = 0.25 (this pair) beside 0.82 ≠ 0.54
10. **Hozirgacha bitta noaniq narsani oʻlchadik. Bitta narsaga qarash boshqasi haqidagi noaniqlikni qanchalik kamaytiradi? Keyingi boʻlimda.**
    *So far we measured one uncertain thing. How much does looking at one thing reduce our uncertainty about another? The next section.*

### 10-boʻlim · Section 10 — Oʻzaro axborot · Mutual information
1. **Entropiya bitta noaniq narsani baholaydi. Koʻp savollarda esa ikkita narsa bor, va biz bilmoqchimiz: biriga qarash ikkinchisi haqidagi noaniqlikni kamaytiradimi?**
   *Entropy scores one uncertain thing. Most questions involve two, and we want to know: does looking at one reduce our uncertainty about the other?*
2. **Bugun yogʻin boʻladimi — yomgʻir yoki boʻron? Ertalab soat yettida osmonga qarash nimadir aytadi. Bugungi sana juft sonmi — hech narsa aytmaydi. Kundalik gapda ikkalasi ham «axborot», lekin haqiqatda faqat bittasi.**
   *Will today be wet, rain or storm? A look at the sky at seven in the morning tells us something. Whether today's date is even tells us nothing. In everyday talk both are "information"; really, only one is.*
   ▸ a grey sky at 7:00 and a calendar page with an even date
3. **Ikkinchi maʼruzada bogʻliq emaslikni tekshirgan edik: ey va bi ning birgalikdagi ehtimoli ey ning ehtimoli karra bi ning ehtimoliga teng boʻlsa, ular bogʻliq emas. Bu «ha yoki yoʻq» javobi edi. Endi bizga miqdor kerak: qanchalik bogʻliq?**
   *In Lecture 2 we tested independence: if the joint probability of A and B equals P of A times P of B, they are independent. That was a yes-or-no answer. Now we want an amount: how strongly related?*
   ▸ P(A ∩ B) = P(A) P(B) → "ha / yoʻq" → "qancha?"
4. **Retsept: qaramasdan oldin yogʻin haqidagi noaniqligimizni oʻlchaymiz, qaragandan keyin qolganini oʻlchaymiz va ayiramiz.**
   *The recipe: measure our uncertainty about rain before looking, measure what is left after, and subtract.*
5. **Qaragandan keyin qolgan noaniqlik shartli entropiya deyiladi: har bir javob ichidagi entropiya, javoblar ehtimoli bilan oʻrtachalangan. Ayirma esa oʻzaro axborot: ay eks, uay teng uay ning entropiyasi minus eks maʼlum boʻlgandagi uay ning entropiyasi.**
   *The uncertainty left after looking is called the conditional entropy: the entropy within each answer, averaged over the answers. The difference is the mutual information: I of X, Y equals H of Y minus H of Y given X.*
   ▸ I(X; Y) = H(Y) − H(Y | X)
6. **Yogʻin — yomgʻir yoki boʻron, ulushi sakkizdan bir qoʻshuv sakkizdan bir, yaʼni toʻrtdan bir. Uning entropiyasi — toʻrtinchi boʻlimdagi son: nol butun yuzdan sakson bir bit.**
   *Wet means rain or storm: an eighth plus an eighth, a quarter. Its entropy is the number from section four: zero point eight one bits.*
   ▸ P(yogʻin) = 0.25, H = 0.81
7. **Ertalab osmon kulrang boʻlsa, yogʻin ehtimoli nol butun yuzdan ellik yettiga koʻtariladi, ochiq boʻlsa — nol butun yuzdan sakkizga tushadi. Bu ikkinchi maʼruzadagi shartli ehtimollik: kulrang osmonli va yogʻinli kunlar ulushi nol butun oʻndan ikki, kulrang osmonli kunlar ulushi nol butun yuzdan oʻttiz besh, boʻlsak — nol butun yuzdan ellik yetti.**
   *If the sky is grey in the morning, the chance of wet rises to zero point five seven; if clear, it falls to zero point zero eight. This is Lecture 2's conditional probability: the share of grey and wet days is zero point two, the share of grey days zero point three five, and dividing gives zero point five seven.*
   ▸ P(yogʻin | kulrang) = 0.20 / 0.35 = 0.57; P(yogʻin | ochiq) = 0.08
8. **Har bir javob ichidagi entropiyani oʻrtachalasak, nol butun oʻndan olti bit qoladi. Demak, kulrang osmon bizga nol butun mingdan ikki yuz oʻn ikki bit beradi — dastlabki noaniqlikning taxminan toʻrtdan bir qismi.**
   *Averaging the entropy within each answer leaves zero point six bits. So the grey sky gives us zero point two one two bits, about a quarter of the uncertainty we started with.*
   ▸ 0.81 − 0.60 = 0.212
9. **Oʻzaro axborot hech qachon manfiy emas va aynan bogʻliq boʻlmaganda nol — ikkinchi maʼruzadagi testning miqdoriy shakli. U simmetrik ham: osmon yogʻin haqida qancha aytsa, yogʻin osmon haqida ham shuncha aytadi. Teskari tomondan hisoblasak ham nol butun mingdan ikki yuz oʻn ikki chiqadi.**
   *Mutual information is never negative, and exactly zero when the two are independent: the quantitative version of Lecture 2's test. It is symmetric too: what the sky says about rain, rain says about the sky. Computed the other way round, it is zero point two one two again.*
   ▸ H(Y) − H(Y | X) = H(X) − H(X | Y) = 0.212
10. **Yana bir tomondan: oʻzaro axborot — key el divergensiya. Osmon va yogʻin bogʻliq boʻlmaganda, kulrang va yogʻinli kunlar ulushi nol butun yuzdan toʻqqizga yaqin boʻlardi. Haqiqatda esa u nol butun oʻndan ikki. Haqiqiy birgalikdagi taqsimotning «bogʻliq emas» taqsimotidan key el divergensiyasi — yana nol butun mingdan ikki yuz oʻn ikki bit.**
    *From one more side: mutual information is a KL divergence. If sky and rain were independent, the share of grey wet days would be about zero point zero nine. In fact it is zero point two. The KL of the real joint distribution from the "independent" one is zero point two one two bits again.*
    ▸ joint 0.20 vs product 0.09; KL(joint ‖ product) = 0.212
11. **Sunʼiy intellektda modelni oʻqitishdan oldin belgilarni oʻzaro axborot bilan baholaymiz: har bir belgi maqsad haqida qancha bit beradi? Bu belgilarni tanlash deyiladi.**
    *In AI, before training a model we score features by mutual information: how many bits does each one buy about the target? That is called feature selection.*
12. ⏸ **Keling, oʻzimiz sinab koʻraylik. Videoni toʻxtating. Juft sanali kunlarda ham, toq sanali kunlarda ham yogʻin ulushi toʻrtdan bir. Sana yogʻin haqida necha bit aytadi?**
    *Let's try it ourselves. Pause the video. On even-dated days and on odd-dated days alike, the share of wet days is a quarter. How many bits does the date tell us about rain?*
13. **Nol bit. Qaragandan keyin ham noaniqlik nol butun yuzdan sakson bir boʻlib qoladi. Ikkinchi maʼruza tilida: juft sana va yogʻin birgalikdagi ehtimoli nol butun mingdan bir yuz yigirma besh — toʻrtdan bir karra yarim. Bogʻliq emas.**
    *Zero bits. After looking, the uncertainty stays at zero point eight one. In Lecture 2's language: the joint probability of an even date and a wet day is zero point one two five, a quarter times a half. Independent.*
    ▸ 0.25 × 0.5 = 0.125; I = 0
14. **Ertalab faqat bitta narsani tekshirishga vaqtimiz bor. Qaysi savolni beramiz? Keyingi boʻlimda.**
    *We have time to check only one thing in the morning. Which question do we ask? The next section.*

### 11-boʻlim · Section 11 — Qaysi savolni beramiz · Which morning question should we ask
1. **Uchta nomzod: osmon kulrangmi, shamol gʻarbdanmi, sana juftmi. Uzuq chiziq — yogʻin entropiyasi, nol butun yuzdan sakson bir bit: oʻrganish mumkin boʻlgan hamma narsa.**
   *Three candidates: is the sky grey, is the wind from the west, is the date even. The dashed line is the entropy of wet, zero point eight one bits: everything there is to learn.*
   ▸ three bars under the dashed line at 0.81
2. **Kulrang osmon — nol butun mingdan ikki yuz oʻn ikki bit. Gʻarbiy shamol — nol butun mingdan yigirma ikki bit: u ham bogʻliq, lekin yogʻin ehtimolini faqat nol butun yuzdan oʻttiz uchga suradi. Kulrang osmondan taxminan oʻn baravar kam foydali. Juft sana — aniq nol.**
   *Grey sky: zero point two one two bits. West wind: zero point zero two two bits. It is related too, but it only moves the chance of wet to zero point three three: about ten times less useful than the grey sky. Even date: exactly zero.*
   ▸ the bars: 0.212, 0.022, 0
3. **Bu tartib — belgilarni tanlashning oʻzi: har bir nomzod kirish haqiqatan necha bit olib keladi?**
   *That ranking is feature selection itself: how many bits does each candidate input actually bring?*
4. **Qaror daraxti har bir tugunda shu savolni beradi: qaysi savol boʻyicha boʻlaman? Har bir nomzodni axborot ortishi bilan baholaydi — boʻlishdan oldingi entropiya minus ikki shoxdagi oʻrtacha entropiya.**
   *A decision tree asks this question at every node: which question do I split on? It scores each candidate by information gain: the entropy before the split minus the average entropy of the two branches.*
   ▸ a tree node trying three splits, each scored in bits
5. **Bu oʻninchi boʻlimdagi formulaning oʻzi, oʻzgarishsiz: uay ning entropiyasi minus eks maʼlum boʻlgandagi uay ning entropiyasi. Birinchi modulning beshinchi maʼruzasidagi daraxt aynan kulrang osmonni shamoldan, shamolni sanadan yuqori qoʻygan hisobni bajaradi.**
   *That is the formula of section ten, unchanged: H of Y minus H of Y given X. The tree in Module 1, Lecture 5 runs exactly the calculation that ranked the grey sky above the wind, and the wind above the date.*
6. **Demak, nolinchi qismdagi savol oʻyini shunchaki oʻxshatish emas edi. Qaror daraxti — har qadamda eng foydali savolni tanlab oʻynaladigan yigirma savol oʻyini, va keyingi savolni entropiya tanlaydi.**
   *So the guessing game of part zero was not just an analogy. A decision tree is twenty questions played greedily, choosing the most useful question at each step, and entropy picks the next question.*
7. **Sunʼiy intellektning boshqa joylarida ham: kontrastiv oʻrganish bitta narsaning ikki koʻrinishi orasidagi oʻzaro axborotni oshiradi. Zamonaviy tasvirlar belgilanganlarsiz shunday oʻrganiladi — ikkinchi va uchinchi modullarda.**
   *Elsewhere in AI too: contrastive learning raises the mutual information between two views of the same thing. That is how modern representations are learned without labels: Modules 2 and 3.*
8. ⏸ **Keling, oʻzimiz sinab koʻraylik. Videoni toʻxtating. Gʻarbiy shamolni bilgandan keyin yogʻin haqida nol butun yuzdan yetmish toʻqqiz bit noaniqlik qoladi. Shamol necha bit berdi?**
   *Let's try it ourselves. Pause the video. After we know whether the wind is from the west, zero point seven nine bits of uncertainty about wet remain. How many bits did the wind give?*
9. **Nol butun yuzdan sakson birdan nol butun yuzdan yetmish toʻqqizni ayiramiz: taxminan nol butun yuzdan ikki bit. Kulrang osmonning nol butun mingdan ikki yuz oʻn ikkisi yonida — taxminan oʻndan bir.**
   *Zero point eight one minus zero point seven nine: about zero point zero two bits. Beside the grey sky's zero point two one two, about a tenth.*
   ▸ 0.81 − 0.79 ≈ 0.02
10. **Keyingi maʼruzalarda: sakkizinchi maʼruzada entropiya biz bilganlarimizni hisobga olgan holda taqsimot maksimallashtiradigan miqdor sifatida qaytadi — Gauss, Bernulli va Puasson taqsimotlari shu bitta tamoyildan chiqadi. Oʻninchi maʼruzada modelning yangi berilganlardagi oʻrtacha minus logarifmik haqiqatga oʻxshashligi — uning haqiqatga nisbatan kross-entropiyasi, perpleksiya aynan shuni koʻrsatadi.**
    *Coming up: in Lecture 8, entropy returns as the quantity a distribution maximises given what we know, and the Gaussian, the Bernoulli and the Poisson all fall out of that one principle. In Lecture 10, a model's average negative log-likelihood on new data is its cross-entropy against reality, which is what perplexity reports.*
11. **Keling, maʼruzani yakunlaylik. Entropiya — aniqlash uchun kerak boʻlgan «ha yoki yoʻq» savollarining oʻrtacha soni, yaʼni oʻrtacha ajablanish. Aniqlikda u nol, tekis taqsimotda eng katta.**
    *Let's wrap up the lecture. Entropy is the average number of yes-or-no questions needed to pin down an outcome, the average surprise. It is zero for certainty and largest for a uniform distribution.*
12. **Kross-entropiya — haqiqat pi boʻlganda kyu ishonchidan foydalanishning narxi. U entropiyadan hech qachon past emas, belgilangan sinf bilan esa beshinchi maʼruzadagi yoʻqotish funksiyasining oʻzi.**
    *Cross-entropy is the price of using belief q when reality is p. It is never below the entropy, and with a labelled class it is Lecture 5's loss itself.*
13. **Key el divergensiya — ularning ayirmasi, kamaytirsa boʻladigan qism. U manfiy emas, faqat kyu pi ga teng boʻlganda nol, va simmetrik emas. Oʻzaro axborot — eks uay haqida necha bit berishi, bogʻliq boʻlmaganda aniq nol.**
    *The KL divergence is their difference, the part that can be removed. It is never negative, zero only when q equals p, and not symmetric. Mutual information is how many bits X gives about Y, exactly zero when they are independent.*
14. **Bitta jumlani eslab qolamiz: yoʻqotishimiz — kross-entropiya, uning poli — dunyoning oʻz noaniqligi, poldan yuqoridagi hamma narsa esa hali kamaytirish mumkin boʻlgan key el divergensiya.**
    *One sentence to keep: our loss is a cross-entropy, its floor is the world's own uncertainty, and everything above that floor is a KL divergence we can still remove.*
15. **Mana shu bilan yettinchi maʼruzamizni tugatamiz. Keyingi maʼruzada eksponensial oila bilan tanishamiz.**
    *With this we finish our seventh lecture. In the next lecture we meet the exponential family.*
