# Lecture 2 — video narration (draft 1, for approval)

**One video for the whole lecture**, in two parts like the slides: Part 0 (Shartli ehtimollik va erklilik) =
sections 1–6, Part 1 (Bayes teoremasi) = sections 7–10. Each section: problem first → concept as the answer → one AI
use → a hands-on pause → the question the next section answers.

**Rules applied:** berilganlar (data) / belgilanganlar (labels); "we", never "you" (only *Videoni toʻxtating*);
Latin letters spoken by their English names (ey, bi, di, ef); numbers spelled for the ear, digits on screen.
**Numbers:** every figure comes from `video/statistics/raw/l02_numbers.json` / `l02_figures.txt`
(`capture_l02.py`, asserted against the slides; Berkeley 1973 from the published counts).

**Terms to confirm** (new in this lecture): shartli ehtimollik (conditional probability) · daraxt diagrammasi (tree
diagram) · qaytarmasdan olish (without replacement) · kontingentlik jadvali (contingency table) · birgalikdagi /
marginal ehtimollik (joint / marginal) · surat / maxraj (numerator / denominator) · Simpson paradoksi · toʻla
ehtimollik formulasi (law of total probability) · aprior ehtimollik / haqiqatga oʻxshashlik / aposterior ehtimollik
(prior / likelihood / posterior) · dalil (evidence) · prokuror xatosi (prosecutor's fallacy) · yolgʻon signal (false
alarm) · asosiy ulush (base rate) · aniqlik (accuracy) · fakultet (a Berkeley department) · Bayes xulosasi (Bayesian
inference).

Format per line: **UZ** (your voice) · *EN* (English track) · ▸ visual.

---

## Lecture opening
▸ title card "2-maʼruza" → the two parts
0. **Assalomu alaykum, aziz doʻstlar. Ikkinchi maʼruzamizga xush kelibsiz. Bu maʼruza ham ikki qismdan iborat. Nolinchi qismda shartli ehtimollik va erklilikni oʻrganamiz, birinchi qismda esa Bayes teoremasini.**
   *Hello, dear friends, and welcome to our second lecture. It also has two parts. In part zero we study conditional probability and independence, and in part one, Bayes' theorem.*

## Part 0 — Shartli ehtimollik va erklilik
▸ part card "0-qism · Shartli ehtimollik va erklilik"

### 1-boʻlim · Section 1 — Shartli ehtimollik · Conditional probability
1. **Kubik tashlaymiz. Olti chiqish ehtimoli — oltidan bir.**
   *We roll a fair die. The chance of a six is one in six.*
   ▸ a die; six faces in a row, each 1/6
2. **Doʻstimiz kubikka qarab: «juft son chiqdi», deydi. Endi faqat ikki, toʻrt va olti qoldi. Olti chiqish ehtimoli endi uchdan bir.**
   *A friend peeks and says: "it's even." Only two, four and six are left. Now the chance of a six is one in three.*
   ▸ 1, 3, 5 grey out; 6 becomes 1/3
3. **Kubik joyidan qimirlamadi. Oʻzgargani — bizning bilganimiz. Yangi narsani bilsak, ehtimol ham oʻzgarishi kerak.**
   *The die never moved. What changed is what we know. When we learn something new, the probability has to change.*
4. **Buni shartli ehtimollik deymiz: ey sodir boʻlgandagi bi ning ehtimoli. Uni topish uchun ey va bi ning birga sodir boʻlish ehtimolini ey ning ehtimoliga boʻlamiz.**
   *We call it conditional probability: the probability of B given that A has happened. To find it, we divide the probability of A and B together by the probability of A.*
   ▸ P(B | A) = P(A ∩ B) / P(A); the bar read as "given"
5. **Kubikda: oltidan birni ikkidan birga boʻlamiz, uchdan bir chiqadi. Yaʼni uchta juft yoqdan bittasi.**
   *On the die: one sixth divided by one half is one third. One of the three even faces.*
6. **Xoʻp, endi kattaroq misol olaylik. Bir kursda yuzta talaba bor. Ulardan qirq beshtasi avtobusda qatnaydi. Demak, avtobusda qatnash ehtimoli nol butun yuzdan qirq besh.**
   *Now a bigger example. A year group has one hundred students. Forty-five of them take the bus. So the probability of taking the bus is zero point four five.*
   ▸ a 10 × 10 grid of students; 45 squares orange (bus)
7. **Endi bilamiz: talabaning velosipedi bor. Velosipedi bor talabalar oltmishta, ulardan avtobusda faqat oʻn beshtasi qatnaydi.**
   *Now we learn that the student owns a bike. Sixty students own one, and only fifteen of them take the bus.*
   ▸ the 40 without a bike grey out; a box around the 60
8. **Hech kimning yoʻli oʻzgarmadi. Faqat kimlarni sanayotganimiz oʻzgardi. Surat qirq beshdan oʻn beshga, maxraj yuzdan oltmishga tushdi: nol butun yuzdan yigirma besh.**
   *Nobody's journey changed. Only who we count changed. The top drops from forty-five to fifteen, the bottom from one hundred to sixty: zero point two five.*
   ▸ 45/100 = 0.45 morphs into 15/60 = 0.25
9. **Demak, shart namunalar fazosini toraytiradi: ey yangi fazoga aylanadi va biz faqat uning ichida sanaymiz.**
   *So a condition shrinks the sample space: A becomes the new sample space, and we count only inside it.*
