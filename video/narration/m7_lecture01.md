# Module 7, Lecture 1 — What is an agent? — video narration (draft 1, for approval)

**The English video has its own narration since 2026-10-17** (`m7_lecture01_en.md`, on UK law); the italic
English lines here are a gloss of the Uzbek, for review only.

**One video for the lecture** (the slides have one part): a lecture opening, then ten sections, each with a short
section card ("3-boʻlim · ReAct"). Each section: problem first → concept as the answer → the real agent → a hands-on
pause → the question the next section answers. Built fresh for this course, not from the short agent-course video.

**The agent on screen is our class agent** (`agents/class_agent/`) on the real Labor Code of Uzbekistan (2022, 581
articles). Every run shown is a recording in `agents/class_agent/traces/`, and every fact quoted from it is asserted
in `test_class_agent.py`. Cost and reliability numbers come from `video/m7/raw/l01_numbers.json`
(`m7/capture_l01.py`, tested in `m7/test_l01.py` against the slides). Narration spells numbers; the screen shows digits.

**Voice:** "we", never "you"; only the pause card says *Videoni toʻxtating*. No Latin letter names in the narration
(the cloned voice blurs them): the screen shows S, a, n, p, k; the voice says the term.

**New terms — please approve or correct** (Module 7 has none recorded yet):

| English | Uzbek (proposed) | note |
|---|---|---|
| agent | agent | |
| pipeline | konveyer | a fixed sequence of steps |
| tool | vosita | |
| action / thought / observation | harakat / fikr / kuzatuv | the three lines of a ReAct turn |
| action space | harakatlar toʻplami | |
| trajectory | traektoriya | |
| scratchpad | qoralama | |
| context window | kontekst oynasi | |
| system prompt | tizim koʻrsatmasi | |
| token | token | |
| step limit | qadamlar chegarasi | |
| cache | kesh | the screen may show "KV kesh"; the voice says «kesh» |
| cite / citation | manba qilib koʻrsatish / manba | |
| grounded | manbaga tayangan | |
| reliability | ishonchlilik | |
| compounding errors | xatolarning toʻplanishi | |
| search / fetch article / answer | qidiruv / moddani olish / javob | the screen keeps `search[…]`, `fetch_article[…]`, `answer[…]` |
| Labor Code, article | Mehnat kodeksi, modda | |
| ReAct | «Riekt» (spoken) | the screen shows ReAct; please say how you pronounce it |
| chatbot | chatbot | |

Format per line: **UZ** (your voice) · *EN* (English track) · ▸ visual.

---

## Lecture opening
▸ title card "7-modul · 1-maʼruza" → "Agent nima?"
0. **Assalomu alaykum, aziz doʻstlar! Yettinchi modulning birinchi maʼruzasiga xush kelibsiz. Ushbu modulda biz agentlar bilan ishlaymiz — bular shunday dasturlarki, ularda til modeli mustaqil qarorlar qabul qiladi va turli vositalarni ishga tushiradi.**
   *Hello, dear friends, and welcome to the first lecture of module seven. In this module we work with agents: programs in which a language model makes its own decisions and calls tools.*
1. **Bugungi savolimiz oddiy: agent nima, va u oddiy dasturdan nimasi bilan farq qiladi? Javobni nazariyadan emas, haqiqiy misoldan topamiz. Oʻzbekiston Mehnat kodeksi ustida kichik agent quramiz va uning har bir qadamini koʻrib chiqamiz.**
   *Today's question is simple: what is an agent, and how is it different from an ordinary program? We find the answer not in theory but in a real example. We build a small agent on the Labor Code of Uzbekistan and look at every step it takes.*
   ▸ the code's cover line "Oʻzbekiston Respublikasining Mehnat kodeksi", 581 article tiles fill the screen

### 1-boʻlim · Section 1 — Nega agent kerak? · Why do we need an agent?
2. **Keling, bitta savoldan boshlaymiz: normal ish haftasi eng koʻpi bilan necha soat? Bu savolga bitta qidiruv yetarli. Kodeksdan kerakli moddani topamiz, oʻqiymiz, va javob beramiz.**
   *Let's start with one question: at most, how many hours is a normal working week? One search is enough for it. We find the right article in the code, read it, and answer.*
   ▸ a row of boxes: savol → qidiruv → javob
3. **Bunday qatʼiy ketma-ketlikni pipeline deymiz. Qadamlar tartibini dasturchi oldindan yozib qoʻygan: avval qidiruv, keyin javob. Qadamlar soni ham oldindan maʼlum.**
   *We call such a fixed sequence a pipeline. The programmer wrote the order of the steps in advance: first search, then answer. The number of steps is known in advance too.*
