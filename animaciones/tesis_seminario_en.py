"""Public seminar “Artificial intelligence agents in orbit — and the problem of knowing whether they work” (English).

English translation of tesis_seminario.py: same slides, same order, same videos, same figures and caveats.
PhD thesis by Alan Rosas Palacios (IPN): “Gobernanza autónoma de redes programables” (autonomous governance of
programmable networks), instantiated in 6G/NTN. ~27 min, a single voice. Each video slide carries an assertion
title, a subtitle and the script in the speaker notes; the pieces (tesis_sem_1_orbita.py, tesis_sem_2_examen.py,
tesis_sem_3_resultados.py) are NOT rendered here. Check it against the Spanish with verificar_traduccion.py.
Outputs: exports/presentaciones/seminar_ai_agents_in_orbit_{oscuro,claro}.pptx and exports/SEMINAR_AI_AGENTS_IN_ORBIT_EN.md
Usage: python3 tesis_seminario_en.py [--solo-guion]
"""
from tesis_decks import main

CFG = dict(
    idioma="en",
    ritmo=140, prefijo="tesis_sem", archivo="seminar_ai_agents_in_orbit",
    guion="SEMINAR_AI_AGENTS_IN_ORBIT_EN.md",
    kicker="PUBLIC SEMINAR", titulo="Artificial intelligence agents in orbit", tam_titulo=54,
    lema="…and the problem of knowing whether they work",
    autor="Alan Rosas Palacios", instit="PhD program · Instituto Politécnico Nacional (IPN)",
    pie="AI agents in orbit · Alan Rosas Palacios", cierre_titulo="Knowing that the measurement meant something",
    titulo_plano="Public seminar: Artificial intelligence agents in orbit — and the problem of knowing whether they work",
    nota_md=("Audience: the graduate-program community (technical, but not from this specialty). Contract: here we **explain**, we don't defend. "
             "Date to be confirmed. Every figure comes from the verified list in the committee script; don't improvise others live. "
             "Never say “the first in the world”."),
)