10. **Sunʼiy intellektda klassifikator aynan shartli ehtimollikni beradi: masalan, xatda «bepul sovrin» degan soʻz boʻlsa, uning spam boʻlish ehtimoli.**
    *In AI, a classifier outputs exactly a conditional probability: for example, the probability that an email is spam given that it says "free prize".*
11. ⏸ **Keling, oʻzimiz sinab koʻraylik. Videoni toʻxtating. Velosipedi yoʻq talabaning avtobusda qatnash ehtimoli qancha?**
    *Let's try it ourselves. Pause the video. What is the probability that a student with no bike takes the bus?*
12. **Velosipedi yoʻq talabalar qirqta, ulardan oʻttiztasi avtobusda qatnaydi. Qirqdan oʻttiz, yaʼni nol butun yuzdan yetmish besh.**
    *Forty students have no bike, and thirty of them take the bus. Thirty out of forty: zero point seven five.*
13. **Bu hisobni bosqichma-bosqich chizsa ham boʻladi. Buni keyingi boʻlimda koʻramiz.**
    *We can also draw this calculation stage by stage. That is the next section.*

### 2-boʻlim · Section 2 — Daraxt diagrammasi · Tree diagrams
1. **Talabani ikki bosqichda tasvirlaymiz: avval velosipedi bormi, keyin avtobusda qatnaydimi.**
   *We describe a student in two stages: first, do they own a bike; then, do they take the bus.*
   ▸ the root "100 talaba" splits into two branches
2. **Har bir bosqich daraxtning shoxi boʻladi. Velosipedi bor — nol butun oʻndan olti, yoʻq — nol butun oʻndan toʻrt.**
   *Each stage is a branch of a tree. Owns a bike: zero point six. No bike: zero point four.*
3. **Velosipedi borlar ichida avtobusda qatnaydiganlar — nol butun yuzdan yigirma besh. Velosipedi yoʻqlar ichida esa — nol butun yuzdan yetmish besh.**
   *Among bike owners, the bus takers are zero point two five. Among students with no bike, zero point seven five.*
   ▸ the four second-stage branches grow
4. **Qoida oddiy: yoʻl boʻylab shoxlarni koʻpaytiramiz. Bu oʻtgan maʼruzadagi koʻpaytirish qoidasi.**
   *The rule is simple: we multiply along the path. That is last lecture's multiplication rule.*
5. **Velosipedi bor va avtobusda qatnaydi: nol butun oʻndan oltini nol butun yuzdan yigirma beshga koʻpaytiramiz, nol butun yuzdan oʻn besh chiqadi. Yaʼni oʻn besh talaba.**
   *Owns a bike and takes the bus: zero point six times zero point two five is zero point one five. That is fifteen students.*
   ▸ the top path lights up; 0.6 × 0.25 = 0.15 → 15
6. **Qolgan uchta yoʻl: qirq besh, oʻttiz va oʻn talaba. Toʻrtta yoʻl har bir talabani bir martadan qamraydi, shuning uchun koʻpaytmalar yigʻindisi birga teng.**
   *The other three paths: forty-five, thirty and ten students. The four paths cover every student exactly once, so the products add up to one.*
   ▸ 0.15 + 0.45 + 0.30 + 0.10 = 1
7. **Sunʼiy intellektda til modeli matnni xuddi shunday daraxt boʻylab yaratadi: har bir soʻz yangi shox, gapning ehtimoli esa yoʻl boʻylab koʻpaytma.**
   *In AI, a language model writes text by walking down exactly such a tree: each word is a new branch, and the sentence's probability is the product along the path.*
8. ⏸ **Keling, oʻzimiz sinab koʻraylik. Videoni toʻxtating. Daraxtni teskari tartibda chizamiz: avval avtobus, keyin velosiped. Birinchi ikki shoxda qanday sonlar turadi?**
   *Let's try it ourselves. Pause the video. We draw the tree the other way round: bus first, then bike. What numbers sit on the first two branches?*
9. **Avtobusda qatnaydiganlar — oʻn besh qoʻshuv oʻttiz, yaʼni qirq besh talaba: nol butun yuzdan qirq besh. Qatnamaydiganlar — nol butun yuzdan ellik besh.**
   *Bus takers: fifteen plus thirty, forty-five students: zero point four five. The rest: zero point five five.*
10. **Bu daraxtda ikkinchi bosqich birinchisiga bogʻliq edi. Bunday bogʻliqlik qayerdan keladi? Buni keyingi boʻlimda tortmadagi paypoqlar misolida koʻramiz.**
    *In this tree, the second stage depended on the first. Where does such dependence come from? We see it in the next section, with socks in a drawer.*

### 3-boʻlim · Section 3 — Ikkita paypoq · Two socks from the drawer
1. **Tortmada oʻnta paypoq bor: oltitasi qora, toʻrttasi oq. Qorongʻida ikkitasini olamiz. Ikkalasi ham qora boʻlish ehtimoli qancha?**
   *A drawer holds ten socks: six black and four white. We pull out two in the dark. What is the chance both are black?*
   ▸ ten socks in a drawer
2. **Birinchisi qora boʻlishi — oʻndan olti.**
   *The first is black: six out of ten.*