4. **Endi savolni biroz oʻzgartiramiz: oʻn sakkiz yoshga toʻlmagan xodimlar uchun bu chegara boshqachami? Endi bitta qidiruv yetmaydi. Umumiy qoidani topamiz, oʻqiymiz, unda yosh haqida hech narsa yoʻqligini koʻramiz, va yana qidiramiz.**
   *Now let's change the question a little: is that limit different for employees under eighteen? Now one search is not enough. We find the general rule, read it, see that it says nothing about age, and search again.*
5. **Necha marta qidiramiz? Buni oldindan hech kim bilmaydi. Keyingi qadam oldingi qadam nima qaytarganiga bogʻliq.**
   *How many times will we search? Nobody knows in advance. The next step depends on what the previous step returned.*
6. **Agent aynan shu muammoning yechimi. Agentda keyingi qadamni dasturchi emas, model tanlaydi. «Yana bir qidiruv kerak» degan qarorni model oʻzi qabul qiladi, kerak boʻlsa uchinchisini ham.**
   *An agent is exactly the answer to this problem. In an agent, the model, not the programmer, chooses the next step. The model itself decides that one more search is needed, and a third one if it must.*
   ▸ the row re-forms: the arrow out of "vosita" bends back into "model"
7. **Ikki chizmani yonma-yon qoʻyaylik. Ikkalasida ham model bor, vosita bor. Farq bitta strelkada: agentda strelka orqaga qaytadi. Sikldan necha marta oʻtishni model hal qiladi.**
   *Let's put the two diagrams side by side. Both have a model and a tool. The difference is one arrow: in the agent, the arrow goes back. The model decides how many times to go round the loop.*
   ▸ pipeline above, agent below; the back arrow pulses
8. **Bir daqiqaga toʻxtaymiz. Ikki savolni olamiz: «yillik taʼtil necha kun?» va «oʻn yetti yoshli xodim haftasiga va kuniga necha soat ishlay oladi?». Qaysi biriga bitta qidiruv yetadi, qaysi biriga bir nechta kerak?**
   *Let's pause for a minute. Take two questions: how many days of annual leave? And how many hours a week and a day may a seventeen-year-old work? Which one needs one search, and which needs several?*
   ▸ pause card
9. **Demak, agent sikl ichida ishlaydi. Xoʻp, endi bu siklning qismlariga nom beraylik.**
   *So an agent works inside a loop. Now let's name the parts of that loop.*

### 2-boʻlim · Section 2 — Vosita, harakat, traektoriya · Tool, action, trajectory
10. **Birinchi tushuncha — vosita. Vosita bu model nomi bilan chaqira oladigan funksiya. Model uni faqat matndagi tavsifidan biladi.**
    *The first concept is a tool. A tool is a function the model can ask for by name. The model knows it only from its description in text.*
11. **Bizning agentimizda uchta harakat bor. Qidiruv soʻzlar boʻyicha moddalarni topadi. Moddani olish bitta moddaning toʻliq matnini beradi. Javob esa ishni tugatadi, va undagi har bir daʼvo modda raqami bilan koʻrsatiladi.**
    *Our agent has three actions. Search finds articles by words. Fetch article returns one article's full text. Answer ends the run, and every claim in it is cited by its article number.*
    ▸ three cards: `search[…]` · `fetch_article[…]` · `answer[…]`
12. **Har bir qadamda tanlash mumkin boʻlgan harakatlarning hammasi harakatlar toʻplami deyiladi. Bizda bu toʻplam uchta harakatdan iborat.**
    *All the actions available at one step are called the action space. Ours has three.*
13. **Bitta vazifa uchun yozilgan barcha fikrlar, harakatlar va kuzatuvlar ketma-ketligi traektoriya deyiladi. Sakkizinchi maʼruzada agentni faqat oxirgi javobi boʻyicha emas, butun traektoriyasi boʻyicha baholaymiz.**
    *The whole sequence of thoughts, actions and observations for one task is called a trajectory. In lecture eight we grade an agent by its whole trajectory, not only by its last answer.*
14. **Eng muhim nuqta shuki: model hech narsani oʻzi bajarmaydi. U faqat soʻrov yozadi: «mana bu moddani olib ber». Bajarish yoki bajarmaslikni bizning kodimiz hal qiladi.**
    *The most important point is this: the model never executes anything itself. It only writes a request: "fetch this article". Our code decides whether to carry it out.*
    ▸ the model box writes a slip `fetch_article[182]`; a code box takes it, runs the tool, hands back the text
15. **Shuning uchun xavfsizlik chegarasi aynan shu yerda, soʻrov bilan bajarish orasida boʻladi. Sakkizinchi maʼruzadagi barcha himoya shu chegaraga quriladi.**
    *That is why the security boundary sits exactly here, between the request and the execution. All the defences in lecture eight are built on this boundary.*
