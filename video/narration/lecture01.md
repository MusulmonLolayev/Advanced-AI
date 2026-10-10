# Lecture 1 — video narration (draft 2, for approval)

Lecture 1 split into **14 short videos**: Part 0 (Berilganlar va tavsiflovchi statistika) = videos 1–9,
Part 1 (Ehtimollik) = videos 10–14. Each video: problem first → concept as the answer → one AI use → a hands-on
pause → the problem the next video solves.

**Draft 2 changes:** data = **berilganlar** (maʼlumot only where *information* is meant, e.g. "ob-havo maʼlumoti");
descriptive = **tavsiflovchi**; every Uzbek line rewritten as spoken Uzbek in your phrasing instead of a translation
of the English ("Toshkent qoʻshuv Samarqand, va boʻlamiz ikkiga"). Spread = *tarqoqlik*.

**Voice:** "we", never "you" — the only line addressed to the viewer is *Videoni toʻxtating* on the pause card.
**Numbers:** every figure comes from `video/statistics/raw/l01_numbers.json` / `l01_figures.txt`
(`capture_l01.py`, asserted against the slides). Narration spells them; the screen shows digits.

Format per line: **UZ** (your voice) · *EN* (English track) · ▸ visual.

---

## Part 0 — Berilganlar va tavsiflovchi statistika

### Video 1 — Berilganlar turlari · Data types
1. **Assalomu alaykum, aziz doʻstlar. Statistikada birinchi savol hisob-kitob emas. Avval qoʻlimizdagi berilganlar qanday turda ekanini bilib olishimiz kerak.**
   *Hello, dear friends. In statistics, the first question is not a calculation. The first question is: what kind of data do we have?*
   ▸ six cards drop in: koʻz rangi · tugʻilgan shahar · baho · farzandlar soni · maosh · boʻy
2. **Tasavvur qilamiz, ikki kishining tugʻilgan shahrini olib, oʻrtachasini hisoblamoqchimiz. Toshkent qoʻshuv Samarqand, va boʻlamiz ikkiga. Bunday hisobning hech qanday maʼnosi yoʻq.**
   *Let's imagine we add up two people's cities of birth and divide by two. Tashkent plus Samarkand, divided by two. That means nothing.*
   ▸ "(Toshkent + Samarqand) ÷ 2 = ?" then a red cross
3. **Demak, ayrim berilganlar son emas, balki toifa boʻladi. Bunday berilganlar kategorial berilganlar deyiladi.**
   *So some data are not numbers at all, but categories. We call them categorical data.*
   ▸ screen splits: left bin "kategorial", right bin "sonli"
4. **Koʻz rangi yoki tugʻilgan shaharni hech qanday tartibga solib boʻlmaydi. Bular nominal berilganlar.**
   *Eye colour and city of birth have no natural order. That is nominal data.*
   ▸ two cards slide into "nominal", shuffled freely
5. **Baho esa past, oʻrta, yuqori boʻladi. Mana bu yerda tartib bor, lekin ular orasidagi masofa teng emas. Bunday berilganlar tartibli, yaʼni ordinal deyiladi.**
   *A rating of low, medium, high does have an order, but the steps are not equal. That is ordinal data.*
   ▸ past → oʻrta → yuqori on a line with unequal gaps
6. **Xoʻp, endi sonli berilganlarga oʻtaylik. Farzandlar sonini sanaymiz: bitta, ikkita, uchta. Ikki yarimta farzand boʻlmaydi. Bular diskret berilganlar.**
   *Now let's move to numerical data. We count children: one, two, three. There is no such thing as two and a half children. That is discrete data.*
   ▸ number line, dots only on whole numbers; 2.5 crossed out
7. **Maosh yoki boʻy esa oʻlchanadi va oraliqdagi istalgan qiymatni olishi mumkin. Bular uzluksiz berilganlar.**
   *Salary and height are measured on a scale, and can take any value in between. That is continuous data.*
   ▸ a marker glides along a ruler: 172 → 172.4 → 172.43
8. **Bu nima uchun kerak? Chunki berilganlar turiga qarab qaysi hisob toʻgʻri ekanini bilamiz. Oʻrtacha qiymat va standart chetlanishni faqat sonli berilganlar uchun hisoblaymiz. Kategorial berilganlarni esa sanaymiz va ulushini topamiz.**
   *Why does this matter? Because the type of data decides which calculations make sense. A mean or a standard deviation only means something for numerical data. Categorical data we count, and turn into proportions.*
   ▸ the 2×2 map, "sanash, ulush" under categorical and "oʻrtacha, chetlanish" under numerical
9. **Sunʼiy intellektda ham xuddi shunday. Shahar nomini modelga son qilib berolmaymiz, avval uni toifa sifatida kodlab olamiz.**
   *The same holds in AI: we cannot feed a city name to a model as a number. We first encode it as a category.*
   ▸ "Toshkent" → [1, 0, 0], "Samarqand" → [0, 1, 0]
10. ⏸ **Keling, oʻzimiz sinab koʻraylik. Videoni toʻxtating. Qon guruhi, imtihondagi oʻrin va xonadagi harorat — har biri qaysi turga kiradi?**
    *Let's try it ourselves. Pause the video. Blood type, finishing place in an exam, and room temperature: which type is each?*
11. **Qon guruhi — nominal. Imtihondagi oʻrin — ordinal, chunki birinchi oʻrin ikkinchidan oldin turadi, lekin ular orasidagi farq teng emas. Harorat esa uzluksiz.**
    *Blood type is nominal. Exam place is ordinal: first comes before second, but the gaps are not equal. Temperature is continuous.*
12. **Endi bizda olti yuzta maosh bor, yaʼni sonli, uzluksiz berilganlar. Lekin bu olti yuz kishi kimlar? Bu butun soha emas, uning bir qismi xolos. Keyingi videoda shu haqida gaplashamiz.**
    *Now we have six hundred salaries: numerical, continuous data. But who are these six hundred people? Not the whole industry, only part of it. That is the next video.*

### Video 2 — Bosh toʻplam va tanlanma · Population and sample
1. **Assalomu alaykum, aziz doʻstlar. Bizda olti yuzta xodimning maoshi bor. Lekin odatda bizni kattaroq savol qiziqtiradi: butun sohada odamlar qancha maosh oladi?**
   *Hello, dear friends. We have the salaries of six hundred employees. But the question we usually care about is bigger: what do people earn across the whole industry?*
   ▸ the 600 dots, then the camera pulls back: they sit inside a huge faint cloud
2. **Sohadagi hamma xodimni oʻlchab chiqolmaymiz, chunki ular juda koʻp. Biz oʻrganmoqchi boʻlgan hamma birliklar bosh toʻplam deb ataladi.**
   *We cannot measure every employee in the industry; there are far too many. Every unit we care about is called the population.*
3. **Haqiqatda oʻlchagan qismimiz esa tanlanma deyiladi. Mana bizning olti yuzta maoshimiz — bu tanlanma.**
   *The part we actually measure is the sample. Our six hundred salaries are a sample.*
   ▸ labels "bosh toʻplam (population)" around the cloud, "tanlanma (sample)" around the 600
4. **Keling, kichikroq misol olaylik. Beshta maosh, ming dollarda: oʻttiz bir, qirq besh, qirq yetti, ellik ikki va sakson sakkiz.**
   *Let's take a smaller example: five salaries, in thousands of dollars. Thirty-one, forty-five, forty-seven, fifty-two, and eighty-eight.*
   ▸ five cards
5. **Har birini nomlab olish uchun raqam beramiz: x bir, x ikki, va shunday qilib x beshgacha. Nechta kuzatuv borligini n bilan belgilaymiz. Mana bu yerda n beshga teng.**
   *To name them, we number each one: x one, x two, and so on up to x five. We write the sample size as n; here n is five.*
   ▸ x₁ … x₅ appear under the cards, then "n = 5"
6. **Demak, x uch — bu uchinchi kuzatuv, yaʼni qirq yetti. x besh esa sakson sakkiz.**
   *So x three is the third observation, forty-seven. And x five is eighty-eight.*