3. **Endi bu paypoq tortmada yoʻq. Toʻqqizta paypoq qoldi, ulardan beshtasi qora. Demak, birinchisi qora boʻlgandagi ikkinchisining qora boʻlishi — toʻqqizdan besh.**
   *That sock is now gone. Nine socks remain, five of them black. So the chance the second is black, given the first was black, is five out of nine.*
   ▸ one black sock leaves; 5 of 9 remain highlighted
4. **Shox boʻylab koʻpaytiramiz: oʻndan oltini toʻqqizdan beshga koʻpaytirsak, toʻqsondan oʻttiz, yaʼni uchdan bir chiqadi.**
   *Multiply along the branch: six tenths times five ninths is thirty out of ninety, one third.*
5. **Agar birinchi paypoqni joyiga qaytarsak-chi? Unda ikkinchi olish birinchisiga bogʻliq boʻlmaydi: oʻndan oltini oʻndan oltiga koʻpaytiramiz, nol butun yuzdan oʻttiz olti.**
   *What if we put the first sock back? Then the second draw does not depend on the first: six tenths times six tenths, zero point three six.*
6. **Demak, qaytarmasdan olish ikkinchi olishni birinchisiga bogʻliq qiladi. Uchdan bir bilan nol butun yuzdan oʻttiz olti orasidagi farq aynan shu bogʻliqlikdan keladi.**
   *So drawing without replacement makes the second draw depend on the first. The gap between one third and zero point three six comes exactly from that dependence.*
7. **Sunʼiy intellektda berilganlar toʻplamini oʻqitish va test qismlariga ajratganda ham misollarni qaytarmasdan olamiz: bitta misol ikkala qismga tushmasligi kerak.**
   *In AI, when we split a dataset into training and test parts, we also draw without replacement: no example may land in both parts.*
8. ⏸ **Keling, oʻzimiz sinab koʻraylik. Videoni toʻxtating. Ikkalasi ham oq boʻlish ehtimoli qancha? Bir xil rangli juft chiqish ehtimoli-chi?**
   *Let's try it ourselves. Pause the video. What is the chance both are white? And of getting a matching pair?*
9. **Ikkalasi oq: oʻndan toʻrtni toʻqqizdan uchga koʻpaytiramiz, toʻqsondan oʻn ikki. Juft esa qora yoki oq boʻladi: toʻqsondan oʻttiz qoʻshuv toʻqsondan oʻn ikki, taxminan nol butun yuzdan qirq yetti. Bu yarimdan ham kam!**
   *Both white: four tenths times three ninths, twelve out of ninety. A pair is black or white: thirty plus twelve out of ninety, about zero point four seven. Less than half the time!*
10. **Daraxt bir-biriga bogʻliq bosqichlarni koʻrsatadi. Ikki xususiyatni birdaniga koʻrish uchun esa boshqa usul bor: jadval. Buni keyingi boʻlimda koʻramiz.**
    *A tree shows stages that depend on each other. To see two attributes at once, there is another tool: a table. That is the next section.*

### 4-boʻlim · Section 4 — Kontingentlik jadvali · Contingency tables
1. **Yuzta talabamizga qaytamiz. Har bir talaba haqida ikkita narsani bilamiz: velosipedi bormi va avtobusda qatnaydimi.**
   *Back to our hundred students. We know two things about each one: do they own a bike, and do they take the bus.*
2. **Har bir juftlikka nechta talaba tushganini sanab, jadvalga yozamiz. Qator va ustun yigʻindilarini chetiga yozamiz. Bu kontingentlik jadvali deb ataladi.**
   *We count how many students fall into each combination and write them in a table, with the row and column totals in the margins. This is called a contingency table.*
   ▸ the four path counts from the tree fly into the four cells; margins 60, 40, 45, 55, 100
3. **Jadvaldan uch xil ehtimollik olamiz. Birinchisi — birgalikdagi ehtimollik: ichki katakni umumiy songa boʻlamiz. Velosiped va avtobus: yuzdan oʻn besh.**
   *The table gives three kinds of probability. The first is joint: an inner cell over the grand total. Bike and bus: fifteen out of a hundred.*
4. **Ikkinchisi — marginal ehtimollik: chetdagi yigʻindini umumiy songa boʻlamiz. Avtobus: yuzdan qirq besh.**
   *The second is marginal: a margin total over the grand total. Bus: forty-five out of a hundred.*
5. **Uchinchisi — shartli ehtimollik: katakni oʻz qatori yoki ustuni yigʻindisiga boʻlamiz. Velosipedi borlar ichida avtobus: oltmishdan oʻn besh, yaʼni nol butun yuzdan yigirma besh.**
   *The third is conditional: a cell over its own row or column total. Bus among bike owners: fifteen out of sixty, zero point two five.*
6. **Demak, shart qoʻyish — bu maxrajni tanlash: birgalikdagi ehtimollik uchun butun jadval, shartli ehtimollik uchun bitta qator yoki ustun.**
   *So conditioning is choosing a denominator: the whole table for a joint probability, one row or column for a conditional one.*
   ▸ the denominator highlight jumps: whole table → one row
7. **Sunʼiy intellektda xatolar matritsasi ham aynan shunday jadval: haqiqiy sinflar va model javoblari. Modelni baholaydigan koʻrsatkichlarning koʻpi shu jadvaldan olingan shartli ehtimolliklar.**
   *In AI, a confusion matrix is exactly such a table: true classes against the model's answers. Most of the scores we judge a model by are conditional probabilities read from it.*