16. **Bir daqiqaga toʻxtaymiz. Agentimizga toʻrtinchi vosita, kalkulyator qoʻshmoqchimiz. Uning tavsifini bitta gap bilan yozib koʻramiz. Qaysi soʻzlar modelga uni qachon chaqirishni tushuntiradi?**
    *Let's pause for a minute. We want to give our agent a fourth tool, a calculator. Let's write its description in one sentence. Which words tell the model when to call it?*
    ▸ pause card
17. **Endi model fikr bilan harakatni qanday navbatlashtirishini koʻraylik.**
    *Now let's see how the model takes turns between thinking and acting.*

### 3-boʻlim · Section 3 — ReAct · ReAct
18. **Agentni qurishning ikkita oddiy yoʻli bor, va ikkalasi ham oʻziga xos tarzda buziladi.**
    *There are two obvious ways to build an agent, and each fails in its own way.*
19. **Birinchi yoʻl — faqat fikrlash. Model rejani chiroyli tuzadi, lekin hech narsani tekshirmaydi. Notoʻgʻri boshlangʻich fikr oxirgi javobgacha yetib boradi.**
    *The first way is thinking only. The model makes a fine plan but checks nothing. A wrong premise travels all the way to the final answer.*
    ▸ a chain of thought bubbles, the first one red, the red carried to the end
20. **Ikkinchi yoʻl — faqat harakat. Model rejasiz vositalarni chaqiraveradi. Natija kutilmagan boʻlsa, «rejani oʻzgartirish kerak» degan fikrni yozib qoʻyadigan joyi yoʻq.**
    *The second way is acting only. The model keeps calling tools with no plan. When a result is surprising, it has nowhere to write down that the plan must change.*
21. **Yao va uning hamkasblari 2023-yilda uchinchi usulni — ReActʼni taklif qildilar. Model ketma-ket ravishda quyidagilarni yozib boradi: fikr, harakat va vosita qaytargan kuzatuv natijasi. Har bir qadam jarayonlar ketma-ketligiga (traektoriyaga) qoʻshib boriladi.**
    *Yao and colleagues proposed a third way in 2023: ReAct. The model writes in turns: a thought, an action, and the observation the tool returned. Each step is added to the trajectory.*
    ▸ the loop: Fikr → Harakat → Kuzatuv → back to Fikr; an exit to Javob
22. **Fikr — bu aynan model shunday deb yozishi mumkin boʻlgan oʻrindir: "bu qidiruv hech qanday foydali natija bermadi; soʻrovni aniqlashtiraman".**
    *The thought is exactly the place where the model can write: "that search gave nothing useful; I will narrow the query".*
23. **Har bir navbatda model shu paytgacha yozilgan butun matnni qaytadan oʻqiydi va keyingi fikrni yozadi. Boshqa hech narsa eslab qolinmaydi.**
    *Every turn the model re-reads the whole text written so far and writes the next thought. Nothing else is remembered.*
24. **Yao va uning hamkasblari oʻtkazgan tajribalarda aralash sikl (mixed loop) ham savollarga javob berish, ham interaktiv vazifalarni bajarish boʻyicha oddiy usullarning ikkalasidan ham ustun keldi.**
    *In Yao and colleagues' experiments, the mixed loop beat both simple ways, on question answering and on interactive tasks.*
25. **Keling, toʻxtab, oʻylab koʻraylik: faqat harakatlarga asoslanadigan agent oʻn sakkiz yoshga toʻlmaganlar masalasida qayerda xatoga yoʻl qoʻyishi mumkin?**
    *Let's stop and think: where could an act-only agent go wrong on the under-eighteen question?*
    ▸ pause card
26. **Endi bu siklni haqiqiy agentda ishga tushirib koʻramiz.**
    *Now let's run this loop in a real agent.*

### 4-boʻlim · Section 4 — Haqiqiy traektoriya · A real trajectory
27. **Bizning agentimiz Mehnat kodeksi ustida ishlaydi: ikki ming yigirma ikkinchi yilgi kodeks, besh yuz sakson bir modda, hammasi oʻzbek tilida. Agent boshida birorta moddani ham koʻrmagan. U faqat harakat orqali oʻqiydi.**
    *Our agent works on the Labor Code: the 2022 code, five hundred and eighty-one articles, all in Uzbek. At the start the agent has seen none of them. It reads only by acting.*
28. **Savolimiz: normal ish haftasi eng koʻpi bilan necha soat, va oʻn sakkiz yoshgacha boʻlgan xodimlar uchun u farq qiladimi?**
    *Our question: at most how many hours is a normal working week, and does it differ for employees under eighteen?*
