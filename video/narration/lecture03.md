# Lecture 3 — video narration (draft 1, for approval)

**One video for the whole lecture**, in two parts like the slides: Part 0 (Tasodifiy miqdorlar) = sections 1–6,
Part 1 (Asosiy taqsimotlar) = sections 7–11. Each section: problem first → concept as the answer → one AI use → a
hands-on pause → the question the next section answers. One running example, the coffee shop, carries the whole
lecture, as in the slides.

**Rules applied:** berilganlar (data) / belgilanganlar (labels); "we", never "you" (only *Videoni toʻxtating*);
Latin letters spoken by their English names (eks, en, pi, key, ey, bi); Greek letters keep theirs (mu, lambda, alfa);
numbers spelled for the ear, digits on screen. A screen label is words only; every number beside it comes from the data.
**Numbers:** every figure comes from `video/statistics/raw/l03_numbers.json` / `l03_figures.txt`
(`capture_l03.py`, unit-tested in `test_l03.py` against the slides, the figure script's output and these lines).
The coffee-shop arrivals are the figure script's simulation (3000 windows), and the narration says so.

**Terms to confirm** (new in this lecture): tasodifiy miqdor (random variable) · ehtimollik taqsimoti (probability
mass function) · matematik kutilma, qisqasi kutilma (expectation) · dispersiya (variance) · standart chetlanish
(standard deviation) · siljitish va masshtablash (shifting and scaling) · standartlashtirish (standardizing) ·
lotereya (raffle) · ruletka (roulette) · tikish (a bet) · Bernulli taqsimoti · binomial taqsimot · kategorial /
multinomial taqsimot · Puasson taqsimoti · Dirixle taqsimoti · oʻrtacha tezlik (rate, λ) · oraliq (a time window) ·
softmaks (softmax) · kuchaytirib oʻrganish (reinforcement learning) · mavzular modeli (topic model, LDA) · normal
taqsimot (the Gaussian).

Format per line: **UZ** (your voice) · *EN* (English track) · ▸ visual.

---

## Lecture opening
▸ title card "3-maʼruza" → the two parts
0. **Assalomu alaykum, aziz doʻstlar. Uchinchi maʼruzamizga xush kelibsiz. Bu maʼruza ham ikki qismdan iborat. Nolinchi qismda tasodifiy miqdorlarni oʻrganamiz, birinchi qismda esa asosiy taqsimotlar bilan tanishamiz.**
   *Hello, dear friends, and welcome to our third lecture. It also has two parts. In part zero we study random variables, and in part one we meet the key distributions.*

## Part 0 — Tasodifiy miqdorlar
▸ part card "0-qism · Tasodifiy miqdorlar"

### 1-boʻlim · Section 1 — Tasodifiy miqdor · Random variables
1. **Oʻtgan maʼruzalarda ehtimolni hodisaga bogʻladik: «kubikda juft son chiqdi», «talaba avtobusda qatnaydi». Lekin koʻp savollar son haqida: nechta, qancha, qancha vaqt.**
   *In the last lectures we attached probability to events: "the die shows an even number", "the student takes the bus". But most questions are about a number: how many, how much, how long.*
2. **Ikkita kubik tashlaymiz va chiqqan sonlarni qoʻshamiz. Tashlash — tasodif, yigʻindi esa tasodif bergan son.**
   *We roll two dice and add them up. The roll is chance; the sum is the number chance produced.*
   ▸ two dice land on 3 and 4; "X = 7"
3. **Har bir natijaga son biriktiradigan qoidani tasodifiy miqdor deymiz va uni katta eks harfi bilan belgilaymiz. Natija uch va toʻrt boʻlsa, eks yetti boʻladi.**
   *A rule that attaches a number to every outcome is called a random variable, and we write it as a capital X. If the outcome is three and four, X is seven.*
4. **Eksning qiymatlarini sanab chiqish mumkin: ikkidan oʻn ikkigacha. Bunday miqdorni diskret deymiz.**
   *The values of X can be listed: two to twelve. We call such a variable discrete.*
5. **Endi har bir qiymat qanchalik ehtimolli ekanini yozamiz. Ikki kubikda oʻttiz oltita teng ehtimolli juftlik bor. Yigʻindi ikki faqat bitta yoʻl bilan chiqadi: bir va bir. Yetti esa olti yoʻl bilan chiqadi.**
   *Now we write down how likely each value is. Two dice give thirty-six equally likely pairs. A sum of two comes only one way: one and one. Seven comes six ways.*
   ▸ the 36 pairs as a 6 × 6 grid, coloured by sum; they stack into bars of 1, 2, … 6, … 1
6. **Demak, yetti chiqish ehtimoli oʻttiz oltidan olti, yaʼni oltidan bir. Bu ikki chiqishidan olti marta koʻp.**
   *So the probability of a seven is six in thirty-six, one in six: six times more likely than a two.*
7. **Har bir qiymatga ehtimol biriktiradigan bu roʻyxatni ehtimollik taqsimoti deymiz. Ehtimollar manfiy boʻlmaydi va ularning yigʻindisi bir, chunki eks qandaydir qiymatni albatta oladi.**
   *This list that gives each value its probability is called the probability mass function. The probabilities are never negative, and they add up to one, because X must take some value.*
   ▸ the bars become p(x); "Σ p(x) = 1"
8. **Shuning uchun stol oʻyinlarini yetti hal qiladi. Monopoliyada toʻq sariq uylar qamoqxonadan olti-toʻqqiz katak narida turadi: qamoqdan chiqqan oʻyinchi eng koʻp aynan shu yerga yetib keladi.**
   *That is why seven decides board games. In Monopoly, the orange properties sit six to nine squares past Jail: the stretch a player leaving Jail is most likely to reach.*
9. **Endi qahvaxonani olaylik. Eks — bitta buyurtmadagi pishiriqlar soni. Nol pishiriq — nol butun oʻndan yetti, bitta — nol butun oʻndan ikki, ikkita — nol butun oʻndan bir. Yigʻindi bir.**
   *Now a coffee shop. X is the number of pastries in one order. No pastry: zero point seven. One: zero point two. Two: zero point one. They add up to one.*
   ▸ three bars 0.7, 0.2, 0.1; the coffee shop runs through the whole lecture
10. **Bu birinchi maʼruzadagi chastotalar jadvaliga oʻxshaydi. Farqi bitta: u yerda oʻlchangan tanlanmadagi sonlar edi, bu yerda esa hali kelmagan mijoz uchun ehtimollar.**
    *This looks like the frequency table from the first lecture. One difference: those were counts in a sample we measured; these are probabilities for a customer who has not come in yet.*
11. **Sunʼiy intellektda model koʻpincha bitta javob emas, aynan shunday taqsimot beradi: har bir mumkin boʻlgan javobga ehtimol, yigʻindisi bir. Masalan, tilli model keyingi soʻz uchun shunday qiladi.**
    *In AI, a model often outputs not a single answer but exactly such a distribution: a probability for every possible answer, adding up to one. A language model does this for the next word.*
12. ⏸ **Keling, oʻzimiz sinab koʻraylik. Videoni toʻxtating. Ikki kubik yigʻindisi oʻn bir chiqish ehtimoli qancha?**
    *Let's try it ourselves. Pause the video. What is the probability that two dice add up to eleven?*
13. **Oʻn bir ikki yoʻl bilan chiqadi: besh va olti, olti va besh. Oʻttiz oltidan ikki, yaʼni oʻn sakkizdan bir.**
    *Eleven comes two ways: five and six, six and five. Two in thirty-six: one in eighteen.*
14. **Taqsimot har bir qiymatni beradi. Lekin bitta son bilan aytmoqchi boʻlsak-chi: oʻrtacha nechta pishiriq? Buni keyingi boʻlimda koʻramiz.**
    *A distribution gives every value. But what if we want one number: how many pastries on average? That is the next section.*

### 2-boʻlim · Section 2 — Matematik kutilma · Expectation
1. **Har bir qiymatni uning ehtimoliga koʻpaytiramiz va hammasini qoʻshamiz. Buni matematik kutilma deymiz. Uni mu harfi bilan ham belgilaymiz — birinchi maʼruzadagi bosh toʻplam oʻrtachasi kabi, chunki u aynan shu.**
   *We multiply each value by its probability and add everything up. This is the expectation. We also write it as mu, the letter of the first lecture's population mean, because that is exactly what it is.*
   ▸ E[X] = Σ x p(x) = μ
2. **Qahvaxonada: nol karra nol butun oʻndan yetti, qoʻshuv bir karra nol butun oʻndan ikki, qoʻshuv ikki karra nol butun oʻndan bir. Natija nol butun oʻndan toʻrt.**
   *In the coffee shop: zero times zero point seven, plus one times zero point two, plus two times zero point one. The result is zero point four.*
   ▸ the three products appear under the bars and add up to 0.4
3. **Demak, yuzta mijoz taxminan qirqta pishiriq oladi.**
   *So one hundred customers buy about forty pastries.*
4. **Lekin nol butun oʻndan toʻrt pishiriqli buyurtma boʻlmaydi. Kutilma bitta mijozni bashorat qilmaydi; u uzoq muddatdagi oʻrtacha qiymat.**
   *But no order holds zero point four pastries. An expectation does not predict any single customer; it is the long-run average.*
5. **Xoʻp, endi lotereyani koʻraylik. Maktab besh yuzta chiptani ikki dollardan sotadi. Bitta chipta toʻrt yuz dollarlik velosiped yutadi.**
   *Now a raffle. A school sells five hundred tickets at two dollars each. One ticket wins a four-hundred-dollar bicycle.*
   ▸ 500 tickets, one of them gold
6. **Eks — chipta egasining sof yutugʻi. Besh yuzdan bir ehtimol bilan u uch yuz toʻqson sakkiz dollar yutadi, qolgan holda ikki dollar yoʻqotadi.**
   *X is the buyer's net gain. With probability one in five hundred they win three hundred and ninety-eight dollars; otherwise they lose two dollars.*
7. **Kutilma — minus bir dollar yigirma sent. Maktab yigʻilgan ming dollardan olti yuz dollarini oʻziga oladi.**
   *The expectation is minus one dollar twenty. The school keeps six hundred of the thousand dollars it raises.*
   ▸ 398 · 1/500 − 2 · 499/500 = −1.20
8. **Hech bir xaridor aynan bir dollar yigirma sent yoʻqotmaydi: yo ikki dollar yoʻqotadi, yo uch yuz toʻqson sakkiz dollar yutadi. Lekin maktab shu songa qarab aniq reja tuza oladi.**
   *No single buyer loses exactly one dollar twenty: they lose two dollars or win three hundred and ninety-eight. Yet the school can budget on that number exactly.*
9. **Sunʼiy intellektda modelni oʻqitganda xatoning kutilmasini kichraytiramiz: model uchratishi mumkin boʻlgan barcha misollar boʻyicha oʻrtacha xatoni.**
   *In AI, training a model makes the expected loss smaller: the average error over all the examples the model may ever meet.*
10. ⏸ **Keling, oʻzimiz sinab koʻraylik. Videoni toʻxtating. Bitta kubik tashlaymiz. Chiqqan sonning kutilmasi qancha?**
    *Let's try it ourselves. Pause the video. We roll one die. What is the expectation of the number it shows?*
11. **Har bir yoq oltidan bir. Birdan oltigacha qoʻshsak yigirma bir, oltiga boʻlsak uch butun oʻndan besh. Yana kubikda yoʻq son.**
    *Each face is one in six. One to six adds up to twenty-one; divided by six, three point five. Again, a number the die never shows.*
12. **Lekin barcha misollarni hech qachon koʻrmaymiz. Unda kutilmani qanday topamiz? Keyingi boʻlimda.**
    *But we never see all the examples. How do we find the expectation then? That is the next section.*

### 3-boʻlim · Section 3 — Kutilma va tanlanma oʻrtachasi · Expectation and the sample mean
1. **Birinchi maʼruzadagi tanlanma oʻrtachasi bizda bor berilganlardan hisoblanardi. Kutilma esa jarayonning xossasi: u birorta berilgan paydo boʻlmasidan oldin ham aniq.**
   *The first lecture's sample mean was computed from data we had. The expectation is a property of the process: it is fixed before any data exists.*
2. **Kubikni qayta-qayta tashlaymiz va har safar shu paytgacha chiqqan sonlarning oʻrtachasini hisoblaymiz. Buni uch marta, bir-biridan mustaqil qilamiz.**
   *We roll a die again and again, and each time we compute the mean of the rolls so far. We do this three times, independently.*
   ▸ three running-mean curves draw left to right on a log axis; a dashed line at 3.5
3. **Oʻnta tashlashdan keyin uchala oʻrtacha: toʻrt butun oʻndan bir, uch butun oʻndan olti, uch butun oʻndan toʻqqiz. Ular bir-biridan ancha farq qiladi.**
   *After ten rolls the three means read four point one, three point six and three point nine. They disagree a lot.*
4. **Ikki ming tashlashdan keyin: uch butun yuzdan ellik toʻrt, uch butun yuzdan ellik bir, uch butun yuzdan qirq toʻqqiz. Uchalasi ham uch butun oʻndan beshga yaqinlashdi.**
   *After two thousand rolls: three point five four, three point five one, three point four nine. All three have closed in on three point five.*
5. **Demak, tanlanma oʻrtachasi kutilma tomon boradi. Koʻproq berilganlar yigʻishning foydasi aynan shunda. Bu qanchalik tez boʻlishini beshinchi maʼruzada aniq koʻramiz.**
   *So the sample mean heads for the expectation. That is why collecting more data helps at all. How fast it happens, we make precise in Lecture 5.*
6. **Sunʼiy intellektda xatoning kutilmasini aynan shunday baholaymiz: bir toʻplam misollar boʻyicha oʻrtacha xatoni olamiz. Toʻplam qanchalik katta boʻlsa, baho shunchalik aniq.**
   *In AI, this is exactly how we estimate the expected loss: we take the average loss over a batch of examples. The bigger the batch, the better the estimate.*
7. ⏸ **Keling, oʻzimiz sinab koʻraylik. Videoni toʻxtating. Birinchi urinishda oʻnta tashlashdan keyin oʻrtacha toʻrt butun oʻndan bir edi. U kutilmadan qanchaga farq qiladi? Ikki ming tashlashdan keyin-chi?**
   *Let's try it ourselves. Pause the video. In the first run, the mean after ten rolls was four point one. How far is that from the expectation? And after two thousand rolls?*
8. **Oʻnta tashlashdan keyin nol butun oʻndan olti. Ikki ming tashlashdan keyin bor-yoʻgʻi nol butun mingdan oʻttiz toʻqqiz.**
   *After ten rolls, zero point six. After two thousand, only zero point zero three nine.*
9. **Lekin oʻrtacha qiymat hamma narsani aytmaydi: ikki jarayonning oʻrtachasi bir xil boʻlib, oʻzi butunlay boshqacha boʻlishi mumkin. Buni keyingi boʻlimda oʻlchaymiz.**
   *But the mean does not tell everything: two processes can share a mean and still behave completely differently. We measure that in the next section.*

### 4-boʻlim · Section 4 — Dispersiya · Variance
1. **Birinchi maʼruzada tarqoqlikni dispersiya bilan oʻlchadik. Tasodifiy miqdorda ham xuddi shunday: dispersiya — oʻrtachadan farq kvadratining kutilmasi.**
   *In the first lecture we measured spread with the variance. For a random variable it is the same: the variance is the expected squared distance from the mean.*
   ▸ Var(X) = E[(X − μ)²] = E[X²] − μ²
2. **Hisoblash uchun qulayroq yoʻl bor: qiymatlarni kvadratga koʻtaramiz, ularning kutilmasini olamiz va oʻrtachaning kvadratini ayiramiz.**
   *There is an easier way to compute it: square the values, take their expectation, and subtract the square of the mean.*
3. **Qahvaxonada kvadratlar kutilmasi nol butun oʻndan olti. Undan nol butun oʻndan toʻrtning kvadratini ayiramiz: nol butun yuzdan qirq toʻrt. Standart chetlanish — undan kvadrat ildiz, taxminan nol butun yuzdan oltmish olti.**
   *In the coffee shop, the expectation of the squares is zero point six. We subtract zero point four squared: zero point four four. The standard deviation is its square root, about zero point six six.*
4. **Endi ikkinchi lotereya. Yana besh yuzta chipta ikki dollardan. Lekin bu safar bitta katta sovrin emas, ellikta sakkiz dollarlik sovrin.**
   *Now a second raffle. Again five hundred tickets at two dollars. But this time, instead of one big prize, fifty prizes of eight dollars.*
5. **Oʻndan bir ehtimol bilan xaridor olti dollar yutadi, qolgan holda ikki dollar yoʻqotadi. Kutilma yana minus bir dollar yigirma sent — aynan bir xil.**
   *With probability one in ten the buyer gains six dollars; otherwise they lose two. The expectation is again minus one dollar twenty: exactly the same.*
6. **Lekin standart chetlanish birinchi lotereyada oʻn yetti dollar sakson yetti sent, ikkinchisida esa bor-yoʻgʻi ikki dollar qirq sent.**
   *But the standard deviation is seventeen dollars eighty-seven in the first raffle, and only two dollars forty in the second.*
   ▸ the two distributions side by side: a far spike at 398 against a near one at 6; the two σ
7. **Kutilma maktab qancha pul yigʻishini aytadi. Dispersiya esa xaridor nimani boshdan kechirishini aytadi. Birinchisi — omad oʻyini, ikkinchisi — kichik chegirma, va kutilma ularni ajrata olmaydi.**
   *The expectation says what the school raises. The variance says what the buyer goes through. The first is a lottery, the second a mild discount, and no expectation can tell them apart.*
8. **Sunʼiy intellektda ham shunday: oʻrtacha xatosi bir xil ikki modeldan dispersiyasi kichigi ishonchliroq, chunki uning xatolari kamdan-kam katta boʻladi.**
   *In AI it is the same: of two models with the same average error, the one with the smaller variance is more reliable, because its errors are rarely large.*
9. ⏸ **Keling, oʻzimiz sinab koʻraylik. Videoni toʻxtating. Ikkinchi lotereyaning dispersiyasi qancha?**
   *Let's try it ourselves. Pause the video. What is the variance of the second raffle?*
10. **Kvadratlar kutilmasi: oʻttiz olti karra nol butun oʻndan bir, qoʻshuv toʻrt karra nol butun oʻndan toʻqqiz — yetti butun oʻndan ikki. Undan bir butun yuzdan qirq toʻrtni ayiramiz: besh butun yuzdan yetmish olti.**
    *The expectation of the squares: thirty-six times zero point one, plus four times zero point nine, which is seven point two. We subtract one point four four: five point seven six.*
11. **Kutilma manfiy boʻlsa, uzoq oʻynash nimaga olib keladi? Buni ruletkada koʻramiz.**
    *When the expectation is negative, where does playing longer lead? We see it at the roulette wheel.*

### 5-boʻlim · Section 5 — Ruletka · Roulette
1. **Ruletkada qizilga tikamiz. Yutsak, tikkan pulimizcha yutamiz. Lekin oʻttiz yettita katakdan faqat oʻn sakkiztasi qizil.**
   *At roulette we bet on red. A win pays as much as we bet. But only eighteen of the thirty-seven pockets are red.*
   ▸ a wheel: 18 red, 18 black, 1 green
2. **Har bir dollarga kutilma — minus oʻttiz yettidan bir, taxminan minus ikki butun oʻndan yetti sent. Gʻildirak oldingi natijani eslamaydi, shuning uchun bu son hech qachon yaxshilanmaydi.**
   *The expectation per dollar is minus one in thirty-seven, about minus two point seven cents. The wheel has no memory, so this number never improves.*
3. **Kutilmalar qoʻshiladi: en marta tiksak, kutilayotgan balans en karra shu son. Uzoq oʻynash yoʻqotganni qaytarish imkoniyati emas — yoʻqotishning oʻzi shu.**
   *Expectations add: after n bets, the expected balance is n times that number. Playing longer is not a chance to win it back; it is the mechanism of the loss.*
   ▸ the expected balance falls in a straight line as the number of bets grows
4. **Shuning uchun foydada boʻlish ehtimoli kamayib boradi: yuz tikishdan keyin oʻttiz olti foiz, ming tikishdan keyin oʻn toʻqqiz foiz, oʻn ming tikishdan keyin nol butun oʻndan uch foiz.**
   *So the chance of being ahead drains away: thirty-six percent after a hundred bets, nineteen percent after a thousand, zero point three percent after ten thousand.*
   ▸ P(ahead) bars: 36 %, 19 %, 0.3 %
5. **Yutgan kecha bunga zid emas. Yuz tikishdan keyin oʻttiz olti foiz — foydada boʻlish oddiy hol, va aynan u odamlarni qaytarib olib keladi. Lekin balans pastga siljiydi, va foydada boʻlgan oxirgi lahza albatta keladi.**
   *A winning night does not contradict this. Thirty-six percent after a hundred bets: being ahead is ordinary, and it is exactly what brings people back. But the balance drifts down, and there is always a last moment in profit.*
6. **«Yutqazsam, tikishni ikki baravar oshiraman» degan usul ham ishlamaydi. Ming dollar bilan ketma-ket toʻqqizta yutqazishni koʻtarsa boʻladi: jami besh yuz oʻn bir dollar. Keyingi tikish uchun besh yuz oʻn ikki dollar kerak, u esa qolmagan.**
   *The doubling system does not work either. With a thousand dollars we can survive nine losses in a row: five hundred and eleven dollars in all. The next bet needs five hundred and twelve, and that money is gone.*
   ▸ 1 + 2 + 4 + … + 256 = 511; the next stake, 512, is crossed out
7. **Bu taxminan toʻrt yuz oʻyinda bir marta boʻladi, va kutilma baribir har oʻyinda minus yigirma yetti sent. Koʻp kichik yutuq bitta katta yoʻqotishga aylanadi.**
   *That happens about once in four hundred sessions, and the expectation stays at minus twenty-seven cents a session. Many small wins turn into one large loss.*
8. **Sunʼiy intellektda kuchaytirib oʻrganishda ham agent har qadamdagi mukofotlar kutilmasining yigʻindisini oshiradi. Har qadamda kutilmasi manfiy boʻlgan strategiya, boshida qanchalik omadli boʻlmasin, uzoq muddatda yutqazadi.**
   *In AI, a reinforcement-learning agent likewise maximizes the sum of the expected rewards of its steps. A strategy whose expected reward per step is negative loses in the long run, however lucky its start.*
9. ⏸ **Keling, oʻzimiz sinab koʻraylik. Videoni toʻxtating. Ming marta bir dollardan tiksak, kutilayotgan balans qancha?**
   *Let's try it ourselves. Pause the video. If we bet one dollar a thousand times, what is the expected balance?*
10. **Ming karra minus oʻttiz yettidan bir: taxminan minus yigirma yetti dollar.**
    *A thousand times minus one in thirty-seven: about minus twenty-seven dollars.*
11. **Har bir natijani ikki baravar oshirsak yoki unga doimiy son qoʻshsak, kutilma va dispersiya qanday oʻzgaradi? Keyingi boʻlimda.**
    *If we double every outcome, or add a fixed amount to it, how do the expectation and the variance change? That is the next section.*

### 6-boʻlim · Section 6 — Siljitish va masshtablash · Shifting and scaling
1. **Qahvaxonada bitta pishiriq ikki dollar turadi. Demak, pishiriqdan tushum — ikki karra eks.**
   *In the coffee shop a pastry costs two dollars. So the pastry revenue is two times X.*
2. **Kutilma ham ikki baravar boʻladi: sakson sent. Standart chetlanish ham ikki baravar: bir dollar oʻttiz uch sent.**
   *The expectation doubles too: eighty cents. So does the standard deviation: one dollar thirty-three.*
   ▸ the bars move apart: 0, 2 and 4 dollars
3. **Har bir buyurtmada yana uch dollarlik qahva bor. Unda hisob — ikki karra eks qoʻshuv uch, va uning kutilmasi uch dollar sakson sent.**
   *Every order also includes a three-dollar coffee. Then the bill is two times X plus three, and its expectation is three dollars eighty.*
4. **Dispersiya esa oʻzgarmaydi: bir butun yuzdan yetmish olti. Doimiy uch dollar hech qanday noaniqlik qoʻshmaydi — u butun taqsimotni choʻzmasdan surib qoʻyadi.**
   *The variance does not change: one point seven six. A fixed three dollars adds no uncertainty; it moves the whole distribution without stretching it.*
   ▸ the bars slide right by 3 without changing shape
5. **Qoida shunday: ey karra eks qoʻshuv bi ning kutilmasi ey karra eks kutilmasi qoʻshuv bi ga teng. Dispersiyasi esa ey ning kvadrati karra eks dispersiyasi. Kvadrat chiqadi, chunki dispersiya kvadrat birliklarda oʻlchanadi.**
   *The rule: the expectation of a times X plus b is a times the expectation of X, plus b. Its variance is a squared times the variance of X. The square appears because variance is measured in squared units.*
   ▸ E[aX + b] = a E[X] + b,  Var(aX + b) = a² Var(X)
6. **Sunʼiy intellektda bu qoidani belgilarni standartlashtirishda ishlatamiz: har bir qiymatdan oʻrtachani ayirib, standart chetlanishga boʻlamiz. Natijada kutilma nol, dispersiya bir boʻladi, va barcha belgilar bir xil oʻlchovga keladi.**
   *In AI we use this rule to standardize features: subtract the mean from every value and divide by the standard deviation. The expectation becomes zero and the variance one, so every feature is on the same scale.*
   ▸ (X − 0.4) / 0.66: the bars move to mean 0, spread 1
7. ⏸ **Keling, oʻzimiz sinab koʻraylik. Videoni toʻxtating. Pishiriq uch dollar boʻlsa, tushumning kutilmasi va dispersiyasi qancha?**
   *Let's try it ourselves. Pause the video. If a pastry costs three dollars, what are the expectation and the variance of the revenue?*
8. **Kutilma — uch karra nol butun oʻndan toʻrt, bir dollar yigirma sent. Dispersiya — toʻqqiz karra nol butun yuzdan qirq toʻrt, uch butun yuzdan toʻqson olti.**
   *The expectation is three times zero point four: one dollar twenty. The variance is nine times zero point four four: three point nine six.*
9. **Mana shu bilan nolinchi qismni tugatamiz. Bir necha shakl qayta-qayta uchraydi; ulardan birini tanib olsak, hisob tayyor boʻladi. Birinchi qismda shu shakllar bilan tanishamiz.**
   *That completes part zero. A few shapes keep reappearing; once we recognize one, the calculation comes ready-made. In part one we meet those shapes.*

## Part 1 — Asosiy taqsimotlar
▸ part card "1-qism · Asosiy taqsimotlar"

### 7-boʻlim · Section 7 — Bernulli taqsimoti · The Bernoulli distribution
1. **Toʻrtta kundalik savolni olaylik. Bu mijoz pishiriq oldimi? Keyingi oʻnta mijozdan nechtasi oldi? Bu mijoz qaysi stakanni tanladi? Keyingi oʻn daqiqada nechta mijoz kiradi? Toʻrt savol — toʻrt xil shakl.**
   *Take four everyday questions. Did this customer buy a pastry? How many of the next ten did? Which cup size did this customer pick? How many customers walk in during the next ten minutes? Four questions, four different shapes.*
   ▸ the four questions, each with its name: Bernoulli, binomial, categorical, Poisson
2. **Birinchisidan boshlaymiz: bitta «ha yoki yoʻq» savoli. Javob «ha» boʻlsa bir, «yoʻq» boʻlsa nol. «Ha» ehtimolini pi deymiz. Bu Bernulli taqsimoti.**
   *We start with the first: one yes-or-no question. The answer is one for yes and zero for no. We call the probability of yes p. This is the Bernoulli distribution.*
3. **Tanga uchun pi — nol butun oʻndan besh. Yangi tugʻilgan chaqaloqning qiz boʻlishi uchun — taxminan nol butun yuzdan qirq toʻqqiz.**
   *For a coin, p is zero point five. For a newborn being a girl, about zero point four nine.*
4. **Kutilma pi ga teng, dispersiya esa pi karra bir minus pi.**
   *The expectation equals p, and the variance is p times one minus p.*
   ▸ E[Y] = p,  Var(Y) = p(1 − p)
5. **Qahvaxonada buyurtmada hech boʻlmaganda bitta pishiriq boʻlish ehtimoli nol butun oʻndan ikki qoʻshuv nol butun oʻndan bir, yaʼni nol butun oʻndan uch. Dispersiya — nol butun oʻndan uch karra nol butun oʻndan yetti, nol butun yuzdan yigirma bir.**
   *In the coffee shop, the chance an order holds at least one pastry is zero point two plus zero point one: zero point three. The variance is zero point three times zero point seven: zero point two one.*
6. **Dispersiya pi nol butun oʻndan besh boʻlganda eng katta, pi nol yoki bir boʻlganda esa nolga teng: javobi oldindan maʼlum savolda noaniqlik yoʻq.**
   *The variance is largest at p equal to zero point five, and zero at p equal to zero or one: a question whose answer is already known carries no uncertainty.*
   ▸ the parabola p(1 − p), peak 0.25 at p = 0.5
7. **Sunʼiy intellektda ikki sinfli klassifikator, masalan «spammi yoki yoʻqmi», aynan Bernulli taqsimotining pi sini beradi. Beshinchi maʼruzada koʻramiz: uning xato funksiyasi shu taqsimotdan kelib chiqadi.**
   *In AI, a two-class classifier, say "spam or not", outputs exactly the p of a Bernoulli distribution. In Lecture 5 we will see that its loss function comes from this distribution.*
8. ⏸ **Keling, oʻzimiz sinab koʻraylik. Videoni toʻxtating. Chaqaloqning qiz boʻlish ehtimoli nol butun yuzdan qirq toʻqqiz. Dispersiya qancha?**
   *Let's try it ourselves. Pause the video. A newborn is a girl with probability zero point four nine. What is the variance?*
9. **Nol butun yuzdan qirq toʻqqiz karra nol butun yuzdan ellik bir: taxminan nol butun yuzdan yigirma besh. Bu deyarli eng katta qiymat: natijani oldindan aytib boʻlmaydi.**
   *Zero point four nine times zero point five one: about zero point two five. That is almost the largest possible: the outcome cannot be called in advance.*
10. **Bitta mijoz emas, oʻnta mijozni sanasak-chi? Keyingi boʻlimda.**
    *And if we count ten customers instead of one? The next section.*

### 8-boʻlim · Section 8 — Binomial taqsimot · The binomial distribution
1. **Bir xil Bernulli tajribasini en marta, bir-biridan mustaqil takrorlaymiz va «ha» javoblarini sanaymiz. Bu son binomial taqsimotga ega.**
   *We repeat the same Bernoulli trial n times, independently, and count the yeses. That count has a binomial distribution.*
2. **Ikki shart muhim: har safar pi bir xil, va hech bir tajriba boshqasiga taʼsir qilmaydi. Ikkinchi maʼruzada paypoqlarni qaytarmasdan olganimizda ikkinchi shart buzilgan edi.**
   *Two conditions matter: the same p every time, and no trial affecting another. When we drew socks without replacement in Lecture 2, the second one broke.*
3. **Formulada ikki qism bor: «ha»lar qaysi tartibda kelishi mumkinligi soni va bitta shunday tartibning ehtimoli.**
   *The formula has two parts: the number of orders in which the yeses can arrive, and the probability of any one such order.*
   ▸ P(X = k) = C(n, k) pᵏ (1 − p)ⁿ⁻ᵏ, the two parts boxed
4. **Oʻnta mijoz, har biri nol butun oʻndan uch ehtimol bilan pishiriq oladi. Aynan uchtasi olish ehtimoli taxminan nol butun yuzdan yigirma yetti. Bu eng ehtimolli son, lekin u ham har toʻrt kunning bittasida boʻladi, xolos.**
   *Ten customers, each buying a pastry with probability zero point three. The chance that exactly three buy is about zero point two seven. It is the most likely count, and still it happens only about one batch in four.*
   ▸ Binomial(10, 0.3) bars; bar 3 lit; 120 × 0.027 × 0.0824 ≈ 0.267
5. **Kutilma — en karra pi, yaʼni uch. Dispersiya — en karra pi karra bir minus pi, ikki butun oʻndan bir; standart chetlanish taxminan bir butun yuzdan qirq besh.**
   *The expectation is n times p: three. The variance is n p times one minus p: two point one; the standard deviation is about one point four five.*
6. **Novvoy uchun bu muhim: aynan uchta pishiriq tayyorlash koʻpincha notoʻgʻri. Olti yoki undan koʻp mijoz olishi ehtimoli taxminan nol butun mingdan qirq yetti — yigirma kunning bittasida.**
   *That matters to the baker: baking exactly three is wrong most of the time. Six or more buyers has a chance of about zero point zero four seven: one batch in twenty.*
7. **Sunʼiy intellektda modelni yuzta test misolida tekshiramiz. Haqiqiy aniqligi toʻqson foiz boʻlsa, toʻgʻri javoblar soni binomial: kutilma toʻqson, standart chetlanish uch. Demak, boshqa yuzta misolda sakson yetti yoki toʻqson uch chiqishi oddiy hol.**
   *In AI we check a model on one hundred test examples. If its true accuracy is ninety percent, the number of correct answers is binomial: expectation ninety, standard deviation three. So on another hundred examples, eighty-seven or ninety-three would be quite ordinary.*
   ▸ Binomial(100, 0.9) around 90; 87 and 93 marked
8. ⏸ **Keling, oʻzimiz sinab koʻraylik. Videoni toʻxtating. Oʻnta mijozdan hech biri pishiriq olmasligi ehtimoli qancha?**
   *Let's try it ourselves. Pause the video. What is the chance that none of the ten customers buys a pastry?*
9. **Har biri nol butun oʻndan yetti ehtimol bilan olmaydi. Buni oʻn marta koʻpaytiramiz: taxminan nol butun mingdan yigirma sakkiz.**
   *Each one does not buy with probability zero point seven. We multiply that ten times: about zero point zero two eight.*
10. **Javob ikkita emas, koʻproq boʻlsa-chi? Masalan, kichik, oʻrta va katta stakan. Keyingi boʻlimda.**
    *What if there are more than two answers, like small, medium and large cups? The next section.*

### 9-boʻlim · Section 9 — Kategorial va multinomial taqsimot · Categorical and multinomial
1. **Mijoz uchta stakandan birini tanlaydi: kichik — nol butun oʻndan ikki, oʻrta — nol butun oʻndan besh, katta — nol butun oʻndan uch. Yigʻindi bir.**
   *A customer picks one of three cups: small, zero point two; medium, zero point five; large, zero point three. They add up to one.*
   ▸ three cups with their shares
2. **Bu kategorial taqsimot: javoblari ikkitadan koʻp Bernulli.**
   *This is the categorical distribution: a Bernoulli with more than two answers.*
3. **Oʻnta mijozdan har bir stakanni nechtasi olishini sanasak, multinomial taqsimot chiqadi: javoblari ikkitadan koʻp binomial. Kutilayotgan sonlar — en karra har bir ehtimol.**
   *If we count how many of ten customers take each cup, we get the multinomial distribution: a binomial with more than two answers. The expected counts are n times each probability.*
4. **Oʻnta mijozdan kutamiz: ikkita kichik, beshta oʻrta, uchta katta. Lekin har bir ertalab bundan farq qiladi — binomial ustunlarida koʻrganimizdek.**
   *From ten customers we expect two small, five medium and three large. But any single morning will differ, just as the binomial bars showed.*
   ▸ the expected counts 2, 5, 3 as bars
5. **Sunʼiy intellektda klassifikatorning chiqish qatlami har bir sinfga ehtimol beradi va ularning yigʻindisi bir. Bu softmaks, va u sinflar ustidagi kategorial taqsimot.**
   *In AI, a classifier's output layer gives every class a probability, and they add up to one. That is the softmax, and it is a categorical distribution over the classes.*
6. ⏸ **Keling, oʻzimiz sinab koʻraylik. Videoni toʻxtating. Yigirmata mijozdan har bir stakanga nechtadan kutamiz?**
   *Let's try it ourselves. Pause the video. From twenty customers, how many of each cup do we expect?*
7. **Toʻrtta kichik, oʻnta oʻrta, oltita katta.**
   *Four small, ten medium, six large.*
8. **Hozirgacha mijozlar sonini oldindan bilardik. Eshikdan nechta mijoz kirishi-chi? Keyingi boʻlimda.**
   *So far we knew how many customers there were. What about how many walk through the door? The next section.*

### 10-boʻlim · Section 10 — Puasson taqsimoti · The Poisson distribution
1. **Mijozlar bir-biridan mustaqil, oʻn daqiqada oʻrtacha toʻrttadan kiradi. Bitta oʻn daqiqalik oraliqda nechta mijoz kirishini sanaymiz.**
   *Customers arrive independently, four per ten minutes on average. We count how many walk in during one ten-minute window.*
2. **Bu sonni Puasson taqsimoti tasvirlaydi. Uning bitta parametri bor — oʻrtacha tezlik, lambda.**
   *This count follows the Poisson distribution. It has one parameter: the average rate, lambda.*
   ▸ P(X = k) = e^(−λ) λᵏ / k!
3. **Binomialdan farqi shundaki, bu yerda en yoʻq: kirmagan mijozlarni hech qachon sanamaymiz.**
   *The difference from the binomial is that there is no n: we never count the customers who did not walk in.*
4. **Puasson taqsimotining kutilmasi ham, dispersiyasi ham lambdaga teng. Bu kuchli daʼvo, va uni haqiqiy sonlarda tekshirish mumkin.**
   *The Poisson distribution's expectation and variance both equal lambda. That is a strong claim, and one we can check on real counts.*
5. **Uch ming oʻn daqiqalik oraliqni simulyatsiya qildik. Oʻrtacha — uch butun yuzdan toʻqson olti, dispersiya — uch butun yuzdan sakson toʻrt. Ikkalasi bir-biriga ham, toʻrtga ham yaqin.**
   *We simulated three thousand ten-minute windows. The mean is three point nine six, the variance three point eight four: close to each other, and to four.*
   ▸ bars = the 3000 simulated windows; dots = the Poisson formula
6. **Oʻn daqiqada hech kim kirmasligi ehtimoli taxminan nol butun mingdan oʻn sakkiz: ellik besh oraliqdan bittasi boʻsh. Sakkiz yoki undan koʻp kirishi ehtimoli taxminan nol butun mingdan ellik bir: yigirmadan bittasi — tirbandlik.**
   *The chance nobody walks in for ten minutes is about zero point zero one eight: one window in fifty-five is empty. Eight or more has a chance of about zero point zero five one: one in twenty is a rush.*
7. **Oʻn soatlik ish kunida oltmishta shunday oraliq bor. Demak, oʻrtacha atigi toʻrtta boʻlsa ham, kuniga taxminan uchta tirbandlik boʻladi. Xodimlarni rejalashtirishda shuni hisobga olamiz.**
   *A ten-hour day holds sixty such windows. So even at four on average, there are about three rushes a day. Staff planning has to allow for that.*
8. **Binomial va Puasson uchrashadi: oʻn daqiqani olti yuz soniyaga boʻlamiz, har soniyada mijoz kirishi ehtimoli bir yuz ellikdan bir. En karra pi yana toʻrt, va ikki taqsimot har bir sonda mingdan birdan kam farq qiladi.**
   *The binomial and the Poisson meet: split the ten minutes into six hundred seconds, each with a one in a hundred and fifty chance of an arrival. n times p is four again, and the two distributions differ by less than one in a thousand at every count.*
9. **Sunʼiy intellektda Puasson sonlarni modellashtiradi: masalan, model serveriga bir soniyada nechta soʻrov kelishini. Ehtimoli juda kichik son kelsa, bu gʻayrioddiy holat belgisi.**
   *In AI, the Poisson models counts, such as how many requests reach a model's server each second. A count with a tiny probability is a sign of something unusual.*
10. ⏸ **Keling, oʻzimiz sinab koʻraylik. Videoni toʻxtating. Oltmishta oraliqli bir kunda oʻrtacha nechta boʻsh oraliq boʻladi?**
    *Let's try it ourselves. Pause the video. In a day of sixty windows, how many empty windows do we expect?*
11. **Oltmish karra nol butun mingdan oʻn sakkiz: taxminan bitta.**
    *Sixty times zero point zero one eight: about one.*
12. **Hozirgacha barcha ehtimollarni bilamiz deb oldik. Ular qayerdan keladi va qanchalik ishonchli? Keyingi boʻlimda.**
    *So far we assumed we know all the probabilities. Where do they come from, and how sure are we? The next section.*

### 11-boʻlim · Section 11 — Dirixle taqsimoti · The Dirichlet distribution
1. **Stakan ulushlari — nol butun oʻndan ikki, besh va uch — bir necha ertalabki buyurtmalardan sanalgan. Ularni hech qachon aniq bilmaymiz.**
   *The cup shares, zero point two, zero point five and zero point three, were counted from a few mornings of orders. We never know them exactly.*
2. **Masalan, dastlabki toʻrtta buyurtma: bitta kichik, ikkita oʻrta, bitta katta. Toʻgʻridan-toʻgʻri oʻqisak, ulushlar nol butun yuzdan yigirma besh, ellik va yigirma besh. Lekin toʻrtta buyurtmadan keyin haqiqiy ulushlar boshqacha chiqsa ham ajablanmaymiz.**
   *Say the first four orders were one small, two medium and one large. Read literally, the shares are zero point two five, zero point five and zero point two five. But after only four orders, nobody would be surprised if the truth were different.*
3. **Demak, ulushlarning oʻzi noaniq. Bizga qaysi ulushlar toʻplami ishonchli ekanini aytadigan taqsimot kerak. Qiyin tomoni shundaki, javob bir vaqtda uchta son, va ularning yigʻindisi doim bir.**
   *So the shares themselves are uncertain. We need a distribution that says which sets of shares are plausible. The hard part is that the answer is three numbers at once, and they must always add up to one.*
4. **Dirixle taqsimoti aynan shuni qiladi: har safar bir yoʻla butun ulushlar toʻplamini tanlaydi, va ularning yigʻindisi doim bir.**
   *The Dirichlet distribution does exactly this: each draw is a whole set of shares at once, always adding up to one.*
   ▸ each draw is a thin line across small, medium, large
5. **Uning parametri alfa allaqachon koʻrilgan buyurtmalarni sanaydi. Taxminan toʻrtta buyurtmaga teng alfa — nol butun oʻndan sakkiz, ikki, bir butun oʻndan ikki — ulushlarni keng sochadi. Taxminan qirqtaga teng alfa — sakkiz, yigirma, oʻn ikki — ularni zich ushlaydi.**
   *Its parameter alpha counts the orders already seen. An alpha worth about four orders, zero point eight, two, one point two, scatters the shares widely. One worth about forty, eight, twenty, twelve, keeps them tight.*
   ▸ top: six draws with α = (0.8, 2, 1.2); bottom: six with α = (8, 20, 12) — the figure script's own draws
6. **Yangilash — bu sanash: yana uchta oʻrta stakan buyurtma qilinsa, alfaning oʻrtadagi soniga uch qoʻshamiz.**
   *Updating is counting: if three more medium cups are ordered, we add three to alpha's middle entry.*
7. **Sunʼiy intellektda softmaks ulushlarni beradi, lekin qanchalik ishonchli ekanini aytmaydi. Alfani bashorat qiladigan tarmoq esa «buni deyarli koʻrmaganman» deya oladi. Bu uchinchi moduldagi mavzular modeli va beshinchi moduldagi AlphaZero yurish ehtimollari ortidagi gʻoya.**
   *In AI, a softmax gives shares with no sense of how sure it is. A network that predicts alpha instead can say "I have barely seen this". That is the idea behind topic models in Module 3 and AlphaZero's move priors in Module 5.*
8. ⏸ **Keling, oʻzimiz sinab koʻraylik. Videoni toʻxtating. Alfa nol butun oʻndan sakkiz, ikki, bir butun oʻndan ikki edi. Yana uchta oʻrta stakan buyurtma qilindi. Yangi alfa qanday?**
   *Let's try it ourselves. Pause the video. Alpha was zero point eight, two, one point two. Three more medium cups were ordered. What is the new alpha?*
9. **Nol butun oʻndan sakkiz, besh, bir butun oʻndan ikki. Oʻrta stakanning kutilayotgan ulushi nol butun oʻndan beshdan taxminan nol butun yuzdan yetmish birga koʻtariladi.**
   *Zero point eight, five, one point two. The medium cup's expected share rises from zero point five to about zero point seven one.*
10. **Keling, maʼruzani yakunlaylik. Tasodifiy miqdor natijaga son biriktiradi; uning taqsimoti har bir qiymatga ehtimol beradi, va ularning yigʻindisi bir. Kutilma — tanlanma oʻrtachasining, dispersiya esa tarqoqlikning bosh toʻplamdagi koʻrinishi. Siljitish dispersiyani oʻzgartirmaydi, ey ga koʻpaytirish esa uni ey ning kvadratiga koʻpaytiradi.**
    *Let's wrap up the lecture. A random variable attaches a number to an outcome; its distribution gives each value a probability, and they add up to one. The expectation is the population version of the sample mean, and the variance of the spread. A shift leaves the variance alone; multiplying by a multiplies it by a squared.*
11. **Bernulli — bitta «ha yoki yoʻq», binomial — en tasidagi «ha»lar soni; kategorial va multinomial — xuddi shu juftlik, faqat javoblar koʻproq. Puasson oraliqdagi hodisalarni sanaydi, kutilmasi ham, dispersiyasi ham lambda. Dirixle esa ehtimollarning oʻzi ustidagi taqsimot.**
    *Bernoulli is one yes or no, binomial the number of yeses in n of them; categorical and multinomial are the same pair with more answers. The Poisson counts events in a window, with mean and variance both lambda. And the Dirichlet is a distribution over the probabilities themselves.*
12. **Mana shu bilan uchinchi maʼruzamizni tugatamiz. Keyingi maʼruzada uzluksiz tasodifiy miqdorlar va normal taqsimot bilan tanishamiz.**
    *That brings our third lecture to an end. In the next lecture, we meet continuous random variables and the Gaussian.*