8. ⏸ **Keling, oʻzimiz sinab koʻraylik. Videoni toʻxtating. Avtobusda qatnaydigan talabaning velosipedi boʻlish ehtimoli qancha?**
   *Let's try it ourselves. Pause the video. What is the probability that a student who takes the bus owns a bike?*
9. **Endi maxraj — avtobus ustuni, yaʼni qirq besh. Ulardan oʻn beshtasining velosipedi bor: qirq beshdan oʻn besh, yaʼni uchdan bir.**
   *Now the denominator is the bus column: forty-five. Fifteen of them own a bike: fifteen out of forty-five, one third.*
10. **Velosiped haqidagi bilim avtobus haqidagi javobni oʻzgartirdi. Bu har doim shundaymi? Buni keyingi boʻlimda koʻramiz.**
    *Knowing about the bike changed the answer about the bus. Is that always so? That is the next section.*

### 5-boʻlim · Section 5 — Jadvaldan erklilik · Independence from a table
1. **Oʻtgan maʼruzada erklilikni koʻrdik: birini bilish ikkinchisi haqida hech narsa aytmaydi. Yaʼni shartli ehtimollik oddiy ehtimollikka teng boʻladi.**
   *Last lecture we met independence: knowing one tells us nothing about the other. In other words, the conditional probability equals the plain one.*
2. **Velosiped va avtobusni tekshiramiz. Umuman avtobusda qatnash — nol butun yuzdan qirq besh. Velosipedi borlarda — nol butun yuzdan yigirma besh, velosipedi yoʻqlarda — nol butun yuzdan yetmish besh.**
   *Let's check bike and bus. Overall, taking the bus is zero point four five. Among bike owners, zero point two five; among the rest, zero point seven five.*
   ▸ three bars: 0.45 overall, 0.25 and 0.75 either side
3. **Velosiped haqidagi bilim javobni ikki tomonga suradi. Demak, ular erkli emas.**
   *Knowing about the bike moves the answer both ways. So they are not independent.*
4. **Xoʻp, endi koʻzoynakni olaylik. Shu kursda qirqta talaba koʻzoynak taqadi, ulardan oʻn sakkiztasi avtobusda qatnaydi. Qirqdan oʻn sakkiz — yana nol butun yuzdan qirq besh.**
   *Now glasses. In the same year group, forty students wear glasses, and eighteen of them take the bus. Eighteen out of forty: zero point four five again.*
5. **Koʻzoynak avtobus haqida hech narsa aytmaydi. Bu ikkisi erkli.**
   *Glasses tell us nothing about the bus. These two are independent.*
6. **Har qanday katak uchun qisqa yoʻl bor. Erkli boʻlsa, katakda qator yigʻindisini ustun yigʻindisiga koʻpaytirib, umumiy songa boʻlganimizcha talaba boʻlishi kerak.**
   *There is a shortcut for any cell. Under independence, a cell should hold the row total times the column total, divided by the grand total.*
7. **Velosiped va avtobus uchun: oltmishni qirq beshga koʻpaytirib, yuzga boʻlamiz — yigirma yetti boʻlishi kerak edi. Jadvalda esa oʻn besh. Koʻzoynak uchun: qirqni qirq beshga koʻpaytirib, yuzga boʻlamiz — oʻn sakkiz. Aynan jadvaldagidek.**
   *For bike and bus: sixty times forty-five over a hundred, there should be twenty-seven. The table says fifteen. For glasses: forty times forty-five over a hundred, eighteen. Exactly what we see.*
   ▸ expected 27 vs observed 15 (red); expected 18 vs observed 18 (green)
8. **Sunʼiy intellektda xususiyat tanlashda ham shunday tekshiramiz: agar xususiyat belgilanganlardan erkli boʻlsa, model undan hech narsa oʻrgana olmaydi.**
   *In AI, we run the same check when choosing features: if a feature is independent of the labels, the model can learn nothing from it.*
9. ⏸ **Keling, oʻzimiz sinab koʻraylik. Videoni toʻxtating. Erklilik boʻlsa, «velosipedi yoʻq va avtobusda qatnaydi» katagida nechta talaba boʻlishi kerak edi?**
   *Let's try it ourselves. Pause the video. Under independence, how many students would sit in the "no bike, takes the bus" cell?*
10. **Qirqni qirq beshga koʻpaytirib, yuzga boʻlamiz: oʻn sakkiz. Jadvalda esa oʻttiz. Yana bogʻliqlik.**
    *Forty times forty-five over a hundred: eighteen. The table says thirty. Dependence again.*
11. **Jadvaldagi guruhlarni birlashtirsak, javob butunlay teskari boʻlib qolishi mumkin. Buni keyingi boʻlimda haqiqiy voqea misolida koʻramiz.**
    *Pool the groups in a table, and the answer can turn completely around. We see it in the next section, in a real event.*

### 6-boʻlim · Section 6 — Simpson paradoksi · Simpson's paradox
1. **Ming toʻqqiz yuz yetmish uchinchi yil kuzi, Berkli universitetining magistraturasi. Eng katta oltita fakultetga erkaklarning qirq besh foizi, ayollarning esa oʻttiz foizi qabul qilingan.**
   *Autumn nineteen seventy-three, graduate admissions at Berkeley. In the six largest departments, forty-five percent of men were admitted, and thirty percent of women.*
   ▸ two pooled bars: men 45 %, women 30 %