29. **Birinchi qadam. Fikr: menga normal ish haftasi va voyaga yetmaganlar uchun qisqartirilgan vaqt haqidagi moddalar kerak. Harakat: qidiruv, «ish haftasining davomiyligi». Kuzatuv: yuz sakson ikkinchi modda, ish vaqtining normal davomiyligi; roʻyxatda toʻrt yuz oʻn beshinchi modda ham bor.**
    *Step one. Thought: I need the provisions on the normal working week and on reduced hours for minors. Action: search, "length of the working week". Observation: Article one hundred eighty-two, normal working time; Article four hundred fifteen is on the list too.*
    ▸ the trace builds line by line from `traces/q2_under18.json`; the search result list appears, 182 and 415 lit
30. **Ikkinchi qadam. Model bir yuz sakson ikkinchi moddani oladi. Unda shunday yozilgan: ish vaqtining normal davomiyligi haftasiga qirq soatdan oshmasligi kerak.**
    *Step two. The model fetches Article one hundred eighty-two. It says: normal working time may not exceed forty hours a week.*
    ▸ the article's Uzbek text, «haftasiga qirq soatdan ortiq» highlighted
31. **Uchinchi qadam. Fikr: endi oʻn sakkiz yoshgacha boʻlganlar uchun alohida qoida kerak. Model toʻrt yuz oʻn beshinchi moddani oladi: oʻn oltidan oʻn sakkiz yoshgacha haftasiga oʻttiz olti soat, oʻn beshdan oʻn olti yoshgacha esa yigirma toʻrt soat.**
    *Step three. Thought: now I need the specific rule for those under eighteen. The model fetches Article four hundred fifteen: thirty-six hours a week from sixteen to eighteen, and twenty-four hours from fifteen to sixteen.*
32. **Toʻrtinchi qadam, javob: qirq soat, yuz sakson ikkinchi modda; oʻn sakkiz yoshgacha esa oʻttiz olti va yigirma toʻrt soat, toʻrt yuz oʻn beshinchi modda.**
    *Step four, the answer: forty hours, Article one hundred eighty-two; under eighteen, thirty-six and twenty-four hours, Article four hundred fifteen.*
33. **Eʼtibor beraylik: toʻrt yuz oʻn beshinchi moddani olishni hech kim buyurmadi. Model qidiruv natijasini koʻrib, oʻzi qaror qildi. Pipelinedan farqi aynan shu.**
    *Notice: nobody told it to fetch Article four hundred fifteen. The model saw the search result and decided itself. That is exactly the difference from a pipeline.*
34. **Yana bir qiziq narsa bor. Birinchi savolimizda modelning birinchi fikri «ehtimol, yuz sakson ikkinchi modda» edi, hali hech narsa qidirmasdan. Model kodeksni oʻqitilgan paytidan eslaydi. Unda nega baribir qidiradi? Chunki u eslaganini emas, oʻqiganini manba qilib koʻrsatishi kerak.**
    *There is one more interesting thing. On our first question, the model's first thought was "likely Article one hundred eighty-two", before it had searched anything. The model remembers the code from its training. So why does it still search? Because it must cite what it read, not what it remembers.*
    ▸ `traces/q1_week.json`, the first Thought, «likely Article 182» underlined
35. **Toʻxtaymiz va oldindan taxmin qilib koʻramiz: oʻn yetti yoshli xodim besh kunlik ish haftasida kuniga necha soat ishlay oladi? Agent qaysi moddalarni oʻqishi kerak?**
    *Let's stop and guess in advance: how many hours a day may a seventeen-year-old work in a five-day week? Which articles must the agent read?*
    ▸ pause card
36. **Agent toʻgʻri javob berdi. Vositalarsiz-chi? Keyingi boʻlimda shuni tekshiramiz.**
    *The agent answered correctly. And without tools? That is what we check in the next section.*

### 5-boʻlim · Section 5 — Vositasiz javob · An answer without tools
37. **Endi xuddi shu modelga xuddi shu savolni beramiz, lekin vositalarsiz. Sikl yoʻq, qidiruv yoʻq, oddiy chatbot kabi bir marta soʻraymiz.**
    *Now we give the same model the same question, but with no tools. No loop, no search: we ask once, like an ordinary chatbot.*
38. **Javob ishonchli eshitiladi: qirq soat, oʻttiz olti soat, yigirma toʻrt soat. Raqamlar toʻgʻri. Lekin manba sifatida yuz sakson uchinchi modda koʻrsatilgan.**
    *The answer sounds sure: forty hours, thirty-six hours, twenty-four hours. The numbers are right. But it cites Article one hundred eighty-three.*
    ▸ `traces/q2_under18_notools.json`, the citation [Art. 183] boxed