7. **Hammasini qoʻshish kerak boʻlsa, uzun qilib yozib oʻtirmaymiz. Sigma belgisi bilan yozamiz: i birdan n gacha, x i larni qoʻshamiz.**
   *When we need to add them all up, we do not write it out longhand. We use the sigma sign: the sum of x i, for i from one to n.*
   ▸ x₁ + x₂ + x₃ + x₄ + x₅ folds into Σ xᵢ
8. **Mana bu yerda yigʻindi ikki yuz oltmish uchga teng.**
   *Here that comes to two hundred and sixty-three.*
9. **Yana bitta kelishuv bor. Tanlanmadan hisoblagan sonlarimizni lotin harflari bilan yozamiz: x chiziqcha va s. Koʻrolmaydigan bosh toʻplamni esa grek harflari bilan yozamiz: myu va sigma.**
   *One more convention. Numbers computed from the sample get Latin letters: x bar and s. The population we cannot see gets Greek letters: mu and sigma.*
   ▸ two columns under the cloud and the sample: x̄, s │ μ, σ
10. **Sunʼiy intellektda oʻqitish toʻplami — bu tanlanma. Model esa butun dunyoda, yaʼni bosh toʻplamda ishlashi kerak. Kursimiz davomida bu farqni koʻp marta uchratamiz.**
    *In AI, the training set is a sample. The model has to work on the whole world: the population. That gap comes back again and again in this course.*
11. ⏸ **Keling, oʻzimiz sinab koʻraylik. Videoni toʻxtating. Beshta maoshimizda x ikki nechaga teng? x bir qoʻshuv x besh-chi?**
    *Let's try it ourselves. Pause the video. In our five salaries, what is x two, and what is x one plus x five?*
12. **x ikki — qirq besh. x bir qoʻshuv x besh — oʻttiz bir qoʻshuv sakson sakkiz, yaʼni bir yuz oʻn toʻqqiz.**
    *x two is forty-five. x one plus x five is thirty-one plus eighty-eight: one hundred and nineteen.*
13. **Xoʻp, olti yuzta maoshimiz bor. Lekin olti yuzta sonni bir qarashda qanday koʻramiz? Bu keyingi videoda.**
    *So we have six hundred salaries. But how do we see the shape of six hundred numbers at a glance? That is the next video.*

### Video 3 — Gistogramma · The histogram
1. **Assalomu alaykum, aziz doʻstlar. Olti yuzta maoshni roʻyxat qilib yozsak, hech narsani koʻrolmaymiz. Keling, ularni rasm qilib chizaylik.**
   *Hello, dear friends. Written as a list, six hundred salaries show us nothing. Let's draw their shape instead.*
   ▸ the salary list scrolls, then collapses into dots on an axis
2. **Maosh uzluksiz kattalik, shuning uchun bir xil qiymat deyarli takrorlanmaydi. Har bir qiymatni alohida sanasak, hammasi bir martadan chiqadi.**
   *Salary is continuous, so almost no value repeats. If we count each value separately, every one of them appears exactly once.*
   ▸ 600 hair-thin bars, all the same height: 1
3. **Shuning uchun avval qiymatlarni sinflarga ajratamiz. Birinchi qadam — oraliqni topamiz. Eng kattasi bir yuz ellik bir ming, eng kichigi yigirma yetti ming. Oraliq bir yuz yigirma toʻrt ming dollar boʻladi.**
   *So first we group the values into classes. Step one is the range: the largest is one hundred and fifty-one thousand, the smallest twenty-seven thousand. The range is one hundred and twenty-four thousand dollars.*
   ▸ min and max dots light up, a brace between them: $124,026
4. **Ikkinchi qadam — nechta sinf boʻlishini tanlaymiz. Odatda beshtadan oʻntagacha olinadi. Biz yettita olamiz.**
   *Step two: choose the number of classes, usually five to ten. We take seven.*
5. **Uchinchi qadam — sinf kengligi. Oraliqni yettiga boʻlamiz, taxminan oʻn yetti ming yetti yuz chiqadi. Qulay boʻlishi uchun yigirma minggacha yaxlitlaymiz.**
   *Step three: the width. The range divided by seven is about seventeen thousand seven hundred. We round it up to a convenient twenty thousand dollars.*
   ▸ 124,026 ÷ 7 = 17,718 → 20,000; seven class edges drop onto the axis
6. **Toʻrtinchi qadam — har bir sinfga nechta odam tushganini sanaymiz.**
   *Step four: count how many people fall into each class.*
   ▸ dots fall into the seven classes; counts tick up: 156, 311, 89, 32, 7, 3, 2
7. **Qirq mingdan oltmish minggacha uch yuz oʻn bir kishi bor, yaʼni yarmidan koʻpi. Undan yuqorida esa ingichka dum choʻzilib ketgan.**
   *Forty to sixty thousand: three hundred and eleven people, more than half. Above that, a thin tail stretches out to the right.*
8. **Beshinchi qadam — har bir sinfga bitta ustun chizamiz, ustunlar bir-biriga tegib turadi. Chunki shkala uzluksiz. Orada boʻshliq qoldirsak, goʻyo u yerda maosh boʻlishi mumkin emasdek koʻrinadi.**
   *Step five: draw one bar per class, with the bars touching. The scale is continuous; a gap would suggest salaries that cannot exist.*
   ▸ the stacks become touching bars; a gap flashes red, then closes
9. **Mana bu gistogramma deb ataladi. Bitta son koʻrsatolmaydigan narsani u koʻrsatadi: maoshlar oʻng tomonga qiyshaygan.**
   *This is a histogram. It shows what no single number can: the salaries are skewed to the right.*
10. **Sunʼiy intellektda ham yangi berilganlar kelsa, birinchi ish shu: har bir belgining gistogrammasini chizamiz. Qanday taqsimlangan, qayerda gʻalati qiymatlar bor — shuni koʻramiz.**
    *In AI, the first thing we do with a new dataset is the same: draw a histogram of every feature, to see how it is spread and where the strange values are.*
11. ⏸ **Keling, oʻzimiz sinab koʻraylik. Videoni toʻxtating. Jadvalga qarab, sakson mingdan koʻp oladiganlar nechta ekanini topamiz.**
    *Let's try it ourselves. Pause the video. Using the table, we find how many employees earn more than eighty thousand.*
12. **Oxirgi toʻrtta sinfni qoʻshamiz: oʻttiz ikki, yetti, uch va ikki. Jami qirq toʻrt kishi.**
    *We add the last four classes: thirty-two, seven, three and two. Forty-four people in all.*
13. **Lekin rahbarimiz baribir bitta son soʻraydi. Qaysi son? Bu keyingi videoda.**
    *But our manager still asks for one number. Which one? That is the next video.*