2. **Farq aniq koʻrinadi. Lekin har bir fakultetni alohida koʻraylik.**
   *The gap looks clear. But let's look at each department on its own.*
3. **Ey fakultetida erkaklarning oltmish ikki foizi, ayollarning sakson ikki foizi qabul qilingan. Oltita fakultetdan toʻrttasida — ey, bi, di va ef fakultetlarida — ayollar yuqoriroq ulushda qabul qilingan.**
   *In department A, sixty-two percent of men were admitted and eighty-two percent of women. In four of the six departments, A, B, D and F, women were admitted at the higher rate.*
   ▸ six pairs of bars, A–F; four pairs flip
4. **Bu qanday boʻlishi mumkin? Erkaklarning yarmidan koʻpi ey va bi fakultetlariga hujjat topshirgan. Bu fakultetlar topshirganlarning taxminan oltmish toʻrt va oltmish uch foizini qabul qilgan.**
   *How can that be? Over half the men applied to A and B, which admitted about sixty-four and sixty-three percent of everyone who applied.*
   ▸ bar widths become the number of applicants
5. **Ayollarning esa deyarli toʻrtdan uch qismi qabul ancha qiyin boʻlgan uchta fakultetga topshirgan. Ular oʻttiz besh, yigirma besh va olti foizni qabul qilgan.**
   *Nearly three quarters of the women applied to three much harder departments, which admitted thirty-five, twenty-five and six percent.*
6. **Hech kimning qabul ehtimoli oʻzgarmadi. Faqat erkaklar va ayollar oson va qiyin fakultetlarga teng taqsimlanmagan edi. Bu Simpson paradoksi deb ataladi.**
   *Nobody's chance of admission changed. Men and women simply were not spread evenly across easy and hard departments. This is called Simpson's paradox.*
7. **Ikkala gap ham bir xil berilganlar haqida toʻgʻri. Ular shunchaki ikki xil savolga javob beradi: umuman qabul ehtimoli va bitta fakultet ichidagi qabul ehtimoli.**
   *Both statements are true of the same data. They simply answer two different questions: the chance of admission overall, and the chance within one department.*
8. **Sunʼiy intellektda birlashtirilgan berilganlarda oʻqitilgan model hech bir guruhda toʻgʻri boʻlmagan bogʻliqlikni oʻrganib olishi mumkin. Shuning uchun doim soʻraymiz: berilganlar bizga kelguncha qanday shart bilan tanlangan?**
   *In AI, a model trained on pooled data can learn a relationship that holds in no group at all. So we always ask: what were the data already conditioned on before they reached us?*
9. ⏸ **Keling, oʻylab koʻraylik. Videoni toʻxtating. Umuman olganda bemorlari kamroq tuzaladigan kasalxona har bir operatsiyada yaxshiroq boʻlishi mumkinmi?**
   *Let's think it through. Pause the video. Can a hospital with the worse overall recovery rate be the better hospital at every single operation?*
10. **Ha, mumkin. Agar u eng ogʻir bemorlarni qabul qilsa. Xuddi Berklidagi qiyin fakultetlar kabi.**
    *Yes, if it takes the hardest cases. Just like Berkeley's hard departments.*
11. **Mana shu bilan nolinchi qismni tugatamiz. Guruhlarni birlashtirishning toʻgʻri usuli bormi? Bor: har bir guruh javobiga uning kattaligicha vazn beramiz. Buni birinchi qismda koʻramiz.**
    *That ends part zero. Is there a right way to combine groups? There is: we give each group's answer a weight by its size. That is part one.*

## Part 1 — Bayes teoremasi
▸ part card "1-qism · Bayes teoremasi"

### 7-boʻlim · Section 7 — Toʻla ehtimollik formulasi · The law of total probability
1. **Avtobusda qatnash ehtimolini bilmasak-u, faqat har bir guruhdagi ulushni bilsak-chi? Velosipedi borlarda nol butun yuzdan yigirma besh, yoʻqlarda nol butun yuzdan yetmish besh.**
   *What if we did not know the overall bus rate, only the rate in each group? Zero point two five among bike owners, zero point seven five among the rest.*
2. **Ularning oddiy oʻrtachasi nol butun oʻndan besh boʻlardi. Lekin guruhlar teng emas: velosipedi borlar oltmishta, yoʻqlar qirqta.**
   *Their plain average would be zero point five. But the groups are not equal: sixty bike owners, forty without.*
3. **Shuning uchun har bir guruh javobini guruh ulushiga koʻpaytirib qoʻshamiz: nol butun yuzdan yigirma besh karra nol butun oʻndan olti, qoʻshuv nol butun yuzdan yetmish besh karra nol butun oʻndan toʻrt.**
   *So we multiply each group's answer by the group's share and add: zero point two five times zero point six, plus zero point seven five times zero point four.*
4. **Nol butun yuzdan oʻn besh qoʻshuv nol butun yuzdan oʻttiz — nol butun yuzdan qirq besh. Aynan jadval chetidagi yuzdan qirq besh.**
   *Zero point one five plus zero point three zero: zero point four five. Exactly the forty-five out of a hundred in the table's margin.*