39. **Bir yuz sakson uchinchi moddani ochamiz. Unda faqat kimlarga qisqartirilgan ish vaqti berilishi sanab oʻtilgan. Oʻttiz olti ham, yigirma toʻrt ham u yerda yoʻq. Bu raqamlar toʻrt yuz oʻn beshinchi moddada.**
    *We open Article one hundred eighty-three. It only lists who gets reduced hours. Neither thirty-six nor twenty-four is there. Those numbers are in Article four hundred fifteen.*
40. **Ikkinchi savol yanada qiziq: Oʻzbekistonda eng kam oylik ish haqi necha soʻm? Vositasiz model aniq raqam aytdi, bir million bir yuz ellik besh ming soʻm, va bir yuz ellik uchinchi moddani koʻrsatdi.**
    *The second question is even more interesting: what is the minimum monthly wage in Uzbekistan, in soʻm? Without tools the model named an exact figure, one million one hundred fifty-five thousand soʻm, and cited Article one hundred fifty-three.*
41. **Bir yuz ellik uchinchi modda esa xodimni ishdan chetlashtirish haqida, ish haqiga hech qanday aloqasi yoʻq. Xuddi shu savolni yana bir marta berdik: bu safar bir million ikki yuz yetmish ming soʻm, ikki yuz toʻqqizinchi modda. Bu modda esa dam olish kunlari ishlashni taqiqlaydi.**
    *But Article one hundred fifty-three is about suspending an employee from work; it has nothing to do with wages. We asked the same question once more: this time one million two hundred seventy thousand soʻm, Article two hundred nine. And that article forbids work on days off.*
    ▸ the two answers side by side, each citation opened to its real article title
42. **Kodeksda esa hech qanday summa yoʻq. Ikki yuz qirq beshinchi moddada yozilgan: eng kam ish haqini Prezident belgilaydi. Agentimiz yetti qadamda aynan shu javobga keldi: kodeksda summa yoʻq, uni Prezident belgilaydi.**
    *The code contains no amount at all. Article two hundred forty-five says the minimum wage is set by the President. Our agent reached exactly this answer in seven steps: the code states no amount; the President sets it.*
43. **Demak, ravon va ishonchli javob, hatto manba koʻrsatilgan boʻlsa ham, manbaga tayangan javob degani emas. Agent eslashi emas, oʻqishi kerak.**
    *So a fluent, confident answer, even one with a citation, is not a grounded answer. An agent has to read, not remember.*
44. **Toʻxtab, bir mashq qilamiz: vositasiz javobdagi har bir daʼvo yoniga «kodeksda bor» yoki «kodeksda yoʻq» deb yozamiz. Qaysilarini tekshirib boʻlmadi?**
    *Let's stop for an exercise: next to each claim in the answer without tools, we write "in the code" or "not in the code". Which ones could not be checked?*
    ▸ pause card
45. **Agent oʻqiydi, oʻqish esa bepul emas. Keyingi boʻlimda narxini hisoblaymiz.**
    *An agent reads, and reading is not free. In the next section we work out the cost.*

### 6-boʻlim · Section 6 — Qoralama va narx · The scratchpad and the bill
46. **Agentning qoralamasi alohida joyda saqlanmaydi. Har bir fikr, harakat va kuzatuv bir-biriga ulanadi va keyingi navbatda modelga butunlay qayta yuboriladi. Yaʼni qoralama bu kontekst oynasining oʻzi.**
    *An agent's scratchpad is not stored anywhere special. Every thought, action and observation is joined together and sent to the model again, whole, on the next turn. The scratchpad is the context window itself.*
47. **Hisoblaymiz. Tizim koʻrsatmasi va vositalar tavsifi doimiy qism, aytaylik, bir ming ikki yuz token. Har bir qadam yana besh yuz token qoʻshadi.**
    *Let's count. The system prompt and the tool descriptions are a fixed part, say twelve hundred tokens. Each step adds another five hundred.*
    ▸ a prompt bar: a fixed block (S = 1200), then one 500-token block per step
48. **Birinchi navbatda bir ming ikki yuz token yuboramiz. Ikkinchisida bir ming yetti yuz. Uchinchisida ikki ming ikki yuz. Har bir navbat oldingisidan uzunroq.**
    *The first turn sends twelve hundred tokens. The second, seventeen hundred. The third, twenty-two hundred. Each turn is longer than the one before.*
49. **Uch qadam uchun jami besh ming bir yuz token toʻlaymiz. Oʻn qadam uchun oʻttiz toʻrt ming besh yuz. Yigirma qadam uchun esa bir yuz oʻn toʻqqiz ming.**
    *For three steps we pay for five thousand one hundred tokens in all. For ten steps, thirty-four thousand five hundred. For twenty steps, one hundred and nineteen thousand.*
    ▸ bars for 3 / 10 / 20 steps, split into the fixed part and the re-read part