### Video 4 — Oʻrtacha qiymat · The mean  *(already built; Uzbek rewritten, English "you" → "we", one new AI line)*
- s1a **Assalomu alaykum, aziz doʻstlar. Bu kompaniyada olti yuz kishi ishlaydi. Mana, har biri qancha maosh oladi. Rahbarimiz oddiy savol beradi: bu yerda odamlar qancha maosh oladi?** · *Hello, dear friends. Six hundred people work at this company. Here is what every one of them earns. Our manager asks a simple question: what do people earn here?*
- s1b **Olti yuzta sonni bittalab oʻqib chiqolmaymiz. Hammasining oʻrnini bosadigan bitta son kerak. Lekin qaysi son?** · *We cannot read out six hundred numbers. We need one number that stands for all of them. But which one?*
- s2a **Eng qadimiy javob eng oddiysi ham. Hammasini qoʻshamiz va teng qilib boʻlib chiqamiz.** · *The oldest answer is also the simplest. We add everything up, and share it out equally.*
- s2b **Mana bu yerda ellik bir ming olti yuz oʻn uch dollar chiqdi. Buni oʻrtacha qiymat deymiz.** · *Here that comes to fifty-one thousand, six hundred and thirteen dollars. We call it the mean.*
- s2c **Keling, u aslida nima qilayotganini koʻraylik. Kompaniyadagi hamma pulni yigʻib, teng boʻlib chiqsak, har bir kishiga mana shuncha tegadi.** · *Let's look at what it is really doing. It is the amount each person would get if all the money in the company were collected, and split evenly.*
- s3a **Shuning uchun umumiy summa muhim boʻlganda bizga aynan oʻrtacha qiymat kerak.** · *That is why the mean is what we want whenever totals matter.*
- s3b **Uni olti yuzga koʻpaytirsak, butun ish haqi fondini qaytarib olamiz: oʻttiz bir millionga yaqin dollar.** · *Multiply it back by six hundred, and we recover the entire payroll: just under thirty-one million dollars.*
- s3c **Boshqa hech bir koʻrsatkich buni qilolmaydi. Oʻrtacha qiymat umumiy summani eslab qoladi.** · *No other summary does that. The mean is the one that remembers the total.*
- **s3d (new, AI)** **Sunʼiy intellektda ham shunday. Modelning xatosini butun berilganlar boʻyicha oʻrtacha qilamiz, oʻqitish esa aynan shu sonni kichraytiradi.** · *AI works the same way: we average a model's error over the whole dataset, and training is exactly the job of shrinking that average.* ▸ loss = (1/n) Σ errorᵢ
- s4a **Xoʻp, endi u qayerda adashishini koʻraylik. Oʻsha olti yuz xodimdan ellik nafari kafega boradi.** · *Now let's watch it fail. Fifty of those six hundred employees go out for a drink.*
- s4b **Ularning oʻrtacha maoshi ellik ming olti yuz yigirma yetti dollar. Oʻrtadagi odam esa qirq yetti ming uch yuz yigirma uch dollar oladi. Kutganimizdek, ikkalasi bir-biriga yaqin.** · *Their average salary is fifty thousand, six hundred and twenty-seven dollars, and the middle person earns forty-seven thousand, three hundred and twenty-three. Close together, as we would expect.*
- s4c **Keyin xonaga yana bir kishi kirib keladi — milliarder. Xonadagilarning hech biri bir tiyin ham boyib qolmadi.** · *Then one more person walks in: a billionaire. Nobody already in that room gained a single cent.*
- s4d **Lekin endi xonadagi oʻrtacha maosh ikki butun oʻndan toʻqqiz milliard dollar boʻldi.** · *But the average salary in that room is now two point nine billion dollars.*
- s4e **Keling, qizil chiziq qayerga tushganiga qaraylik. Boʻsh joyga, odamlar bilan milliarderning oʻrtasiga. Xonadagi hech kim bunday maosh olmaydi.** · *Let's look at where that red line lands. In empty space, between the crowd and the billionaire. It describes nobody present.*
- s5a **Endi uzuq chiziqqa qaraylik. Avval: qirq yetti ming uch yuz yigirma uch dollar.** · *Now let's look at the dashed line. Before: forty-seven thousand, three hundred and twenty-three.*
- s5b **Keyin: qirq yetti ming yetti yuz oltmish bir dollar. Bor-yoʻgʻi toʻrt yuz dollarga siljidi.** · *After: forty-seven thousand, seven hundred and sixty-one. It moved by four hundred dollars.*
- s5c **Mana shu chiziq mediana deb ataladi. U keyingi videomizning mavzusi.** · *That line is the median, and it is the subject of the next video.*
- s6a **Keling, oʻzimiz sinab koʻraylik. Videoni toʻxtating. Mana toʻqqizta maosh, ming dollarda. Oʻrtacha qiymatini hisoblaymiz. Keyin toʻqqiz kishidan nechtasi undan kam olishini sanaymiz.** · *Let's try it ourselves. Pause the video. Here are nine salaries, in thousands of dollars. We work out the mean. Then we count how many of the nine earn less than it.*
- s6b **Yigʻindi toʻrt yuz ellik uch, demak oʻrtacha qiymat ellik ming uch yuz oʻttiz uch dollar.** · *The total is four hundred and fifty-three, so the mean is fifty thousand, three hundred and thirty-three dollars.*
- s6c **Toʻqqiz kishidan oltitasi undan kam oladi. Hech qanday milliarder yoʻq boʻlsa ham, oʻrtacha qiymat koʻpchilikdan yuqorida turibdi.** · *And six of the nine earn less than that. Even with no billionaire anywhere, the mean already sits above most of the people in it.*
- s7 **Mana shu muammoni mediana hal qiladi.** · *Which is exactly the problem the median solves.*

### Video 5 — Mediana va moda · The median and the mode
1. **Assalomu alaykum, aziz doʻstlar. Oʻtgan videoda bitta milliarder oʻrtacha qiymatni boʻsh joyga olib ketdi. Keling, bunday paytda ham joyidan qimirlamaydigan son topaylik.**
   *Hello, dear friends. In the last video, one billionaire dragged the mean into empty space. Let's find a number that holds its ground.*
2. **Gʻoya oddiy. Maoshlarni kichigidan kattasigacha tartib bilan teramiz va oʻrtada turgan odamni olamiz. Bu mediana deb ataladi.**
   *The idea is simple: we line the salaries up from smallest to largest, and take the person standing in the middle. That is the median.*
3. **Beshta maosh: oʻttiz bir, qirq besh, qirq yetti, ellik ikki, sakson sakkiz. Ular tartiblangan, n beshga teng. Demak, oʻrtadagisi uchinchisi, yaʼni qirq yetti.**
   *Five salaries: thirty-one, forty-five, forty-seven, fifty-two, eighty-eight. They are sorted, n is five, so the middle one is the third: forty-seven.*
   ▸ five bars in a row; two from each end fade, the third glows
4. **Agar n juft boʻlsa-chi? Sakson sakkizni olib tashlaymiz. Toʻrtta qoldi, endi oʻrtada bitta emas, ikkita odam turibdi.**
   *What if n is even? Let's drop the eighty-eight. Now four are left, and there is not one middle person but two.*
5. **Bunday holatda ikkalasining oʻrtachasini olamiz. Qirq besh bilan qirq yetti — mediana qirq olti boʻladi.**
   *Then we take the average of those two: forty-five and forty-seven, so the median is forty-six.*
6. **Endi beshtasiga qaytaylik. Ularning oʻrtacha qiymati ellik ikki butun oʻndan olti. Bu beshta maoshdan toʻrttasidan katta! Bitta sakson sakkiz uni yuqoriga tortib ketdi. Mediana esa oʻrtadagi odamda qoldi.**
   *Back to the five. Their mean is fifty-two point six. That is larger than four of the five salaries! A single eighty-eight pulled it up, while the median stayed on the middle person.*
   ▸ red mean line at 52.6 above four bars; green median line on the third
7. **Demak, mediana odatiy odamni koʻrsatadi. Oʻrtacha qiymat esa umumiy summani teng boʻlsak, har kimga qancha tegishini koʻrsatadi.**
   *So the median describes a typical member of the sample. The mean describes each person's share if the total were split equally.*
8. **Shuning uchun statistika idoralari oilalar daromadini mediana bilan eʼlon qiladi. Uy narxlari ham xuddi shunday. Bir nechta milliarder yoki hashamatli uy oʻrtachani buzib yuboradi.**
   *That is why national statistics offices report median household income, and house prices the same way. A handful of billionaires or mansions would make the mean meaningless.*
9. **Yana bitta markaz bor — moda. Bu eng koʻp uchraydigan qiymat. Kategorial berilganlar uchun faqat moda ishlaydi: masalan, eng koʻp uchraydigan qon guruhi yoki doʻkonda eng koʻp sotiladigan oyoq kiyim oʻlchami.**
   *There is one more center: the mode, the value that appears most often. It is the only one that works for categorical data: the most common blood type, or the shoe size a shop sells most.*