5. **Bu toʻla ehtimollik formulasi deb ataladi. Fazoni bir-birini kesmaydigan va hammasini qamraydigan guruhlarga boʻlamiz, har bir guruh ichida hisoblaymiz va guruh kattaligi boʻyicha oʻrtachalaymiz.**
   *This is the law of total probability. We split the space into groups that never overlap and cover everything, work out the answer inside each group, and average by group size.*
   ▸ P(B) = Σ P(B | Aᵢ) P(Aᵢ)
6. **Rasmda ustun kengligi — guruh kattaligi, rangli qismi — avtobusda qatnaydiganlar. Umumiy javob nol butun yuzdan yigirma besh bilan nol butun yuzdan yetmish besh orasida, lekin yigirma beshga yaqinroq, chunki velosipedi borlar guruhi kattaroq.**
   *In the picture, bar width is group size and the coloured part is the bus takers. The overall answer lands between zero point two five and zero point seven five, nearer zero point two five, because the bike group is bigger.*
   ▸ two bars, widths 60 and 40, filled to 0.25 and 0.75; a dashed line at 0.45
7. **Sunʼiy intellektda modelning umumiy aniqligi ham har bir guruhdagi aniqlikning vaznli oʻrtachasi. Shuning uchun umumiy natija yaxshi koʻrinsa-yu, kichik bir guruhda model yomon ishlashi mumkin.**
   *In AI, a model's overall accuracy is the weighted average of its accuracy in each group. So the overall number can look good while the model fails a small group.*
8. ⏸ **Keling, oʻzimiz sinab koʻraylik. Videoni toʻxtating. Shu formula bilan avtobusda qatnamaslik ehtimoli qancha chiqadi?**
   *Let's try it ourselves. Pause the video. With the same formula, what is the probability of not taking the bus?*
9. **Nol butun yuzdan yetmish besh karra nol butun oʻndan olti, qoʻshuv nol butun yuzdan yigirma besh karra nol butun oʻndan toʻrt: nol butun yuzdan qirq besh qoʻshuv nol butun oʻndan bir, yaʼni nol butun yuzdan ellik besh. Jadvaldagi ellik besh.**
   *Zero point seven five times zero point six, plus zero point two five times zero point four: zero point four five plus zero point one, zero point five five. The table's fifty-five.*
10. **Shu paytgacha biz guruhdan javobga bordik. Teskarisi-chi? Talaba avtobusda qatnashini bilsak, uning velosipedi boʻlish ehtimoli qancha? Buni keyingi boʻlimda koʻramiz.**
    *So far we have gone from the group to the answer. And the other way? Knowing a student takes the bus, what is the chance they own a bike? That is the next section.*

### 8-boʻlim · Section 8 — Bayes teoremasi · Bayes' theorem
1. **Bizda velosipedi borlar ichida avtobus ehtimoli bor. Bizga esa teskarisi kerak: avtobusda qatnaydiganlar ichida velosiped ehtimoli.**
   *We have the chance of the bus among bike owners. We want the reverse: the chance of a bike among bus takers.*
2. **Koʻpaytirish qoidasini ikki tomondan yozamiz. Ey va bi birga — bu ey ning ehtimoli karra ey sodir boʻlgandagi bi ning ehtimoli. Shu bilan birga, bu bi ning ehtimoli karra bi sodir boʻlgandagi ey ning ehtimoli.**
   *We write the multiplication rule both ways round. A and B together is the probability of A times the probability of B given A. It is also the probability of B times the probability of A given B.*
   ▸ P(A ∩ B) = P(A) P(B | A) = P(B) P(A | B)
3. **Ikkalasini tenglashtirib, bi ning ehtimoliga boʻlamiz. Mana shu Bayes teoremasi.**
   *We set them equal and divide by the probability of B. That is Bayes' theorem.*
   ▸ P(A | B) = P(B | A) P(A) / P(B)
4. **Maxrajni esa toʻla ehtimollik formulasidan olamiz.**
   *And the denominator comes from the law of total probability.*
5. **Talabalarda tekshiramiz: nol butun yuzdan yigirma beshni nol butun oʻndan oltiga koʻpaytirib, nol butun yuzdan qirq beshga boʻlamiz. Uchdan bir chiqadi. Jadval ham shuni aytadi: avtobusda qatnaydigan qirq besh talabadan oʻn beshtasining velosipedi bor.**
   *Check it on the students: zero point two five times zero point six, divided by zero point four five, gives one third. The table agrees: of the forty-five bus takers, fifteen own a bike.*
6. **Uchta qismning nomi bor, ular kursning oxirigacha uchraydi. Ey ning ehtimoli — aprior ehtimollik: dalil koʻrmasdan oldingi ishonchimiz.**
   *The three pieces have names that stay with us for the rest of the course. The probability of A is the prior: what we believed before seeing any evidence.*
   ▸ the three pieces of the formula light up and get their names
7. **Ey sodir boʻlgandagi bi ning ehtimoli — haqiqatga oʻxshashlik: ey sababi dalilni qanchalik yaxshi tushuntiradi. Bi sodir boʻlgandagi ey ning ehtimoli — aposterior ehtimollik: dalilni koʻrgandan keyingi ishonchimiz.**
   *The probability of B given A is the likelihood: how well the cause A explains the evidence B. The probability of A given B is the posterior: what we believe once we have seen it.*