50. **Qadamlarni oʻndan yigirmaga, yaʼni ikki marta oshirdik. Narx esa ikki emas, uch butun oʻndan toʻrt marta oshdi. Sababi: har bir qadamni undan keyingi hamma qadamlar qayta oʻqiydi, va bu qism qadamlar sonining kvadrati kabi oʻsadi.**
    *We doubled the steps, from ten to twenty. The bill grew not two times but three point four times. The reason: every step is re-read by every step after it, and that part grows like the square of the number of steps.*
    ▸ the formula n·S + a·n(n−1)/2, the second term lit
51. **Agar faqat yangi matn uchun toʻlaganimizda, yigirma qadam bor-yoʻgʻi oʻn bir ming ikki yuz token boʻlardi.**
    *If we paid only for the new text, twenty steps would be just eleven thousand two hundred tokens.*
    ▸ beside each bar, a thin bar for the new text only: 2,700 / 6,200 / 11,200
52. **Toʻxtab hisoblaymiz: besh qadamlik traektoriya uchun jami nechta token toʻlaymiz?**
    *Let's stop and count: how many tokens in all do we pay for in a five-step trajectory?*
    ▸ pause card
53. **Bu narxni kamaytirishning bir yoʻli bor. Keyingi boʻlimda koʻramiz.**
    *There is a way to bring this bill down. We see it in the next section.*

### 7-boʻlim · Section 7 — Kesh · The cache
54. **Model har bir yangi tokenni yozish uchun undan oldingi hamma tokenlar boʻyicha hisob-kitob qiladi. Lekin bu hisob-kitob faqat oldingi matnga bogʻliq. Server uni bir marta bajarib, saqlab qoʻyishi mumkin. Buni kesh deymiz.**
    *To write each new token, the model computes over every token before it. But that computation depends only on the earlier text. A server can do it once and keep it. We call this a cache.*
55. **Agent sikli kesh uchun eng qulay holat: har bir navbat oldingi navbatning matni bilan aynan bir xil boshlanadi. Faqat oxirgi qoʻshilgan tokenlar yangi.**
    *An agent loop is the ideal case for a cache: each turn begins with exactly the previous turn's text. Only the tokens added last are new.*
    ▸ the turn-2 bar slides under the turn-1 bar: the shared prefix turns grey ("keshda")
56. **Bizning modelimizda keshdagi token ellik baravar arzon: millionta oddiy token oʻn besh sent turadi, keshdagisi esa nol butun oʻndan uch sent.**
    *For our model a cached token is fifty times cheaper: a million ordinary tokens cost fifteen cents, cached ones three tenths of a cent.*
57. **Oʻn qadamlik traektoriyada besh ming yetti yuz token yangi, yigirma sakkiz ming sakkiz yuzi esa keshdan olinadi. Natijada bitta yurish narxi besh yarim marta arzonlashadi.**
    *In a ten-step trajectory, five thousand seven hundred tokens are new and twenty-eight thousand eight hundred come from the cache. One run becomes five and a half times cheaper.*
58. **Besh yuz savollik baholashda bu ikki dollar ellik toʻqqiz sent oʻrniga qirq yetti sent degani.**
    *Across a five-hundred-question evaluation, that means forty-seven cents instead of two dollars fifty-nine.*
59. **Lekin kesh bitta shart bilan ishlaydi: matnning boshi oʻzgarmasligi kerak. Tizim koʻrsatmasiga soat yoki sanani qoʻshsak, yoki vositalar tartibini almashtirsak, kesh oʻsha joydan boshlab yoʻqoladi.**
    *But the cache works on one condition: the beginning of the text must not change. If we put the time or date into the system prompt, or swap the order of the tools, the cache is lost from that point on.*
60. **Toʻxtab oʻylaymiz: agentimizning tizim koʻrsatmasi boshiga bugungi sanani qoʻshsak, nima boʻladi?**
    *Let's stop and think: what happens if we put today's date at the start of our agent's system prompt?*
    ▸ pause card
61. **Endi narxdan vositalarning oʻziga qaytamiz: ularni qanday tanlaymiz?**
    *Now from the bill back to the tools themselves: how do we choose them?*

### 8-boʻlim · Section 8 — Harakatlar toʻplamini loyihalash · Designing the action space
62. **Harakatlar toʻplami modelning yagona lugʻati. Uni notoʻgʻri oʻlchamda tanlash ikki tomonga ham zarar.**
    *The action space is the model's only vocabulary. Sizing it wrong hurts in both directions.*
63. **Juda katta boʻlsa: qidiruv, izlash, moddani topish, korpusdan soʻrash, toʻrtta deyarli bir xil vosita. Model qaysi birini nazarda tutganimizni taxmin qilishga majbur boʻladi.**
    *Too large: search, look up, find article, query corpus, four near-identical tools. The model is forced to guess which one we meant.*