10. **Demak, qoidamiz shunday. Simmetrik berilganlar va umumiy summa uchun — oʻrtacha qiymat. Qiyshiq berilganlar va juda katta qiymatlar boʻlsa — mediana. Kategorial berilganlar uchun — moda.**
    *Our rule of thumb: for symmetric data and for totals, the mean. For skewed data and extreme values, the median. For categorical data, the mode.*
    ▸ three cards, each with its data type icon
11. **Sunʼiy intellektda ham shunday. Berilganlardagi bitta xato, masalan bitta ortiqcha nol bilan yozilgan maosh, oʻrtachani buzib yuboradi, medianani esa deyarli qimirlatmaydi. Shuning uchun berilganlarni tozalashda koʻpincha medianaga tayanamiz.**
    *The same in AI: one error in the data, say a salary typed with an extra zero, wrecks the mean and barely moves the median. That is why data cleaning often leans on the median.*
12. ⏸ **Keling, oʻzimiz sinab koʻraylik. Videoni toʻxtating. Oʻtgan videodagi toʻqqizta maoshning medianasini topamiz.**
    *Let's try it ourselves. Pause the video. We find the median of the nine salaries from the last video.*
13. **Toʻqqizta qiymat bor, demak oʻrtadagisi beshinchisi — qirq yetti ming dollar. Oʻrtacha qiymat esa ellik ming uch yuz oʻttiz uch dollar edi.**
    *Nine values, so the middle one is the fifth: forty-seven thousand dollars. The mean was fifty thousand, three hundred and thirty-three.*
14. **Lekin markaz hamma narsani aytib bermaydi. Ikki xil berilganlarning oʻrtachasi bir xil boʻlib, oʻzi butunlay boshqacha boʻlishi mumkin. Bu keyingi videoda.**
    *But a center does not tell the whole story. Two datasets can share the same mean and behave completely differently. That is the next video.*

### Video 6 — Dispersiya · Variance
1. **Assalomu alaykum, aziz doʻstlar. Tasavvur qilamiz, ishga ikki xil yoʻl bilan borishimiz mumkin: avtobusda yoki mashinada. Besh kun avtobusda, besh kun mashinada yuramiz va vaqtini yozib boramiz.**
   *Hello, dear friends. Let's imagine we can get to work two ways: by bus or by car. We time five days by bus and five days by car.*
2. **Avtobusda: oʻttiz, yigirma toʻqqiz, oʻttiz bir, oʻttiz, oʻttiz daqiqa. Mashinada: oʻn sakkiz, qirq ikki, yigirma besh, oʻttiz besh, oʻttiz daqiqa.**
   *Bus: thirty, twenty-nine, thirty-one, thirty, thirty minutes. Car: eighteen, forty-two, twenty-five, thirty-five, thirty minutes.*
   ▸ two rows of dots on a minutes axis
3. **Ikkalasining oʻrtachasi ham roppa-rosa oʻttiz daqiqa. Faqat oʻrtachaga qarasak, ular bir xil.**
   *Both average exactly thirty minutes. If we only look at the mean, they are the same.*
4. **Lekin mashinada bir kuni oʻn ikki daqiqa kechikdik. Demak, bizga qiymatlar qanchalik tarqoq ekanini oʻlchaydigan son kerak.**
   *But one day by car we were twelve minutes late. We need a number that measures spread.*
5. **Keling, har bir kun oʻrtachadan qancha farq qilishini topaylik. Mashinada: minus oʻn ikki, plyus oʻn ikki, minus besh, plyus besh va nol.**
   *Let's take each day's distance from the mean. By car: minus twelve, plus twelve, minus five, plus five, zero.*
   ▸ arrows from the mean line to each car dot
6. **Shunchaki qoʻshsak, nol chiqadi, chunki musbatlar bilan manfiylar bir-birini yeb qoʻyadi. Shuning uchun har birini kvadratga oshiramiz.**
   *If we simply add them, we get zero: the pluses and minuses cancel. So we square each one first.*
   ▸ each arrow grows into a square: 144, 144, 25, 25, 0
7. **Kvadratlarni qoʻshsak, uch yuz oʻttiz sakkiz chiqadi. Uni n minus birga, yaʼni toʻrtga boʻlamiz: sakson toʻrt butun oʻndan besh. Mana shu dispersiya deb ataladi.**
   *The squares add up to three hundred and thirty-eight. We divide by n minus one, that is four: eighty-four point five. This is the variance.*
8. ⏸ **Keling, oʻzimiz sinab koʻraylik. Videoni toʻxtating. Avtobusning dispersiyasini ham xuddi shunday hisoblaymiz.**
   *Let's try it ourselves. Pause the video. We work out the bus's variance the same way.*
9. **Avtobusda farqlar bor-yoʻgʻi minus bir va plyus bir. Kvadratlar yigʻindisi ikki, dispersiya esa nol butun oʻndan besh.**
   *By bus the distances are only minus one and plus one. The squares add up to two, so the variance is zero point five.*
10. **Dispersiyaning birligi daqiqaning kvadrati, bu biroz gʻalati. Shuning uchun ildizdan chiqaramiz va standart chetlanishni olamiz: mashinada taxminan toʻqqiz daqiqa, avtobusda bir daqiqaga ham yetmaydi.**
    *Variance is measured in squared minutes, which is an odd unit. Taking the square root gives the standard deviation: about nine minutes by car, less than one minute by bus.*
11. **Nima uchun n ga emas, n minus birga boʻlamiz? Chunki oʻrtachani shu tanlanmaning oʻzidan hisobladik. Shuning uchun u tanlanmaga haqiqiy oʻrtachadan doim biroz yaqinroq boʻladi. n minus birga boʻlib, shu kamchilikni tuzatamiz.**
    *Why n minus one, not n? We computed the mean from the sample itself, so it always sits a little closer to the sample than the true mean does. Dividing by n minus one corrects for that.*
12. **Sunʼiy intellektda ikki modelning oʻrtacha aniqligi bir xil boʻlsa, natijasi har safar sakrab turadiganini emas, barqarorini tanlaymiz. Bu farqni aynan dispersiya koʻrsatadi.**
    *In AI, between two models with the same average accuracy, we choose the steady one over the one that jumps around from run to run. Variance is what shows the difference.*
13. **Keyingi videoda dispersiya qanday qilib haqiqiy pulga va chiqindiga aylanishini koʻramiz.**
    *In the next video, we see how variance turns into real money and real waste.*

### Video 7 — Tarqoqlik — bu xavf · Variance is risk
1. **Assalomu alaykum, aziz doʻstlar. Keling, ichimlik zavodiga boraylik. Shishaga besh yuz millilitr deb yozilgan. Qonun boʻyicha toʻrt yuz toʻqson beshdan besh yuz beshgacha boʻlishi mumkin.**
   *Hello, dear friends. Let's visit a bottling plant. The label says five hundred millilitres, and the law allows four hundred and ninety-five to five hundred and five.*
   ▸ a fill axis with the 495–505 band shaded
2. **Zavodda ikkita mashina bor. Ikkalasi ham oʻrtacha roppa-rosa besh yuz millilitr quyadi.**
   *There are two machines, and both fill exactly five hundred millilitres on average.*
3. **Birinchi mashinaning standart chetlanishi ikki millilitr. Chegaralar oʻrtachadan ikki yarim standart chetlanish uzoqda turibdi. Shuning uchun mingta shishadan bor-yoʻgʻi oʻn bittasi yaroqsiz chiqadi.**
   *Machine A has a standard deviation of two millilitres. The limits sit two and a half standard deviations out, so only eleven bottles in a thousand are rejected.*
   ▸ a narrow bell inside the band; a grid of 1000 bottles, 11 turn red
4. **Ikkinchi mashinaning standart chetlanishi toʻrt millilitr. Endi oʻsha chegaralar bor-yoʻgʻi bir butun toʻrtdan bir standart chetlanish uzoqda. Mingtadan ikki yuz oʻntasi yaroqsiz, yaʼni har beshinchi shisha.**
   *Machine B has a standard deviation of four millilitres. Now the same limits are only one and a quarter standard deviations out. Two hundred and ten in a thousand are rejected: one bottle in five.*
   ▸ a wide bell spilling past the band; 210 of the 1000 turn red