8. **Masalan, tashqariga qaramasdan yomgʻir ehtimoli — aprior. Yoʻlak hoʻl ekan — bu dalil. Yomgʻir yoqsa, yoʻlak deyarli doim hoʻl boʻladi, shuning uchun yomgʻir ehtimoli oshadi. Lekin aniq boʻlib qolmaydi: koʻcha yuvadigan mashina ham yoʻlakni hoʻl qiladi.**
   *Before looking outside, the chance of rain is the prior. The pavement is wet: that is the evidence. Rain almost always wets the pavement, so the chance of rain rises. But not to certainty: a street cleaner also leaves the pavement wet.*
9. **Sunʼiy intellektda Bayes teoremasi — dalil asosida ishonchni yangilash qoidasi. Berilganlardan oʻrganish aynan shu degani. Sodda Bayes klassifikatori spamni shu formula bilan aniqlaydi.**
   *In AI, Bayes' theorem is the rule for updating a belief with evidence, and that is exactly what learning from data means. The naive Bayes classifier finds spam with this very formula.*
10. ⏸ **Keling, oʻzimiz sinab koʻraylik. Videoni toʻxtating. Avtobusda qatnaydigan talabaning velosipedi yoʻq boʻlish ehtimoli qancha? Bayes teoremasi bilan hisoblaymiz.**
    *Let's try it ourselves. Pause the video. What is the probability that a bus taker has no bike? Let's use Bayes' theorem.*
11. **Nol butun yuzdan yetmish beshni nol butun oʻndan toʻrtga koʻpaytirib, nol butun yuzdan qirq beshga boʻlamiz: uchdan ikki. Jadvalda ham qirq beshdan oʻttiz.**
    *Zero point seven five times zero point four, divided by zero point four five: two thirds. The table says thirty out of forty-five too.*
12. **Talabalarda ikkala yoʻnalish ham oson topildi. Hayotda esa bizga kerakli yoʻnalishni oʻlchash deyarli doim qiyin. Buni keyingi boʻlimda koʻramiz.**
    *With the students, both directions were easy to find. In real life, the direction we need is almost always the one that is hard to measure. That is the next section.*

### 9-boʻlim · Section 9 — Musbat test nimani anglatadi · What a positive test means
1. **Test kasalligi aniq boʻlgan odamlarda tekshiriladi. Bu bizga kasal boʻlgandagi musbat natija ehtimolini beradi — bu testning xususiyati.**
   *A test is checked on people already known to be ill. That gives us the chance of a positive result given illness: a property of the test.*
2. **Bemorga esa teskarisi kerak: natija musbat boʻlgandagi kasal boʻlish ehtimoli. U kasallik qanchalik keng tarqalganiga ham bogʻliq.**
   *The patient wants the reverse: the chance of being ill given a positive result. And that also depends on how common the illness is.*
3. **Bu ikkisini almashtirib yuborish xatosining nomi bor — prokuror xatosi. «Million begunoh odamdan faqat bittasi mos keladi» degani — begunoh boʻlgandagi moslik ehtimoli, mos kelgandagi begunohlik ehtimoli emas.**
   *Mixing the two up has a name: the prosecutor's fallacy. "Only one innocent person in a million would match" is the chance of a match given innocence, not the chance of innocence given a match.*
4. **Keling, hisoblaylik. Yuz kishidan bittasi kasal. Oʻn ming kishini tekshiramiz: yuztasi kasal, toʻqqiz ming toʻqqiz yuztasi sogʻlom.**
   *Let's compute. One person in a hundred has the disease. We test ten thousand people: one hundred are ill, nine thousand nine hundred are healthy.*
   ▸ 10 000 small squares; 100 red
5. **Test birorta ham kasalni oʻtkazib yubormaydi deb olamiz: yuzta kasalning hammasi musbat chiqadi. Lekin u sogʻlomlarning har yuztasidan beshtasini ham notoʻgʻri musbat deb topadi — yana toʻrt yuz toʻqson besh kishi.**
   *Say the test never misses: all one hundred ill people test positive. But it also wrongly flags five in every hundred healthy people: four hundred and ninety-five more.*
   ▸ 495 orange squares join the 100 red
6. **Musbatlar: yuz qoʻshuv toʻrt yuz toʻqson besh, besh yuz toʻqson besh kishi. Ulardan faqat yuztasi kasal. Besh yuz toʻqson beshdan yuz — taxminan oʻn yetti foiz.**
   *Positives: one hundred plus four hundred and ninety-five, five hundred and ninety-five people. Only one hundred of them are ill. One hundred out of five hundred and ninety-five: about seventeen percent.*
   ▸ the 595 positives magnified into one bar: 100 red, 495 orange
7. **Nima uchun? Katta guruhning besh foizi kichik guruhning yuz foizidan koʻp. Sogʻlomlar kasallardan toʻqson toʻqqiz baravar koʻp, shuning uchun har bir haqiqiy holatga taxminan beshta yolgʻon signal toʻgʻri keladi.**
   *Why? Five percent of a huge group beats one hundred percent of a tiny one. Healthy people outnumber the ill ninety-nine to one, so there are about five false alarms for every real case.*
8. **Sunʼiy intellektda firibgarlikni aniqlaydigan model ham xuddi shunday: firibgarlik kamdan-kam boʻlgani uchun uning signallarining koʻpi yolgʻon boʻladi.**
   *In AI, a fraud detector works the same way: because fraud is rare, most of its alarms are false.*