64. **Juda dagʻal boʻlsa: bitta qidiruv vositasi bilan model «faqat Mehnat kodeksi ichidan qidir» deya olmaydi. U soʻrovga qoʻshimcha soʻzlar tiqib, umid qiladi.**
    *Too coarse: with a single search tool the model cannot say "search only inside the Labor Code". It stuffs extra words into the query and hopes.*
65. **Qoida shunday: har bir vositani bitta gap bilan tasvirlash mumkin boʻlsin, va hech qachon ikkita vosita bitta ehtiyojga birdek mos kelmasin.**
    *The rule is: every tool should be describable in one sentence, and no two tools should ever both fit the same need.*
66. **Va har bir vositada xato javobi boʻlsin. Bizning agentimizda «bunday modda yoʻq» yoki «nomaʼlum harakat» degan javob dasturni toʻxtatmaydi. U kuzatuv sifatida modelga qaytadi, va model keyingi qadamni tanlaydi.**
    *And every tool needs a failure reply. In our agent, "there is no such article" or "unknown action" does not stop the program. It goes back to the model as an observation, and the model picks the next step.*
    ▸ `fetch_article[1182]` → Observation: there is no article 1182
67. **Toʻxtaymiz: uchta harakatimizdan qaysi biriga yana bitta argument qoʻshish foydali boʻlardi? Masalan, qidiruvga bob raqami?**
    *Let's pause: which of our three actions would gain from one more argument? For example, a chapter number for search?*
    ▸ pause card
68. **Xato javoblari boʻlsa ham, sikl baribir buzilishi mumkin. Qanday qilib, keyingi boʻlimda koʻramiz.**
    *Even with failure replies, the loop can still break. How, we see in the next section.*

### 9-boʻlim · Section 9 — Sikl qanday buziladi · How the loop breaks
69. **Sikl uch xil yoʻl bilan buziladi. Birinchisi cheksiz sikl. Model bir xil harakatni qayta-qayta takrorlaydi, chunki kuzatuv uning fikrida hech narsani oʻzgartirmagan.**
    *The loop breaks in three ways. The first is an endless loop. The model repeats the same action again and again, because the observation changed nothing in its thinking.*
70. **Davosi qadamlar chegarasi. Bizning agentimizda u sakkiz qadam. Eng kam ish haqi haqidagi savol yetti qadam oldi: ikki marta qidiruv, ikki yuz qirq beshinchi modda, yana qidiruv, ikki yuz qirq uchinchi modda, yana bir qidiruv, va javob.**
    *The cure is a step limit. Ours is eight steps. The minimum-wage question took seven: two searches, Article two hundred forty-five, another search, Article two hundred forty-three, one more search, and the answer.*
    ▸ `traces/q3_min_wage.json` as seven step tiles under an 8-step ruler
71. **Chegarani uch qadamga tushirsak-chi? Agent ikki yuz qirq beshinchi moddani oʻqiydi va toʻxtaydi. Hech qanday javob yoʻq. Sikl xavfsiz tugadi, lekin foydalanuvchi hech narsa bilmadi.**
    *What if we lower the limit to three steps? The agent reads Article two hundred forty-five and stops. No answer at all. The loop ended safely, but the user learned nothing.*
    ▸ `traces/q3_min_wage_steps3.json`: three tiles, then a wall
72. **Shuning uchun chegaraga yetganda agent jim qolmasligi, balki halol aytishi kerak: chegara ichida topilmadi, oxirgi oʻqilgan modda ikki yuz qirq beshinchi. Taxmin qilish esa halol emas.**
    *So when it hits the limit, the agent should not go silent but say honestly: not found within the limit; the last article read was two hundred forty-five. A guess is not honest.*
73. **Ikkinchi yoʻl mavjud boʻlmagan vositani chaqirish yoki notoʻgʻri argument berish. Davosi xatoni kuzatuv sifatida qaytarish, keyingi maʼruzada esa notoʻgʻri chaqiruvni umuman imkonsiz qilish.**
    *The second way is calling a tool that does not exist, or giving it a wrong argument. The cure is to hand the error back as an observation, and in the next lecture, to make a wrong call impossible altogether.*
74. **Uchinchi yoʻl xatolarning toʻplanishi. Har bir qadam oldingi hamma qadamlarga tayanadi, shuning uchun bitta yomon kuzatuv keyingi hammasini buzadi. Buning davosi yoʻq, faqat hisob-kitobi bor.**
    *The third way is compounding errors. Every step rests on all the steps before it, so one bad observation spoils everything after it. There is no cure for this, only arithmetic.*