5. **Tarqoqlik ikki baravar oshdi, chiqindi esa oʻn toʻqqiz baravar koʻpaydi. Oʻrtacha qiymat esa bir millilitr ham oʻzgarmadi.**
   *The spread doubled, and the waste went up nineteen times. The mean never moved by a single millilitre.*
6. **Demak, zavod faqat oʻrtachani emas, tarqoqlikni ham nazorat qilishi kerak. Sifat nazoratidagi mashhur «Olti Sigma» gʻoyasi aynan shu.**
   *So the plant has to control the spread, not just the average. That is the whole idea behind Six Sigma quality control.*
7. **Kundalik hayotda ham shunday: vaqtida keladigan avtobus, navbati oldindan maʼlum boʻlgan klinika, haroratni bir xil ushlab turadigan pech. Oʻrtacha qiymat ishlar qanchalik tez-tez buzilishini hech qachon aytmaydi.**
   *Everyday life is the same: a bus that keeps its timetable, a clinic with predictable waiting times, an oven that holds its temperature. The average never tells us how often things go wrong.*
8. **Sunʼiy intellektda ham modelning bashoratidan tashqari, uning qanchalik ishonchsizligini, yaʼni tarqoqligini baholaymiz. Shunda modelga qachon ishonmaslik kerakligini bilamiz.**
   *In AI, we estimate not just a model's prediction but its uncertainty, its spread, so we know when not to trust it.*
9. ⏸ **Keling, oʻylab koʻraylik. Videoni toʻxtating. Ikkinchi mashinaning tarqoqligini kamaytirolmasak, uning oʻrtachasini qayerga qoʻyishimiz kerak?**
   *Let's think it through. Pause the video. If we cannot reduce machine B's spread, where should we set its average?*
10. **Aynan chegaralarning oʻrtasiga. Oʻrtachani qaysi tomonga sursak ham, bitta chegara yaqinlashadi va yaroqsiz shishalar koʻpayadi.**
    *Right in the middle of the limits. Whichever way we move the average, one limit gets closer, and more bottles are rejected.*
11. **Lekin dispersiya bitta juda katta qiymatga ham sezgir. Shunday qiymatlardan buzilmaydigan tarqoqlik oʻlchovi bormi? Bu keyingi videoda.**
    *But variance is very sensitive to a single extreme value. Is there a measure of spread that survives outliers? That is the next video.*

### Video 8 — Kvartillar va quti diagrammasi · Quartiles and box plots
1. **Assalomu alaykum, aziz doʻstlar. Mediana markazni juda katta qiymatlardan himoya qildi. Keling, tarqoqlik uchun ham xuddi shunday himoya quraylik.**
   *Hello, dear friends. The median protected the center from outliers. Let's build the same protection for spread.*
2. **Toʻqqizta maoshimizni tartib bilan teramiz. Mediana beshinchisi, yaʼni qirq yetti. U berilganlarni ikki yarmiga ajratadi.**
   *We take our nine salaries, sorted. The median is the fifth, forty-seven. It splits the data into two halves.*
   ▸ nine bars; the fifth glows and a divider drops
3. **Pastki yarmi: oʻttiz bir, oʻttiz sakkiz, qirq ikki, qirq besh. Uning medianasi oʻttiz sakkiz bilan qirq ikkining oʻrtachasi, yaʼni qirq. Bu birinchi kvartil deb ataladi, Q bir.**
   *The lower half: thirty-one, thirty-eight, forty-two, forty-five. Its median is the average of thirty-eight and forty-two: forty. That is the first quartile, Q one.*
4. **Yuqori yarmi: qirq toʻqqiz, ellik ikki, oltmish bir, sakson sakkiz. Uning medianasi ellik olti yarim. Bu uchinchi kvartil, Q uch.**
   *The upper half: forty-nine, fifty-two, sixty-one, eighty-eight. Its median is fifty-six and a half. That is the third quartile, Q three.*
5. **Endi beshta son bilan berilganlarni tasvirlaymiz: eng kichigi, Q bir, mediana, Q uch va eng kattasi. Oʻttiz bir, qirq, qirq yetti, ellik olti yarim va sakson sakkiz.**
   *Now five numbers describe the data: the minimum, Q one, the median, Q three and the maximum. Thirty-one, forty, forty-seven, fifty-six and a half, eighty-eight.*
6. **Q uchdan Q birni ayirsak, kvartillararo oraliq chiqadi, qisqacha IQR. Bu oʻrtadagi yarim berilganlarning kengligi. Mana bu yerda oʻn olti yarim. U ham medianaga oʻxshab, juda katta qiymatlardan buzilmaydi.**
   *Q three minus Q one is the interquartile range, the IQR: the width of the middle half of the data. Here, sixteen and a half. Like the median, it survives extreme values.*
7. **Endi chetga chiqqan qiymatlarni topamiz. Q uchga bir yarim IQR qoʻshamiz: sakson bir butun yuzdan yigirma besh chiqadi. Bundan yuqoridagi har qanday qiymat chetga chiqqan hisoblanadi.**
   *Now we can flag outliers. Add one and a half IQRs to Q three: eighty-one point two five. Anything above that counts as an outlier.*
8. **Sakson sakkiz bu chegaradan oshib ketdi. Demak, sakson sakkiz ming dollarlik maosh — chetga chiqqan qiymat.**
   *Eighty-eight is past that fence. So the eighty-eight thousand dollar salary is flagged as an outlier.*
9. **Endi hammasini bitta rasmga chizamiz: Q birdan Q uchgacha quti, ichida mediana chizigʻi, ikki tomonda moʻylovlar va alohida nuqta — chetga chiqqan qiymat. Bu quti diagrammasi deb ataladi.**
   *We draw all of this as one picture: a box from Q one to Q three, a median line inside, whiskers, and a separate dot for the outlier. This is a box plot.*
   ▸ the nine bars turn sideways and collapse into the box plot
10. **Uning kuchi guruhlarni solishtirganda koʻrinadi. Xizmat koʻrsatish markazining uchta filialida kutish vaqtini olaylik. A filialida mediana oʻn bir butun oʻndan sakkiz daqiqa, B filialida oʻn yetti butun oʻndan yetti, C filialida esa yigirma toʻqqiz yarim.**
    *Its strength is comparing groups. Waiting times at three branches of a service centre: branch A has a median of eleven point eight minutes, branch B seventeen point seven, branch C twenty-nine point five.*
    ▸ three box plots side by side
11. **C filiali ham eng sekin, ham eng beqaror: uning qutisi deyarli yigirma daqiqa keng. Bitta oʻrtacha son qaysi filialni tuzatish kerakligini koʻrsatib berolmas edi.**
    *Branch C is both the slowest and the most variable: its box is almost twenty minutes wide. A single average would not tell us which branch to fix.*
12. **Sunʼiy intellektda modelni oʻqitishdan oldin aynan shu qoida bilan gʻalati qiymatlarni topamiz: xato yozilgan yozuvlar, sensor xatolari va hokazo.**
    *In AI, before training a model we use exactly this rule to catch strange values: mistyped records, sensor glitches.*
13. ⏸ **Keling, oʻzimiz sinab koʻraylik. Videoni toʻxtating. Pastki chegarani hisoblaymiz, yaʼni Q birdan bir yarim IQR ni ayiramiz. Undan pastda qiymat bormi?**
    *Let's try it ourselves. Pause the video. We work out the lower fence, Q one minus one and a half IQRs. Is any value below it?*
14. **Pastki chegara oʻn besh butun yuzdan yigirma besh. Eng kichik maosh oʻttiz bir. Demak, pastda chetga chiqqan qiymat yoʻq.**
    *The lower fence is fifteen point two five. The smallest salary is thirty-one, so there is no outlier at the bottom.*
15. **Lekin beshta son ham bizni aldashi mumkin. Keyingi videoda statistikasi bir xil, lekin rasmi butunlay boshqacha boʻlgan toʻrtta berilganlar toʻplamini koʻramiz.**
    *But even five numbers can fool us. In the next video, four datasets with the same statistics and completely different pictures.*