9. ⏸ **Keling, oʻzimiz sinab koʻraylik. Videoni toʻxtating. Kasallik oʻn kishidan birida boʻlsa-chi? Test oʻsha-oʻsha.**
   *Let's try it ourselves. Pause the video. What if one person in ten has the disease? Same test.*
10. **Oʻn ming kishidan ming kishi kasal, toʻqqiz ming sogʻlom. Yolgʻon signallar — toʻqqiz mingning besh foizi, toʻrt yuz ellik. Bir ming toʻrt yuz ellikdan ming — taxminan oltmish toʻqqiz foiz.**
    *Of ten thousand, a thousand are ill and nine thousand healthy. False alarms: five percent of nine thousand, four hundred and fifty. A thousand out of one thousand four hundred and fifty: about sixty-nine percent.*
11. **Test oʻzgarmadi, faqat kasallik qanchalik keng tarqalgani oʻzgardi. Bu sonning kuchini keyingi boʻlimda koʻramiz.**
    *The test did not change; only how common the disease is changed. The next section shows the power of that number.*

### 10-boʻlim · Section 10 — Asosiy ulush · Base rates
1. **Kasallik testdan oldin qanchalik keng tarqalganini asosiy ulush deymiz. Bu Bayes teoremasidagi aprior ehtimollik.**
   *How common the disease is before any test is called the base rate. It is the prior in Bayes' theorem.*
2. **Testni oʻzgartirmasdan, faqat asosiy ulushni oʻzgartirib koʻramiz.**
   *Let's keep the test fixed and change only the base rate.*
   ▸ the curve P(ill | positive) against the base rate draws itself
3. **Ming kishidan bittasi kasal boʻlsa, musbat natija ortida kasallik boʻlish ehtimoli atigi ikki foiz. Yuzdan bittada — oʻn yetti foiz. Oʻndan bittada — oltmish toʻqqiz foiz.**
   *At one in a thousand, a positive result means only a two percent chance of disease. At one in a hundred, seventeen percent. At one in ten, sixty-nine percent.*
   ▸ markers at 0.1 %, 1 %, 10 %: 2 %, 17 %, 69 %
4. **Shuning uchun sogʻlom aholini tekshirish qiyin: deyarli hamma sogʻlom boʻlsa, kichik yolgʻon signal ulushi ham haqiqiy holatlardan koʻp musbat beradi. Shuning uchun musbat natijadan keyin boshqa, ikkinchi test oʻtkaziladi.**
   *That is why screening a healthy population is hard: when almost everybody is well, even a small false-alarm rate produces more positives than real cases. So a positive screen is followed by a second, different test.*
5. **Sunʼiy intellektda shu hisob tufayli kam uchraydigan hodisalar uchun aniqlik yaroqsiz koʻrsatkich. Bu yerda doim «sogʻlom» deb javob beradigan model toʻqson toʻqqiz foiz aniq boʻlardi, lekin birorta ham kasalni topmasdi.**
   *In AI, the same arithmetic is why accuracy is a useless score for rare events. Here, a model that always answers "healthy" would be ninety-nine percent accurate, and would never find a single sick person.*
6. ⏸ **Keling, oʻzimiz sinab koʻraylik. Videoni toʻxtating. Kasallik ming kishidan birida boʻlsa, doim «sogʻlom» deydigan modelning aniqligi qancha?**
   *Let's try it ourselves. Pause the video. If one person in a thousand is ill, how accurate is the model that always says "healthy"?*
7. **Toʻqson toʻqqiz butun oʻndan toʻqqiz foiz. Kasallik qanchalik kam boʻlsa, foydasiz model shunchalik yaxshi koʻrinadi.**
   *Ninety-nine point nine percent. The rarer the disease, the better a useless model looks.*
8. **Bu formula kursda koʻp marta qaytadi: oltinchi maʼruzada Bayes xulosasida, uchinchi modulda sodda Bayes klassifikatorida, birinchi modulda esa tasniflash koʻrsatkichlarida.**
   *This formula comes back many times in the course: in Lecture 6, in Bayesian inference; in Module 3, in the naive Bayes classifier; and in Module 1, in classification metrics.*
9. **Keling, maʼruzani yakunlaylik. Shart namunalar fazosini toraytiradi va biz uning ichida qayta sanaymiz. Daraxtda shoxlar boʻylab koʻpaytiramiz, jadvalda esa maxrajni tanlaymiz. Erklilik — shartli ehtimollik oddiy ehtimollikka teng degani, guruhlarni birlashtirish esa javobni teskari qilishi mumkin. Toʻla ehtimollik formulasi guruhlar javobini vaznli oʻrtachalaydi, Bayes teoremasi esa shartni teskari aylantiradi.**
   *Let's wrap up the lecture. A condition shrinks the sample space, and we recount inside it. On a tree we multiply along branches; in a table we choose the denominator. Independence means the conditional equals the plain probability, and pooling groups can turn an answer around. The law of total probability takes a weighted average of the groups' answers, and Bayes' theorem turns the condition around.*
10. **Mana shu bilan ikkinchi maʼruzamizni tugatamiz. Keyingi maʼruzada tasodifiy miqdorlar va asosiy taqsimotlar bilan tanishamiz.**
    *That brings our second lecture to an end. In the next lecture, we meet random variables and the key distributions.*