75. **Toʻxtab oʻylaymiz: model bir xil qidiruvni ikkinchi marta yozsa, kodimiz unga qanday kuzatuv qaytarishi kerak?**
    *Let's stop and think: if the model writes the same search a second time, what observation should our code give back?*
    ▸ pause card
76. **Xoʻp, endi hisob-kitobga oʻtamiz.**
    *Now let's turn to the arithmetic.*

### 10-boʻlim · Section 10 — Xatolar toʻplanadi · Errors compound
77. **Nolinchi modulning ikkinchi maʼruzasini eslaylik: bir-biriga bogʻliq boʻlmagan hodisalarning hammasi roʻy berish ehtimoli ularning ehtimolliklari koʻpaytmasiga teng.**
    *Let's recall lecture two of module zero: the probability that independent events all happen is the product of their probabilities.*
78. **Agentning har bir qadami bir xil ehtimollik bilan toʻgʻri boʻlsin deylik. Unda oʻn qadamning hammasi toʻgʻri boʻlish ehtimoli shu ehtimollikni oʻn marta oʻziga koʻpaytirganimizga teng.**
    *Suppose each step of an agent is right with the same probability. Then the chance that all ten steps are right is that probability multiplied by itself ten times.*
    ▸ p · p · … · p = pᵏ, the ten factors drawn as tiles
79. **Har bir qadam yuzdan toʻqson besh holatda toʻgʻri. Bu juda yaxshi koʻrsatkich. Lekin oʻn qadamdan keyin butun traektoriya taxminan nol butun mingdan besh yuz toʻqson toʻqqiz ehtimollik bilan toʻgʻri, yaʼni oʻn martadan taxminan olti marta.**
    *Each step is right ninety-five times in a hundred. That is excellent. But after ten steps the whole trajectory is right with probability about zero point five nine nine, roughly six times in ten.*
    ▸ the curve pᵏ for p = 0.95 and p = 0.90, k from 1 to 20; k = 10 marked
80. **Haqiqatda bundan ham yomonroq, chunki qadamlar bir-biriga bogʻliq: bitta yomon qidiruv keyingi fikrni ham yomonlashtiradi.**
    *In reality it is even worse, because the steps depend on each other: one bad search makes the next thought worse too.*
81. **Bundan muhim xulosa kelib chiqadi: qadamlarni qisqartirish koʻpincha modelni yaxshilashdan foydaliroq. Har bir qadam yuzdan toʻqson holatda toʻgʻri boʻlsa, oʻn qadam nol butun yuzdan oʻttiz besh beradi, besh qadam esa nol butun yuzdan ellik toʻqqiz.**
    *An important lesson follows: shortening the trajectory is often worth more than improving the model. At ninety in a hundred per step, ten steps give zero point three five, and five steps give zero point five nine.*
82. **Uchta richag bor, odatda shu tartibda foyda beradi: kamroq qadam, yaxshiroq qadam, va xatoni sezib qayta urinish.**
    *There are three levers, usually paying off in this order: fewer steps, better steps, and noticing a failure and trying again.*
83. **Toʻxtab hisoblaymiz: har bir qadam yuzdan toʻqson toʻqqiz holatda toʻgʻri boʻlsa, yigirma qadamlik traektoriya qanchalik ishonchli?**
    *Let's stop and count: if each step is right ninety-nine times in a hundred, how reliable is a twenty-step trajectory?*
    ▸ pause card
84. **Sakkizinchi maʼruzada aynan shuning uchun faqat oxirgi javobni emas, butun traektoriyani baholaymiz.**
    *That is exactly why, in lecture eight, we grade the whole trajectory and not only the last answer.*

## Closing
85. **Mana shu bilan birinchi maʼruzani tugatamiz. Agent bu keyingi qadamni model tanlaydigan dastur, orqaga qaytadigan strelka uning yagona yangiligi. Riekt fikr, harakat va kuzatuvni navbatlashtiradi. Qoralama bu kontekst oynasi, shuning uchun uzun traektoriya qimmat. Ishonchlilik esa koʻpaytiriladi.**
    *With this we finish our first lecture. An agent is a program in which the model chooses the next step; the arrow that goes back is its only new idea. ReAct takes turns between thought, action and observation. The scratchpad is the context window, so a long trajectory is expensive. And reliability multiplies.*
86. **Keyingi maʼruzada model vositani qanday chaqirishini aniq koʻramiz: vositalar sxemasi, tuzilgan javoblar, va notoʻgʻri chaqiruvni imkonsiz qiladigan usullar. Koʻrishguncha!**
    *In the next lecture we see exactly how a model calls a tool: tool schemas, structured outputs, and ways to make a wrong call impossible. See you!*
    ▸ closing card "2-maʼruza · Vositalarni chaqirish"