### Video 9 — Berilganlarni doim chizamiz · Always plot the data (Anscombe)
1. **Assalomu alaykum, aziz doʻstlar. Keling, toʻrtta berilganlar toʻplamini olaylik. Har birida oʻn bittadan nuqta bor.**
   *Hello, dear friends. Let's take four datasets. Each has eleven points.*
   ▸ four tables of numbers, no plots yet
2. **Ularning statistikasini hisoblaymiz. x ning oʻrtachasi toʻrttasida ham toʻqqiz. y ning oʻrtachasi ham toʻrttasida yetti yarim.**
   *Let's compute their statistics. The mean of x is nine in all four. The mean of y is seven and a half in all four.*
3. **x ning dispersiyasi hammasida oʻn bir. Korrelyatsiya hammasida taxminan nol butun mingdan sakkiz yuz oʻn olti. Hatto eng yaxshi toʻgʻri chiziq ham bir xil: y teng uch qoʻshuv x ning yarmi.**
   *The variance of x is eleven in all of them. The correlation is about zero point eight one six in all of them. Even the best-fitting line is the same: y equals three plus half of x.*
4. **Raqamlarga qarasak, toʻrttasi ham bir xil. Xoʻp, endi ularni chizib koʻraylik.**
   *By the numbers, these are the same dataset four times. Now let's draw them.*
5. **Birinchisi — oddiy chiziqli bogʻlanish, atrofida biroz tarqoqlik bor. Mana bu yerda toʻgʻri chiziq toʻgʻri keladi.**
   *The first: an ordinary straight-line relationship with some scatter. Here, a line fits.*
6. **Ikkinchisi — mukammal egri chiziq. Bu yerda toʻgʻri chiziq umuman notoʻgʻri model.**
   *The second: a perfect curve. Here, a straight line is the wrong model entirely.*
7. **Uchinchisi — mukammal toʻgʻri chiziq, lekin bitta chetga chiqqan nuqta chiziqni oʻziga tortib ketgan.**
   *The third: a perfect line, but one outlier pulls the fitted slope toward itself.*
8. **Toʻrtinchisida esa hech qanday bogʻlanish yoʻq. Faqat bitta uzoqdagi nuqta kuchli korrelyatsiya bordek koʻrsatyapti.**
   *The fourth: no relationship at all. A single far-off point fakes a strong correlation.*
9. **Bu toʻrtta toʻplamni statistik Frensis Enskomb ming toʻqqiz yuz yetmish uchinchi yilda aynan shuni koʻrsatish uchun eʼlon qilgan: berilganlarni chizmasdan turib, statistikaga ishonmang.**
   *The statistician Francis Anscombe published these four datasets in nineteen seventy-three for exactly this reason: never trust the statistics without plotting the data.*
10. **Sunʼiy intellektda bu juda muhim. Aniqlik kabi bitta son model toʻgʻri tanlanganini aytmaydi. Modelga ishonishdan oldin uning nuqtalarini va xatolarini doim chizib koʻramiz.**
    *In AI this matters a lot: one number like accuracy does not tell us the model is the right one. Before we trust a model, we always plot its points and its errors.*
11. ⏸ **Keling, oʻylab koʻraylik. Videoni toʻxtating. Toʻrttasidan qaysi birida toʻgʻri chiziqli model haqiqatan toʻgʻri keladi?**
    *Let's think it through. Pause the video. In which of the four is a straight-line model actually right?*
12. **Faqat birinchisida. Qolgan uchtasida oʻsha chiziq bizni aldaydi.**
    *Only the first. In the other three, the same line misleads us.*
13. **Mana shu bilan maʼruzamizning birinchi qismini tugatamiz. Keyingi qismda noaniqlikni oʻlchashni oʻrganamiz, yaʼni ehtimollikni.**
    *That brings us to the end of the first part of this lecture. In the next part we learn to measure uncertainty: probability.*

---

## Part 1 — Ehtimollik

### Video 10 — Namunalar fazosi, hodisa, ehtimollik · Sample space, event, probability
1. **Assalomu alaykum, aziz doʻstlar. Maʼruzamizning ikkinchi qismiga xush kelibsiz. Ertaga yomgʻir yogʻadimi? Kubik olti koʻrsatadimi? Keling, bunday savollarni songa aylantirishni oʻrganaylik.**
   *Hello, dear friends, and welcome to the second part of our lecture. Will it rain tomorrow? Will the die show a six? Let's learn to turn questions like these into numbers.*
2. **Birinchi qadam — natijaga qarashdan oldin, nima boʻlishi mumkin boʻlsa, hammasini yozib chiqamiz. Kubikda bu bir, ikki, uch, toʻrt, besh, olti. Buni namunalar fazosi deymiz va omega bilan belgilaymiz.**
   *Step one: before we look, we write down everything that could happen. For a die, that is one, two, three, four, five, six. We call this the sample space, and write it as omega.*
   ▸ six die faces drop into a set Ω
3. **Tangada: gerb yoki raqam. Ertangi kun uchun: yomgʻir yogʻadi yoki yogʻmaydi.**
   *For a coin: heads or tails. For tomorrow: rain or no rain.*
4. **Ikkinchi qadam — savolimizni yozamiz. Kubik juft son koʻrsatadimi? Javobi «ha» boʻladigan natijalarni yigʻamiz: ikki, toʻrt, olti. Mana shu toʻplam hodisa deb ataladi.**
   *Step two: we write down our question. Will the die show an even number? We collect the outcomes that answer yes: two, four, six. That set is called an event.*
   ▸ 2, 4, 6 lift out of Ω into a ring labelled A
5. **Uchinchi qadam — har bir hodisaga noldan birgacha bitta son beramiz. Nol — boʻlishi mumkin emas, bir — albatta boʻladi. Omeganing ehtimoli doim bir, chunki nimadir albatta sodir boʻladi.**
   *Step three: we give each event one number between zero and one. Zero means impossible, one means certain. The probability of omega is always one, because something must happen.*
6. **Toʻgʻri kubikda juft son chiqish ehtimoli: oltitadan uchtasi, yaʼni ikkidan bir.**
   *For a fair die, the probability of an even number is three outcomes out of six: one half.*
7. **Nima uchun toʻplamlar bilan ishlaymiz? Chunki savol toʻplamga aylansa, «yoki» birlashma boʻladi, «va» kesishma boʻladi, «emas» esa toʻldiruvchi boʻladi. Qolgan hisobni qoidalar qiladi.**
   *Why bother with sets? Because once a question is a set, "or" becomes a union, "and" becomes an intersection, and "not" becomes a complement. Then the rules do the counting for us.*
8. **Sunʼiy intellektda klassifikator aynan shunday ishlaydi. Har bir sinf uchun noldan birgacha ehtimol beradi va ularning yigʻindisi birga teng boʻladi.**
   *In AI, a classifier works exactly like this: it outputs a probability between zero and one for each class, and they add up to one.*
9. ⏸ **Keling, oʻzimiz sinab koʻraylik. Videoni toʻxtating. «Kubik toʻrtdan katta son koʻrsatadi» degan hodisani yozamiz va ehtimolini topamiz.**
   *Let's try it ourselves. Pause the video. We write down the event "the die shows more than four", and find its probability.*
10. **Besh va olti. Oltitadan ikkitasi, yaʼni uchdan bir.**
    *Five and six. Two out of six: one third.*
11. **Keyingi videoda bu ehtimollarni birlashtiradigan uchta qoidani koʻramiz.**
    *In the next video, the three rules that combine these probabilities.*

### Video 11 — Uchta qoida · The three rules
1. **Assalomu alaykum, aziz doʻstlar. Oddiy hodisalarning ehtimolini topishni bilamiz. Murakkab hodisalarnikini qanday topamiz? Buning uchun uchta qoida yetarli.**
   *Hello, dear friends. We have the probabilities of simple events. How do we get them for complicated ones? Three rules are enough.*