DIAPOS = [
    ("portada",
     "Good afternoon. I'm going to start with a story, not a definition. A story that already happened over our heads, "
     "on the International Space Station, the ISS, and it has a twist that isn't about space at all: it's about method. "
     "I'm Alan Rosas Palacios. I'm doing a PhD at the Instituto Politécnico Nacional, IPN, on how to govern, autonomously, "
     "6G networks that include satellites. And my thesis was born from a very simple discomfort: if I put artificial intelligence in charge of decisions inside a network, "
     "how am I going to know whether it works? That question sounds easy, and it isn't. What I'm going to share with you today is why, "
     "and what I'm doing to answer it."),

    ("texto", "Today's idea, in one sentence", "If you can repeat it at the end, the talk worked",
     ["Artificial intelligence agents are already operating in space",
      "The bodies that define 6G are writing, right now, the rules they must follow",
      "The open question isn't whether they work better, but how we'd know they work",
      "And the tests the field uses to decide that are broken"],
     "Let me give you the whole idea up front, so that everything else can hang from it. First: there are already artificial intelligence agents operating in space, "
     "not in a movie, on real hardware. Second: the bodies that define what 6G networks will look like are writing, right now, "
     "the rules those agents will have to follow. Third, and this is what almost nobody asks: not whether they work better, but how we would know whether they work. "
     "And fourth, the uncomfortable part: it turns out that the tests a good part of the field uses to decide that are broken. "
     "We're going to walk through those four claims, in that order, and at the end I'll ask you whether you can repeat them."),

    ("seccion", "A language model at work in orbit", "A story with a twist",
     "Let's start with the story. It's short and it has numbers, but I'll say the numbers to you, not read them off the slide."),

    ("video", "AstreaAconseja", "A tiny language model, working in orbit",
     "ASTREA · International Space Station · September 2025",
     "In September 2025, on the International Space Station, an experiment called ASTREA was switched on. "
     "A language model, the same kind that sits behind conversational assistants, but a tiny one: one point five four billion parameters, "
     "compressed to fit on the onboard hardware. Its job was to supervise the thermal control system of a payload. "
     "And notice a detail that matters: it didn't decide. It advised. It tuned a parameter of an automatic controller, and that controller is the one that decides. "
     "It's a sensible architecture: the part that's fast and rarely wrong stays in the classical controller, and the language model brings judgment, not reflexes. "
     "Hold on to that split between the one who advises and the one who decides, because it comes back later in my own work."),

    ("video", "AstreaRitmoOrbita", "It failed by running at the wrong pace",
     "Every 15 minutes it got worse; at orbital pace, it improved",
     "And now the lovely detail, the one I want you to take home. When the model gave its advice every fifteen minutes, the system got worse: "
     "thermal violations went up by twenty-four percent. When they set it to the orbit's own rhythm, ninety minutes, "
     "one full lap around the Earth, violations dropped by sixty-six percent. "
     "The intelligence didn't fail for being too little. It failed by running at the wrong pace. Thinking slowly about a system that changes fast is worse than not thinking at all. "
     "And the other way around: aligning the decision with the system's natural rhythm was the difference between making it worse and making it much better. "
     "That's the first lesson of this talk, and it's a lesson about design, not about model size.",
     "The episode-duration figure (+245.8% orbit-aligned, −19.1% with a 15-min window) is on the approved list, but its meaning is not "
     "interpreted here; verify it in arXiv:2509.13380 §4.3 before saying it live. That's why this script uses only the thermal violations."),

    ("texto", "How to cite it honestly", "A preprint, not a verdict",
     ["Single-author preprint, with few episodes and no confidence intervals",
      "The paper presents it as the first agentic system on flight-heritage hardware",
      "Not “the first language model in space”: there were others before",
      "The agent advises; the controller decides"],
     "Before going on, a warning about how I cite this, because it's what gives the story its strength. "
     "It's a preprint, by a single author, with few episodes and no confidence intervals. I say it like that, out loud, because I'd rather you "
     "distrusted me for saying it than trusted me for keeping quiet. And the claim is bounded: the paper presents it as the first agentic system "
     "run on flight-heritage hardware. Not as the first language model in space, because there were others before. "
     "Acknowledging the limits of the evidence doesn't take strength away from the story. It gives it strength. And that attitude, telling what we know and also what we don't, "
     "is exactly the one I'm going to ask of the whole field later on.",
     "Never say “the first in the world” without qualification."),

    ("video", "StarlingCuatroNaves", "Not an isolated case: autonomous coordination has already flown",
     "NASA · Starling mission · 2023-2024 · rules, not learning",
     "If anyone thinks this is an isolated case, it isn't. Autonomous coordination among several spacecraft has already flown. "
     "NASA demonstrated it with four CubeSats in the Starling mission, between 2023 and 2024: the first fully distributed autonomous operation "
     "of multiple spacecraft. No central leader, each spacecraft deciding together with the others. "
     "Except that there, the intelligence wasn't learned. It was a classical planner, made of rules and logic, written by people. "
     "And scaling up to sixty spacecraft was tested only in simulation on the ground. "
     "That matters for what comes next: what's coming in now is the learned part, the part nobody writes rule by rule, "
     "and that's exactly the part we're worst at measuring."),

    ("seccion", "Why this was inevitable", "A matter of arithmetic",
     "Now, why I believe this isn't a passing fad but something inevitable. And the reason fits in three numbers."),

    ("video", "AritmeticaDeLaEscala", "Over sixteen thousand satellites; nearly nine in ten maneuver",
     "Active payloads in orbit · as of August 2026",
     "There are sixteen thousand two hundred seventy-nine active satellites in orbit, as of August 2026. "
     "Of those, ten thousand seven hundred forty-two belong to a single constellation, Starlink: two out of every three belong to one company. "
     "And eighty-six point eight percent of active payloads can maneuver: nearly nine in ten move on purpose. "
     "In other words, the system is dynamic by construction, not because something disturbs it every now and then. "
     "Compare that with the tiny circle over there: that's what a human operator can supervise with real attention. Dozens. Not thousands."),

    ("cita", "No one supervises sixteen thousand satellites", "Automation isn't a technology choice: it's arithmetic",
     "A human operator can supervise dozens of satellites. No one supervises sixteen thousand. "
     "Automation isn't a technology choice: it's arithmetic. Let me say it again, slowly, because it's the sentence that justifies everything else: "
     "we don't automate because it's elegant, we automate because otherwise it simply doesn't fit."),

    ("video", "EstandaresEscribenAhora", "6G standards are being written now",
     "IETF, ETSI and 3GPP define what a network agent may do",
     "And this isn't regulatory science fiction: it's happening now, in the standards. The bodies that define how 6G networks will work, "
     "the IETF, ETSI and 3GPP, are writing, right now, the rules for network agents: what an agent may do, what it must never do, "
     "what it has to log. There's a 2026 IETF draft that says it in normative language: a device agent must not carry out actions "
     "that violate the policies, and all of its significant actions must be logged. "
     "The 3GPP has already concluded a study on requirements for network artificial intelligence agents, and it places the freeze of the first 6G release "
     "potentially in early 2029. ETSI went from studying agents to specifying an autonomous agent entity. "
     "The vocabulary all of this is going to be read in is being set now."),

    ("texto", "Normative language, in the original text", "IETF draft on device agents, 2026",
     ["“A DA MUST NOT be allowed to take actions that violate these policies”",
      "“All significant actions taken by a DA MUST be logged”",
      "Three layers of agents, down to an agent in the network element",
      "MUST and MUST NOT are standards language: they don't suggest, they bind"],
     "Let me show you the full quote, because on screen it's more striking than spoken. It's from the IETF draft on device agents. Two sentences. The first: "
     "a device agent must not be allowed to take actions that violate these policies. The second: all significant actions taken by an agent must be logged. "
     "Look at the capitalized words, MUST and MUST NOT. In a standards document they aren't emphasis, they're an obligation: it's the language of a norm. "
     "The draft defines three layers of agents, all the way down to an agent in the network element itself. In other words, there's already a fairly concrete idea of how "
     "these agents should behave, how they should be constrained and how they should be held accountable. Now look at what's missing from that document."),

    ("video", "BuscarSatelite", "I searched that document for the word “satellite”",
     "Zero times",
     "Here's the fact that changed my year. I took that IETF draft, the one on device agents, and searched for the word satellite. "
     "Zero times. I also searched for the acronym for non-terrestrial networks. Zero. "
     "I don't say it as criticism: it's normal for a standard to start with the terrestrial case. I say it because that's exactly where a doctoral student's work fits in. "
     "There's an agent architecture being standardized, and the case of an agent that lives on a satellite isn't part of the conversation yet. "
     "If you ever wonder what someone still in training can contribute to a field this big, the answer is often in those zeros."),

    ("video", "SateliteDeviceAgent", "The gap: a network agent that lives in orbit",
     "Intermittent contact, finite energy, regulatory limits",
     "That zero leaves a concrete gap open, and it's the part of this talk that gets the most questions. An agent in the network element, but in orbit. "
     "Because an agent on the ground has three luxuries that one on a satellite doesn't. Continuous contact: in orbit, the link comes and goes in windows. "
     "Unlimited energy: a satellite has a finite battery, which drains in shadow and recharges in sunlight. "
     "And local regulation: in space, the limits come from international rules that say where and when you're allowed to transmit. "
     "An agent like that has to decide well with less information, less energy and more rules. "
     "I present it as an open gap, not as a result of mine: it's a question I think is worth someone answering."),

    ("video", "NormaSinIA", "And the space autonomy standard doesn't mention AI",
     "ECSS-E-ST-70-11C, revised in October 2025",
     "And there's a second absence that's just as telling. The European standard on spacecraft autonomy, ECSS, revised in October 2025, "
     "mentions the word autonomy eighty-one times. And it mentions artificial intelligence zero times, machine learning zero times "
     "and constellation zero times. Not once. "
     "Think about it: we have artificial intelligence agents flying, and an autonomy scale in force that doesn't know they exist. "
     "If you ask me what happens if the agent gets it wrong up there, that's the honest answer: the regulatory framework for this doesn't exist yet. "
     "And that's why it matters so much to be able to measure well what these agents do."),

    ("seccion", "What if the exam itself is flawed?", "Here the tone changes",
     "Up to here it was a story. Now comes the real problem, and I'm going to start with an analogy that works with any audience."),

    ("video", "TermometroRoto", "Two doctors and a broken thermometer",
     "An analogy about measuring without checking the instrument",
     "Imagine you want to know which of two doctors diagnoses better. You give both of them the same thermometer and send them off to see patients. "
     "One gets it right seventy percent of the time, the other seventy-two. You conclude the second one is better. "
     "Except nobody checked the thermometer. And the thermometer always reads thirty-seven degrees, no matter what's going on with the patient. "
     "With that instrument, the difference between the two doctors means nothing. It's not that the measurement is imprecise: it's that there's nothing to measure. "
     "Notice how treacherous this is: the numbers come out, the bars get drawn, and nobody suspects a thing, because the error isn't in the doctors or in the arithmetic. "
     "It's in the instrument, and the instrument almost never gets checked. The figures in this analogy are just examples."),

    ("texto", "The same example, with numbers", "Example figures to get the idea across",
     ["Doctor A gets 70 out of 100 right; Doctor B, 72 out of 100",
      "The thermometer reads 37° for every patient, sick or not",
      "Both are “right” only when the patient happened to be healthy",
      "The two-point gap is noise: the instrument can't discriminate"],
     "Let me put it in numbers, as if we were at a whiteboard. A hundred patients. Doctor A gets seventy right, B gets seventy-two, and from that you'd say B is better. "
     "But the thermometer reads thirty-seven degrees for everyone, sick or not. So when are both of them right? Only when the patient, by chance, happened to be healthy. "
     "What separates A from B, those two points, is noise: which of the two got a couple more healthy patients. The instrument can't tell sick from healthy, "
     "so it can't tell a good doctor from a bad one. "
     "These are example numbers, not mine. But the structure is exactly that of a testbed that doesn't reward adapting: the difference you see, even if it's reproducible, means nothing."),

    ("video", "PoliticaQueNoMira", "A policy that looks at nothing wins scenarios",
     "NeurIPS 2023 · the standard testbed for cooperating agents",
     "Now the punch, which is real and belongs to others, not to me. In 2023, a group of researchers published at NeurIPS, one of the most important "
     "artificial intelligence conferences, an uncomfortable result about SMAC, the standard testbed that a whole subfield, the one on multiple agents learning to cooperate, "
     "used to compare its algorithms. They tried a policy that looks at nothing. It doesn't observe the state of the world. It just counts time and runs a fixed sequence. "
     "That policy wins scenarios in the benchmark. "
     "Take that in slowly: a blindfolded agent, doing the same thing every time, beats sophisticated algorithms on the exam everybody was using. "
     "The exam, in those scenarios, didn't reward looking.",
     "Third-party result: present it as such. The page numbers in the NeurIPS proceedings are not verified."),

    ("video", "SemillasQueInvierten", "With ten seeds, the result flips",
     "August 2026 · a study in another domain, the same measurement problem",
     "And in August 2026, another group showed something even more uncomfortable about the same kind of comparisons. With five random seeds, one algorithm looks better. "
     "With ten, the result flips. A completely random policy scores within the range of the trained ones. "
     "And none of the comparisons survives statistical correction for multiple comparisons. "
     "A note of honesty: that study is about a soccer simulator, not about satellite networks. I bring it up because the measurement problem is the same. "
     "Translation: for years, a good part of the field was comparing doctors with a broken thermometer.",
     "Yılmaz and Çelikcan, Applied Sciences 16(15):7650. It's Google Research Football, not NTN: say so if asked."),

    ("texto", "Three questions for reading any comparison", "They work for papers, demos and press releases",
     ["Does the environment reward adapting, or is a fixed strategy already optimal?",
      "How many seeds were used, and does the result flip with more?",
      "Was it corrected for making many comparisons at once?"],
     "Since this may sound abstract, here are three practical questions for reading any comparison of algorithms, whether in a paper, a demo or a press release. "
     "One: does the environment reward adapting, or is a fixed strategy already optimal? That's the thermometer question. "
     "Two: how many seeds were used, and does the result hold up if you use more? That's the flip with ten seeds. "
     "Three: was it corrected for making many comparisons at once? If you compare twenty things, one of them wins by chance. "
     "You don't need to be a specialist to ask those three questions, and an evasive answer already tells you plenty. "
     "My thesis is an attempt to turn the first of them into a mandatory measurement."),

    ("cita", "If the environment doesn't reward adapting, comparing algorithms on it means nothing.",
     "And that isn't known until it's measured.",
     "This is the sentence that holds up my whole thesis. If the environment doesn't reward adapting, comparing algorithms on it means nothing. "
     "And here's what makes the sentence more than a complaint: you don't know that until you measure it. "
     "It's not enough to suspect it, or for the simulator to look realistic. You have to measure it, before comparing anything. I'm going to show you how."),

    ("seccion", "What I'm building", "Three pieces, no jargon",
     "Now, my work. There are three pieces. I'll walk through them without jargon, and whenever a technical term shows up, I'll translate it."),

    ("video", "PadaCuatroCajas", "Piece 1: govern the network, not just control it",
     "PADA · Perception, Analysis, Decision, Action",
     "The first piece is an architecture I call PADA: Perception, Analysis, Decision, Action. "
     "The underlying idea is to separate the one who understands from the one who decides, precisely because of the ASTREA lesson: the slow, semantic part can't live inside the fast loop. "
     "Look at the two clocks on the screen: analysis thinks slowly, decision responds quickly, and the boxes talk to each other through programmable interfaces. "
     "Another practical advantage: when something fails, you know which box it failed in. Whether the network didn't see the problem, misunderstood it, decided badly or couldn't carry it out. "
     "And it isn't an aesthetic preference: it's the separation that the reference architecture of open networks already imposes. "
     "Let me be clear that this is work in progress, part of my thesis, not a finished product."),

    ("video", "ModeloArribaRLAbajo", "The slow part can't live inside the fast loop",
     "Language model on top, reinforcement learning below",
     "Someone will ask: why not just use a large language model for everything? Because the industry itself limits where it's useful. "
     "A 2026 IETF draft, signed by the lead author of the intent-based networking standard, points out that a network's raw telemetry "
     "exceeds the processing capacity of these models for the foreseeable future, unless other measures are taken to reduce the data volume "
     "by several orders of magnitude. That coda matters. "
     "The pattern that's taking hold is: language model on top, to translate intents and explain; reinforcement learning below, to decide fast. "
     "And the ASTREA story I opened with is exactly that, measured in flight.",
     "Say the full coda of the quote (“unless other measures are taken…”)."),

    ("video", "DecisionConjunta", "Piece 2: a single joint decision under incomplete information",
     "The formal model, in thirty seconds",
     "The second piece is a formal model, and I'll give it thirty seconds, because this audience doesn't need the formalism: it needs to know it exists. "
     "It treats the problem of several network layers, radio, transport and core, as a single joint decision, where each part sees only a fraction of what's going on "
     "and they all share a common reward. It's the difference between three controllers, each one optimizing its own thing and colliding, "
     "and a team that coordinates. If anyone's interested in the formalism, I'll gladly walk you through it after the talk."),

    ("video", "MargenAdaptativoIdea", "Piece 3: the Adaptive Margin",
     "How much can you gain, at most, by adapting?",
     "The third piece is the one I consider my contribution. I define a quantity I call the Adaptive Margin, and it answers this question: "
     "in this environment, how much can you gain, at most, by adapting to what's happening, compared with the best possible fixed strategy? "
     "Think of it as terrain. If the terrain has relief, choosing your path well matters: the best route that adapts beats the best straight route by a lot. "
     "There the margin is large, and it makes sense to compare algorithms that learn. "
     "If the terrain is flat, every path leads to the same place. The margin is zero, the best fixed strategy is already optimal, and no result on that environment "
     "means anything. Not for, not against. It's the thermometer again, but now with a rule for knowing whether it always reads the same."),

    ("video", "CompuertaAntesDeCorrer", "Committing in writing to throw out the measurement",
     "Threshold set before running; no gate, no report",
     "And here's the commitment. I set a threshold, twenty-five percent, before running the experiments, and I turn it into a gate. "
     "If the environment passes it, algorithms can be compared. If it doesn't pass, algorithm results on it aren't reported. They aren't discussed. They don't exist. "
     "Notice the order, because that's what makes it honest: the threshold gets nailed down first. If I could lower it until my environment passed, the gate would be worthless. "
     "What gives it value is that it ties my hands before I see the results. It's a thesis that starts by measuring its own instrument."),

    ("texto", "Mine is the use, not the idea", "What already existed and what I add",
     ["Checking the environment before training: there's work doing it since 2020",
      "In 2026, a pre-filter for digital twins before training the agent came out",
      "The quantity rests on a theoretical result published in 2008",
      "What's mine: set the threshold before running and turn it into a gate"],
     "I want to be precise about what's mine and what isn't, because it's easy to exaggerate. Checking the environment before training isn't my idea: there's work doing it since 2020, "
     "and in 2026 someone published a method that pre-filters digital twins before training the agent. The quantity I use rests on a theoretical result published in 2008. "
     "What's mine is the use. I set the threshold before running the experiments and turn it into a gate: if the environment doesn't pass, the results aren't reported. "
     "I looked for precedents of that specific combination and didn't find any, but that's my own search, not proof that they don't exist. "
     "I'd rather have a narrow claim that holds up than a broad one that collapses after a single search.",
     "Don't say “nobody validates the environment before the algorithm” (false: Xu and Chen 2021, Furuta 2021, Oller 2020, Tao et al. 2026)."),

    ("cita", "A thesis that starts by measuring its own instrument",
     "And commits in writing to throwing out its results if it fails",
     "A thesis that starts by measuring its own instrument, and that commits in writing to throwing out its own results if the instrument doesn't pass. "
     "It sounds like not wanting to win very much. It's the opposite: it's the only way for a win, when it comes, to be worth anything. And now I'll tell you how it went."),

    ("seccion", "What I found, including what went wrong", "This is the block that earns credibility",
     "I'll tell this block in the first person and without defending myself. It's the one that earns credibility, and that's why I don't cut it."),

    ("video", "RecorridoDelMargen", "My first testbed failed",
     "Adaptive Margin of 1.7% in version 1; 31.8% in version 2, threshold 25%",
     "First: my own testbed failed. The first version of the environment I built had an Adaptive Margin of one point seven percent. "
     "Practically zero. It was a broken thermometer, and it was mine. If I had run the experiments there, I would have gotten pretty plots and worthless conclusions. "
     "The second version reached thirty-one point eight percent, with the threshold at twenty-five. "
     "One more piece of honesty: of that thirty-one point eight, what I actually managed to reach with a real policy was around ten percent. I'll come back to that in a moment. "
     "And later there was a worse episode, which I'll also tell you about: in a pilot, a misconfigured testbed produced spectacular results, three times better than the ceiling of the real environment, which is impossible. "
     "The protocol caught them and voided them. That's the best proof that the framework works. A validation system that never invalidates anything isn't measuring anything.",
     "The 31.8% is the envelope (lower-bound estimator); the achievable decision margin measured in G2b is 9.5%. Report the pair, not the lone number. "
     "The 25% also appears as a design target for the environment: the first validation is partly calibration."),

    ("video", "AlgoritmoVsEstatica", "With a valid instrument, the algorithm won",
     "Between 9.5% and 16.3% better than the best fixed strategy, in all three seeds",
     "Second: once the instrument was valid, the algorithm won. The multi-agent learning method beat the best fixed strategy in all three random seeds "
     "tested, with improvements of between nine point five and sixteen point three percent. And it reached between eighty-four and eighty-seven percent "
     "of the performance of a policy with privileged information, a kind of authorized cheating that serves as a reference ceiling, and that is a lower bound on the optimum, "
     "not the theoretical maximum. "
     "It's a modest result, and it's honest. Modest, because the environment is still small. Honest, because the instrument was certified before running. "
     "I'm not telling you that artificial intelligence won. I'm telling you that now, if it wins, I know what that means. Three seeds, not thirty."),

    ("video", "VarianteSimpleNoEmpeora", "A negative result, publishable",
     "The variant without the nonlinear component is no worse (n = 3)",
     "Third: a negative result. I tested a simpler variant of the algorithm, without its nonlinear component. It's no worse. "
     "Provisional conclusion: in this regime, the extra complexity doesn't earn its place. "
     "And I say it with caution: it's three seeds. It's a diagnosis, not a proof, and it doesn't have the statistical power to claim they're equivalent. "
     "But in a field with a strong publication bias, where nobody reports what doesn't work or what's superfluous, being able to say this out loud is part of the framework's value. "
     "A result that others would have hidden is, here, a product.",
     "Don't call it a “proven negative result”: it's a diagnosis with n = 3."),

    ("seccion", "What comes next, and why it's urgent", "The honest part first",
     "And now, what comes next. I'll start with the honest part, which is my job to tell you."),

    ("video", "SimuladorMasReal", "Next step: does the margin survive realism?",
     "Real orbits, inter-satellite links and measured latencies · proposed",
     "The honest part first: my current environment is small, with two satellites, and the threshold I required of it also appeared as a design target. "
     "That means the first validation is, in part, calibration. "
     "The next step, which I'm proposing but still need to agree on with my advisor, is the real test: taking the framework to a simulator with real orbits, inter-satellite links "
     "and measured latencies, and asking whether the margin survives the increase in realism. "
     "And this is what I like most about having designed the thesis this way: if the margin doesn't survive, that's a result too. We'd know at what level of realism there stops being "
     "anything to learn. That kind of question, framed that way, I didn't find in the literature I reviewed.",
     "The thesis CLAUDE.md (2026-09-17) records that Dr. Barrera approved the consolidated memo, but leaves the point-by-point detail pending. "
     "Confirm which of this was ratified before saying “I still need to agree on”. Say “proposed” until you've confirmed it."),

    ("video", "PrisaDosMilVeintinueve", "The vocabulary is being set now",
     "First 6G release frozen in early 2029; my defense lands on the other side",
     "And why the rush? The 3GPP places the freeze of the first release of the 6G standard potentially in early 2029, "
     "and it's already evaluating which protocols network agents will use to talk to each other. "
     "My PhD runs from February 2026 to February 2030; I'm in the second semester of eight. My defense lands right on the other side of that line. "
     "That has a practical consequence: whatever I contribute has to be readable in the vocabulary that standard is going to set, not in an earlier one. "
     "That's why my position is deliberately narrow. I'm not trying to reinvent the agent architecture, which is already being standardized. "
     "I'm trying to contribute what that work is missing: the satellite case and the validation of the instrument."),

    ("texto", "Takeaways", "Three ideas",
     ["Artificial intelligence is already deciding in space, and the rules are being written now",
      "The field compares algorithms with tests that sometimes measure nothing",
      "Measure the instrument first, and throw out the results if it fails"],
     "If you take three things home, let them be these. One: there's already artificial intelligence making decisions in space, with pace, with rules and with limits, "
     "and the rules are being written now. Two: the field compares algorithms with tests that sometimes measure nothing, "
     "and it doesn't know, because nobody measures it. Three: the answer isn't a better algorithm, but measuring the instrument first and committing in writing to throwing out "
     "the results if it doesn't pass. If you can repeat those three, the talk did its job."),

    ("cita", "I'm not trying to prove that artificial intelligence wins.",
     "I'm trying to make sure that, when it wins or when it loses, we know the measurement meant something.",
     "And with that, I'll close. I'm not trying to prove that artificial intelligence wins. I'm trying to make sure that, when it wins or when it loses, "
     "we know the measurement meant something."),

    ("cierre",
     "Thank you very much. I'm happy to take questions, and I'll tell you up front that I have answers ready for the most common ones: whether satellites already think for themselves, "
     "what happens if the agent gets it wrong, whether this is of any use in Mexico, why not use a language model for everything, and how much I have left."),

    ("respaldo", "Do satellites already think for themselves?", "They decide some things alone; the learned part is just arriving",
     ["Yes, they decide some things alone, and have for a while", "But with rules written by humans, not learned ones",
      "What's arriving now is the learned part", "That's why measuring it matters"],
     "They do decide some things on their own, yes, and have for a long time, but with rules written by humans, not learned ones. What's coming in now is the learned part, "
     "and that's why it matters to know how to measure it."),

    ("respaldo", "What if the agent gets it wrong up there?", "That's exactly the open question",
     ["Current ECSS standard (Oct 2025): “autonomy” 81 times", "Zero mentions of AI, machine learning or constellation",
      "The regulatory framework for this doesn't exist yet"],
     "That's exactly the open question. The space autonomy scales in force, the European ECSS standard revised in October 2025, don't mention "
     "artificial intelligence, machine learning or constellation even once. There are eighty-one occurrences of autonomy and zero of AI. The regulatory framework for this doesn't exist yet."),

    ("respaldo", "Is this of any use in Mexico?", "Satellite connectivity reaches where fiber doesn't",
     ["A realistic route for areas that fiber doesn't reach",
      "Constellation governance rules are being written in international forums now",
      "Having trained people here isn't a luxury"],
     "Satellite connectivity is the realistic route for areas where fiber doesn't reach, and the rules for how those constellations are governed are being written in international "
     "forums right now. Having people trained in this here isn't a luxury."),

    ("respaldo", "Why not a language model for everything?", "Language on top, reinforcement below",
     ["Raw telemetry exceeds these models' capacity for the foreseeable future",
      "…unless the data volume is cut by several orders of magnitude",
      "Language on top to translate and explain; reinforcement below to decide fast"],
     "Because the industry itself limits where it's useful. A 2026 IETF draft points out that a network's telemetry data exceeds the processing capacity of these models "
     "for the foreseeable future, unless the data volume is reduced by several orders of magnitude. The pattern that's taking hold is language model on top and reinforcement learning below. "
     "And ASTREA is exactly that, measured in flight."),

    ("respaldo", "How much do you have left?", "Second semester of eight",
     ["PhD: February 2026 to February 2030", "I'm in the second semester of eight"],
     "The PhD runs from February 2026 to February 2030. I'm in the second semester of eight."),
]


if __name__ == "__main__":
    main(CFG, DIAPOS)