2. **Birinchisi — toʻldiruvchi qoidasi. A sodir boʻlmasligining ehtimolini topish uchun birdan A ning ehtimolini ayiramiz. Juft son chiqmasligi: birdan ikkidan birni ayiramiz, yaʼni ikkidan bir.**
   *The first is the complement rule. The probability that A does not happen is one minus the probability of A. Not even: one minus a half, which is a half.*
3. **Bu qoida «hech boʻlmaganda bittasi» degan savollarda juda qulay: hech biri boʻlmasligini hisoblab, birdan ayiramiz.**
   *It is the easy way into "at least one" questions: we work out "none", and subtract it from one.*
4. **Ikkinchisi — qoʻshish qoidasi. Keling, ellik ikkita kartadan bittasini olaylik. Yurak belgili karta chiqishi — ellik ikkidan oʻn uch. Qirol chiqishi — ellik ikkidan toʻrt.**
   *The second is the addition rule. Let's draw one card from fifty-two. A heart: thirteen out of fifty-two. A king: four out of fifty-two.*
   ▸ the 52-card grid; the hearts row and the kings column light up
5. **Yurak yoki qirol chiqish ehtimoli-chi? Oʻn uch qoʻshuv toʻrt emas. Chunki yurak qiroli ikkala guruhda ham bor, uni ikki marta sanab qoʻyamiz.**
   *What about a heart or a king? Not thirteen plus four. The king of hearts is in both groups; we would count it twice.*
   ▸ the crossing card flashes
6. **Shuning uchun kesishmani bir marta ayiramiz: oʻn uch qoʻshuv toʻrt minus bir, yaʼni ellik ikkidan oʻn olti.**
   *So we subtract the overlap once: thirteen plus four minus one, sixteen out of fifty-two.*
7. **Uchinchisi — koʻpaytirish qoidasi. A va B ning birga sodir boʻlish ehtimolini topish uchun A ning ehtimolini A sodir boʻlgandagi B ning ehtimoliga koʻpaytiramiz.**
   *The third is the multiplication rule. The probability of A and B together is the probability of A, times the probability of B given that A has happened.*
8. **Masalan, yurak qiroli. Avval yurak chiqishi — ellik ikkidan oʻn uch. Yurak chiqqanini bilsak, uning qirol boʻlishi — oʻn uchdan bir. Koʻpaytirsak, ellik ikkidan bir chiqadi.**
   *The king of hearts: first a heart, thirteen out of fifty-two. Given it is a heart, the chance it is a king is one in thirteen. Multiply them: one out of fifty-two.*
9. **Mana shu «… sodir boʻlgandagi» degan tushuncha shartli ehtimollik deb ataladi. Uni ikkinchi maʼruzada chuqur oʻrganamiz.**
   *That word "given" is conditional probability. We study it in depth in Lecture 2.*
10. **Sunʼiy intellektda til modeli gapni aynan koʻpaytirish qoidasi bilan baholaydi: har bir soʻzning ehtimolini oldingi soʻzlarga qarab hisoblaydi va hammasini koʻpaytiradi.**
    *In AI, a language model scores a sentence with exactly the multiplication rule: the probability of each word given the words before it, all multiplied together.*
11. ⏸ **Keling, oʻzimiz sinab koʻraylik. Videoni toʻxtating. Karta yurak ham, qirol ham boʻlmaslik ehtimoli qancha?**
    *Let's try it ourselves. Pause the video. What is the probability that the card is neither a heart nor a king?*
12. **Toʻldiruvchi qoidasi bilan: birdan ellik ikkidan oʻn oltini ayiramiz, yaʼni ellik ikkidan oʻttiz olti.**
    *The complement rule: one minus sixteen out of fifty-two, which is thirty-six out of fifty-two.*
13. **Keyingi videoda toʻldiruvchi qoidasi deyarli hammani aldaydigan savolga javob beradi.**
    *In the next video, the complement rule answers a question that fools almost everyone.*

### Video 12 — Tugʻilgan kun masalasi · The birthday problem
1. **Assalomu alaykum, aziz doʻstlar. Xonada nechta odam boʻlsa, ikkitasining tugʻilgan kuni bir xil boʻlish ehtimoli yarimdan oshadi? Koʻpchilik yuz saksonta atrofida deb oʻylaydi.**
   *Hello, dear friends. How many people must be in a room before the chance that two share a birthday passes one half? Most people guess around one hundred and eighty.*
2. **Keling, toʻgʻridan-toʻgʻri sanab koʻraylik: kimdir kim bilandir bir kunda tugʻilgan hamma holatlarni. Juftlar, uchliklar, bir nechta juftlar — sanash tezda chalkashib ketadi.**
   *Let's try to count it directly: every case where someone shares a birthday with someone. Pairs, triples, several pairs at once; the counting gets messy fast.*
3. **Shuning uchun teskarisini hisoblaymiz: hammaning tugʻilgan kuni har xil boʻlsin. Keyin buni birdan ayiramiz.**
   *So we compute the opposite: everyone's birthday is different. Then we subtract it from one.*
4. **Birinchi odam istalgan kunda tugʻilishi mumkin. Ikkinchisi qolgan uch yuz oltmish toʻrt kunning birida tugʻilishi kerak. Uchinchisi uch yuz oltmish uch kunning birida, va hokazo.**
   *The first person can have any birthday. The second must land on one of the other three hundred and sixty-four days. The third on one of three hundred and sixty-three, and so on.*
   ▸ a 365-cell calendar; each new person takes a free cell
5. **Shu kasrlarni koʻpaytiramiz va natijani birdan ayiramiz.**
   *We multiply those fractions together, and subtract the result from one.*
6. **Oʻn kishi boʻlsa, ehtimol bor-yoʻgʻi oʻn ikki foiz. Yigirma uch kishi boʻlsa, ellik butun oʻndan yetti foiz. Yarimdan oshdi!**
   *With ten people the chance is only twelve percent. With twenty-three, it is fifty point seven percent. Past one half!*
   ▸ the curve draws itself point by point; a marker stops at 23
7. **Ellik kishida toʻqson yetti foiz, yetmish kishida esa deyarli aniq.**
   *With fifty people, ninety-seven percent. With seventy, almost certain.*
8. **Nima uchun sezgimiz adashadi? Chunki biz oʻzimizni boshqalar bilan solishtiramiz. Aslida esa har bir juftlik hisobga kiradi: yigirma uch kishidan ikki yuz ellik uchta juftlik chiqadi.**
   *Why does our intuition fail? Because we compare ourselves with the others. In fact every pair counts: twenty-three people make two hundred and fifty-three pairs.*
   ▸ 23 dots, then all 253 connecting lines
9. **Kompyuter fanlari va sunʼiy intellektda xuddi shu hisob bilan xesh toʻqnashuvlari va berilganlardagi takrorlanishlar baholanadi: ular biz kutganimizdan ancha tez paydo boʻladi.**
   *In computing and AI, the same calculation estimates hash collisions and duplicates in data: they show up much sooner than we expect.*
10. ⏸ **Keling, oʻzimiz sinab koʻraylik. Videoni toʻxtating. Oʻttiz kishilik guruhda ehtimol qancha? Grafikdan topamiz.**
    *Let's try it ourselves. Pause the video. In a class of thirty, what is the chance? Let's read it off the curve.*
11. **Taxminan yetmish bir foiz. Demak, oʻttiz kishilik guruhlarning koʻpchiligida tugʻilgan kuni bir xil boʻlgan juftlik bor.**
    *About seventy-one percent. Most classes of thirty have a shared birthday.*
12. **Bu hisobda biz odamlarning tugʻilgan kunlari bir-biriga bogʻliq emas deb oldik. «Bogʻliq emas» degani aslida nima? Bu keyingi videoda.**
    *In that calculation we assumed people's birthdays have nothing to do with each other. What does that really mean? That is the next video.*

### Video 13 — Istisno qiluvchi va erkli hodisalar · Mutually exclusive vs. independent
1. **Assalomu alaykum, aziz doʻstlar. Ikkita tushuncha koʻpincha adashtiriladi: bir-birini istisno qiluvchi hodisalar va erkli hodisalar. Keling, farqini kubik misolida koʻraylik.**
   *Hello, dear friends. Two ideas get mixed up all the time: mutually exclusive and independent. Let's see the difference on a die.*
2. **Ikki hodisa hech qachon birga sodir boʻlmasa, ular bir-birini istisno qiladi. Kesishmasi boʻsh, birga sodir boʻlish ehtimoli nol.**
   *Two events are mutually exclusive if they can never happen together: their overlap is empty, and the probability of both is zero.*
3. **Ikki hodisaning birga sodir boʻlish ehtimoli ularning ehtimollari koʻpaytmasiga teng boʻlsa, ular erkli deyiladi. Yaʼni birini bilish ikkinchisi haqida hech narsa aytmaydi.**
   *Two events are independent if the probability of both equals the product of their probabilities. In other words, knowing one tells us nothing about the other.*
4. **Kubik tashlaymiz. A — juft son: ikki, toʻrt, olti, ehtimoli ikkidan bir. B — toʻrtdan katta son: besh, olti, ehtimoli uchdan bir.**
   *We roll a die. A is "even": two, four, six, with probability one half. B is "more than four": five, six, with probability one third.*
   ▸ Venn diagram over the six faces
5. **Ikkalasi birga faqat oltida boʻladi, ehtimoli oltidan bir. Ikkidan birni uchdan birga koʻpaytirsak ham oltidan bir chiqadi. Demak, A va B erkli.**
   *Both together: only six, with probability one sixth. And one half times one third is also one sixth. So A and B are independent.*
6. **Lekin ular bir-birini istisno qilmaydi, chunki olti ikkalasida ham bor.**
   *But they are not mutually exclusive: six belongs to both.*
7. **Xoʻp, endi teskarisini olaylik: juft va toq. Ular bir-birini istisno qiladi. Ular erklimi?**
   *Now the reverse: even and odd. They are mutually exclusive. Are they independent?*
8. **Yoʻq! Son juft chiqqanini bilsak, toq emasligini aniq bilamiz. Bu kuchli bogʻliqlik. Ehtimollar koʻpaytmasi toʻrtdan bir, haqiqiy ehtimol esa nol.**
   *No! If we know the number came up even, we know for certain it is not odd. That is strong dependence. The product of the probabilities is one quarter, but the real probability is zero.*
9. **Demak, qoida shunday: ehtimoli noldan katta boʻlgan ikkita istisno qiluvchi hodisa doim bogʻliq boʻladi.**
   *The rule: two mutually exclusive events with nonzero probability are always dependent.*
10. **Sunʼiy intellektda mashhur sodda Bayes klassifikatori aynan erklilik farazi ustiga qurilgan: u har bir soʻzni boshqa soʻzlardan erkli deb hisoblaydi.**
    *In AI, the well-known naive Bayes classifier is built on exactly this assumption: it treats each word as independent of the others.*
11. ⏸ **Keling, oʻzimiz sinab koʻraylik. Videoni toʻxtating. «Juft son» va «uchdan kichik son» hodisalari erklimi?**
    *Let's try it ourselves. Pause the video. Are the events "even" and "less than three" independent?*
12. **Kesishmasi faqat ikki, ehtimoli oltidan bir. Ikkidan birni uchdan birga koʻpaytirsak ham oltidan bir. Demak, erkli.**
    *Their overlap is only two: one sixth. One half times one third is also one sixth. So they are independent.*
13. **Hozirgacha biz toʻgʻri kubikda sanadik. Lekin hayotda hamma natijalar teng ehtimolli boʻlishi kamdan-kam uchraydi. Bu keyingi videoda.**
    *So far we have counted on a fair die. But in the real world, equally likely outcomes are rare. That is the next video.*

### Video 14 — Klassik va empirik ehtimollik · Classical vs. empirical probability
1. **Assalomu alaykum, aziz doʻstlar. Ob-havo maʼlumotida eshitamiz: ertaga yomgʻir yogʻish ehtimoli yetmish foiz. Bu son qayerdan olinadi?**
   *Hello, dear friends. The weather forecast says: seventy percent chance of rain tomorrow. Where does that number come from?*
2. **Kubikda biz klassik ehtimollikdan foydalandik. Hamma natijalar teng ehtimolli boʻlsa, hodisadagi natijalar sonini jami natijalar soniga boʻlamiz.**
   *On the die, we used classical probability: when all outcomes are equally likely, we divide the outcomes in the event by the total number of outcomes.*
3. **Ob-havoda esa teng ehtimolli natijalar yoʻq, sanaydigan fazomiz ham yoʻq.**
   *Weather has no equally likely outcomes. There is no sample space to count.*
4. **Buning oʻrniga oʻtmishga qaraymiz: bugungidek sharoit boʻlgan oʻtgan kunlarning taxminan yetmish foizida yomgʻir yoqqan. Bu empirik ehtimollik deb ataladi.**
   *Instead, we look at the past: of all past days with conditions like today's, it rained on about seventy percent. That is empirical probability.*
   ▸ a grid of past days filling with rain/no-rain icons (labelled as an illustration)
5. **Formulasi oddiy: hodisa necha marta kuzatilganini jami kuzatuvlar soniga boʻlamiz.**
   *The formula is simple: the number of times the event was observed, divided by the total number of observations.*
6. **Masalan, olti yuzta xodimimizdan uch yuz oʻn bittasi qirq mingdan oltmish minggacha oladi. Demak, tasodifiy tanlangan xodimning shu oraliqda boʻlish ehtimoli taxminan ellik ikki foiz.**
   *For example, of our six hundred employees, three hundred and eleven earn between forty and sixty thousand. The empirical probability that a random employee lands there is about fifty-two percent.*
   ▸ the histogram from video 3; the 40–60k bar lifts out: 311 / 600
7. **Sunʼiy intellekt deyarli doim empirik ehtimollikka tayanadi: oʻqitish toʻplamidagi sinflar ulushi, matnlardagi soʻzlar chastotasi, reklamani bosishlar ulushi va hokazo.**
   *AI almost always relies on empirical probability: class shares in a training set, word frequencies in a corpus, click-through rates in logs.*
8. ⏸ **Keling, oʻylab koʻraylik. Videoni toʻxtating. Spam filtrni toʻqson foizi spam boʻlgan berilganlarda oʻqitdik. Shu berilganlardan olingan spam ehtimoli haqiqiy pochtaga toʻgʻri keladimi?**
   *Let's think it through. Pause the video. We trained a spam filter on data where ninety percent of emails are spam. Is the spam probability from that data right for real email?*
9. **Yoʻq. Empirik ehtimollik faqat berilganlar olingan joy uchun toʻgʻri. Tanlanma bosh toʻplamga oʻxshamasa, ehtimol ham notoʻgʻri chiqadi.**
   *No. An empirical probability is only right for the place the data came from. If the sample does not look like the population, the probability is wrong too.*
10. **Keling, maʼruzani yakunlaylik. Berilganlar turi qaysi hisob toʻgʻri ekanini belgilaydi. Oʻrtacha qiymat umumiy summani eslab qoladi, mediana esa juda katta qiymatlardan buzilmaydi. Dispersiya va IQR xavfni oʻlchaydi. Berilganlarni doim chizib koʻramiz. Ehtimollik qoidalari esa murakkab hodisalarni oddiylari orqali hisoblaydi.**
    *Let's wrap up the lecture. The type of data decides which calculations are valid. The mean remembers the total; the median survives outliers. Variance and the IQR measure risk. We always plot the data. And the probability rules build complex events from simple ones.*
11. **Mana shu bilan birinchi maʼruzamizni tugatamiz. Keyingi maʼruzada «… sodir boʻlgandagi» degan soʻzning kuchini koʻramiz: shartli ehtimollik va Bayes teoremasi.**
    *That brings our first lecture to an end. In the next lecture, we see the power of the word "given": conditional probability and Bayes' theorem.*
