"""Deterministic, diverse synthetic patient-support message generator.
Produces realistic operational inquiries across PS-1 categories and urgency levels.
"""

import random
from datetime import datetime, timedelta
from typing import Dict, List, Set
from .config import DataGenerationConfig
from .schemas import PatientMessageRecord


class SyntheticDataGenerator:
    """Generates a realistic, diverse, balanced dataset of patient-support inquiries
    according to PS-1 category, urgency, and data contract specifications.
    """

    def __init__(self, config: DataGenerationConfig = DataGenerationConfig()):
        self.config = config
        self.rng = random.Random(self.config.random_seed)
        self.generated_texts: Set[str] = set()

    def _generate_timestamp(self, index: int) -> str:
        """Produces realistic synthetic timestamps across a 60-day operational window."""
        base_time = datetime(2026, 7, 1, 8, 0, 0)
        day_offset = (index * 13) % 60
        hour_offset = (index * 7) % 12 + 8
        minute_offset = (index * 19) % 60
        second_offset = (index * 23) % 60
        dt = base_time + timedelta(days=day_offset, hours=hour_offset, minutes=minute_offset, seconds=second_offset)
        return dt.isoformat() + "Z"

    def _build_appointment_messages(self, count: int, urgency: str) -> List[str]:
        messages = []
        clinics = [
            "cardiology", "dermatology", "orthopedic clinic", "primary care", "pediatrics",
            "physical therapy", "oncology center", "neurology", "ENT department", "ophthalmology",
            "family medicine", "endocrinology", "rheumatology", "pulmonology", "gastroenterology"
        ]
        actions = [
            "reschedule", "move", "cancel", "book", "schedule", "change the date of",
            "push back", "check the time of", "confirm", "inquire about rescheduling"
        ]
        openers = [
            "Hello, I need to", "Good morning, could you please help me", "Hi, I am writing to",
            "Please assist me to", "Urgent request:", "I am requesting to", "Can someone please help me",
            "Kindly advise if I can", "I would like to", "Dear staff, please help me",
            "Message for scheduling:", "Greetings, I must"
        ]
        reasons_routine = [
            "due to a conflict with my work schedule",
            "because I will be out of town on business next week",
            "as my transportation fell through for that day",
            "since I have another appointment scheduled at the same time",
            "because my childcare plans changed unexpectedly",
            "to a later slot when my spouse can drive me",
            "because I am feeling much better and just need a routine checkup later",
            "for my annual wellness checkup visit",
            "to review my yearly blood work results",
            "because I prefer an afternoon time slot if possible",
            "as my work shift was unexpectedly changed to mornings",
            "to coordinate with my upcoming physical therapy schedule"
        ]
        reasons_urgent = [
            "because my scheduled procedure is tomorrow morning and I have developed sudden fever and chills",
            "as my flight was cancelled today and I must be seen before my surgery clearance expires on Friday",
            "immediately because my post-surgical follow-up was cancelled by mistake and stitches need removal",
            "right away as I missed my pre-operative consultation and surgery is in two days",
            "as soon as possible because my doctor told me to come in within 24 hours if pain spikes",
            "urgently because my blood pressure medication ran out and I need immediate clinical reassessment",
            "today if possible because my vision suddenly became blurry in my right eye",
            "for an urgent same-day cancellation so another patient can take this critical morning slot",
            "because I experienced severe swelling following my cast application yesterday",
            "urgently as my dialysis shunt has developed redness and needs immediate evaluation today"
        ]
        days = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "next week", "this coming Friday", "early next month"]

        while len(messages) < count:
            c = self.rng.choice(clinics)
            a = self.rng.choice(actions)
            o = self.rng.choice(openers)
            d = self.rng.choice(days)
            style = self.rng.randint(1, 5)

            if urgency == "Routine":
                r = self.rng.choice(reasons_routine)
                if style == 1:
                    text = f"{o} {a} my upcoming {c} appointment {r}."
                elif style == 2:
                    text = f"Regarding my {c} visit scheduled for {d}: I would like to {a} it {r}. Please let me know available openings."
                elif style == 3:
                    text = f"Can I {a} my {c} checkup {r}? Sometime {d} would work much better for me."
                elif style == 4:
                    text = f"Please {a} my appointment with the {c} specialist {r}. Thank you for your assistance."
                else:
                    text = f"Inquiry for the front desk: need to {a} my {c} visit {r}. Could you offer any slots {d}?"
            else:
                r = self.rng.choice(reasons_urgent)
                if style == 1:
                    text = f"URGENT: {o} {a} my {c} appointment {r}. Please call me back as soon as possible."
                elif style == 2:
                    text = f"Immediate action required for {d}: Need to {a} my scheduled {c} visit {r}."
                elif style == 3:
                    text = f"Hello triage desk, I must {a} my {c} consult today {r}. Please alert the nursing staff immediately."
                elif style == 4:
                    text = f"Emergency schedule request: I cannot make my {c} visit {d} {r}. What should I do right now?"
                else:
                    text = f"Priority scheduling notice: Please {a} my {c} visit immediately {r}. My procedure is pending."

            if text not in self.generated_texts:
                self.generated_texts.add(text)
                messages.append(text)

        return messages

    def _build_billing_messages(self, count: int, urgency: str) -> List[str]:
        messages = []
        services = [
            "lab tests", "recent MRI scan", "urgent care visit", "annual exam", "outpatient biopsy",
            "physical therapy sessions", "ER visit from last month", "telehealth consultation",
            "specialist visit", "echocardiogram", "CT scan of abdomen", "routine blood draw",
            "post-op wound check", "allergy testing panel", "ultrasound examination"
        ]
        insurance = ["Blue Cross", "Aetna", "UnitedHealthcare", "Cigna", "Medicare", "Humana", "Medicaid", "Kaiser", "Tricare"]
        amounts = ["$45.00", "$75.00", "$120.00", "$185.50", "$250.00", "$340.00", "$480.00", "$650.00", "$890.00", "$1,200.00", "$2,450.00"]
        statement_ids = [f"#{self.rng.randint(10000, 99999)}" for _ in range(50)]
        dates = ["last month", "three weeks ago", "in June", "on May 14th", "earlier this month", "during my last clinic visit"]

        while len(messages) < count:
            s = self.rng.choice(services)
            ins = self.rng.choice(insurance)
            amt = self.rng.choice(amounts)
            stmt = self.rng.choice(statement_ids)
            dt = self.rng.choice(dates)
            style = self.rng.randint(1, 5)

            if urgency == "Routine":
                if style == 1:
                    text = f"I received an invoice for {amt} for my {s} {dt}, but I believe my {ins} insurance should have covered this. Could billing review statement {stmt}?"
                elif style == 2:
                    text = f"Hello, can you please email me an itemized statement and payment receipt for {amt} regarding my {s} {dt}? I need it for my FSA submission."
                elif style == 3:
                    text = f"Question regarding billing: I already paid my {amt} copay at the clinic desk for my {s}, but statement {stmt} shows a pending balance. Please update."
                elif style == 4:
                    text = f"Could someone from patient accounts explain the out-of-pocket charges of {amt} on statement {stmt}? My primary carrier is {ins}."
                else:
                    text = f"I would like to set up a monthly payment plan for my outstanding balance of {amt} regarding the {s} {dt}. Please send agreement paperwork."
            else:
                if style == 1:
                    text = f"URGENT BILLING DISPUTE: My account (statement {stmt}) was wrongfully sent to collections today for {amt} despite my {ins} appeal pending. Place an immediate hold!"
                elif style == 2:
                    text = f"Emergency financial notice: My scheduled chemotherapy treatment tomorrow is being blocked by registration due to an unresolved {amt} charge on {stmt}. Please clear immediately."
                elif style == 3:
                    text = f"Critical billing issue: You charged my credit card {amt} twice this morning for my {s}, overdrew my bank account, and I require an immediate reversal today."
                elif style == 4:
                    text = f"Urgent: I received a pre-collection final notice for an unverified bill of {amt} for {s}. I need a supervisor callback today before credit bureaus are notified."
                else:
                    text = f"URGENT: Pharmacy refusing to dispense my medication until a disputed balance of {amt} on statement {stmt} is cleared by your billing office right now."

            if text not in self.generated_texts:
                self.generated_texts.add(text)
                messages.append(text)

        return messages

    def _build_medication_refill_messages(self, count: int, urgency: str) -> List[str]:
        messages = []
        meds = [
            "Lisinopril 10mg", "Metformin 500mg", "Atorvastatin 20mg", "Albuterol inhaler",
            "Levothyroxine 50mcg", "Amlodipine 5mg", "Omeprazole 40mg", "Losartan 50mg",
            "Insulin Glargine 100u/ml", "Sertraline 50mg", "Gabapentin 300mg", "Hydrochlorothiazide 25mg",
            "Pantoprazole 40mg", "Montelukast 10mg", "Duloxetine 30mg", "Metoprolol Succinate 50mg"
        ]
        pharmacies = [
            "CVS on Main Street", "Walgreens Pharmacy on 5th Ave", "Walmart Pharmacy",
            "Rite Aid on Oak Boulevard", "Kroger Pharmacy", "Costco Mail Order",
            "local hospital outpatient pharmacy", "Target CVS pharmacy", "Express Scripts home delivery"
        ]
        supplies = ["30-day supply", "90-day maintenance supply", "standard monthly refill", "auto-refill renewal"]
        days_left = ["about 5 days", "one week's worth", "approximately 10 days", "a few doses"]

        while len(messages) < count:
            m = self.rng.choice(meds)
            p = self.rng.choice(pharmacies)
            sup = self.rng.choice(supplies)
            dl = self.rng.choice(days_left)
            style = self.rng.randint(1, 5)

            if urgency == "Routine":
                if style == 1:
                    text = f"I am requesting a {sup} renewal for my {m}. Please send the electronic prescription to {p}."
                elif style == 2:
                    text = f"Good morning, my prescription for {m} has no refills remaining at {p}. I have {dl} left. Could the doctor authorize another refill?"
                elif style == 3:
                    text = f"Please renew my {m}. I recently switched my preferred pharmacy to {p}, so please update my file accordingly."
                elif style == 4:
                    text = f"Hello nurse, could you check with my doctor if I can get a {sup} for {m}? {p} informed me that authorization expired."
                else:
                    text = f"Requesting routine refill authorization for {m}. My pharmacy {p} said they sent an electronic request yesterday."
            else:
                if style == 1:
                    text = f"URGENT REFILL: I took my last dose of {m} this morning and have ZERO pills left. Please call in an emergency supply to {p} immediately."
                elif style == 2:
                    text = f"CRITICAL: Ran out of my {m} over the weekend. My symptoms are returning and I need an urgent same-day refill authorization sent to {p}."
                elif style == 3:
                    text = f"Emergency refill request: The pharmacist at {p} says my {m} needs immediate physician reauthorization today or I will miss my evening dose."
                elif style == 4:
                    text = f"Urgent assistance needed: My {m} was lost during travel, and I require an emergency 3-day bridge prescription sent to {p} today."
                else:
                    text = f"URGENT: Diabetic patient completely out of {m}. {p} is waiting on authorization to dispense today. Please contact on-call provider immediately."

            if text not in self.generated_texts:
                self.generated_texts.add(text)
                messages.append(text)

        return messages

    def _build_report_request_messages(self, count: int, urgency: str) -> List[str]:
        messages = []
        reports = [
            "lumbar spine MRI scan", "complete metabolic panel blood test", "chest CT angiogram",
            "skin biopsy pathology report", "echocardiogram diagnostic results", "mammogram screening summary",
            "colonoscopy pathology report", "lipid panel lab results", "thyroid ultrasound report",
            "post-op surgical notes", "electrocardiogram (ECG) tracing", "cervical spine X-ray report",
            "HbA1c diabetes lab results", "cardiac stress test summary", "pulmonary function test report"
        ]
        recipients = [
            "my orthopedic surgeon", "my disability insurance case manager", "my new primary care physician",
            "Dr. Johnson's office", "my legal representative", "my personal health folder",
            "the specialist in Boston", "my cardiologist Dr. Chen", "my worker's compensation coordinator"
        ]
        timeframes = ["from last month", "completed two weeks ago", "from my visit on June 12th", "done earlier this week", "from last Friday"]

        while len(messages) < count:
            rep = self.rng.choice(reports)
            rcp = self.rng.choice(recipients)
            tf = self.rng.choice(timeframes)
            style = self.rng.randint(1, 5)

            if urgency == "Routine":
                if style == 1:
                    text = f"Could you please release a copy of my official {rep} {tf}? I would like to download it from my patient portal."
                elif style == 2:
                    text = f"Hello medical records, I am requesting that my {rep} {tf} be forwarded to {rcp} for my routine follow-up consultation."
                elif style == 3:
                    text = f"Can someone please upload the doctor's clinical summary and the {rep} {tf} to my health portal documents section?"
                elif style == 4:
                    text = f"I need a certified copy of my {rep} for my personal medical records binder. Please let me know if I need to sign an authorization release."
                else:
                    text = f"Please send my recent {rep} results to {rcp}. They requested the official radiologist report before our appointment next month."
            else:
                if style == 1:
                    text = f"URGENT RECORDS REQUEST: My appointment with {rcp} is at 2:00 PM today and they cannot proceed without my {rep}. Please fax it immediately!"
                elif style == 2:
                    text = f"Emergency: Surgery scheduled for tomorrow morning will be cancelled unless the surgical team receives my pre-op {rep} by 4:00 PM today."
                elif style == 3:
                    text = f"Time-sensitive report request: Need immediate dispatch of my {rep} {tf} to {rcp}. The oncology review board meets this afternoon."
                elif style == 4:
                    text = f"Urgent: Dr. Miller ordered an immediate comparison between my previous {rep} and current acute symptoms. Please expedite release to the triage desk."
                else:
                    text = f"CRITICAL: Patient being admitted to regional hospital right now. Emergency room needs my {rep} {tf} faxed over immediately."

            if text not in self.generated_texts:
                self.generated_texts.add(text)
                messages.append(text)

        return messages

    def _build_technical_issue_messages(self, count: int, urgency: str) -> List[str]:
        messages = []
        browsers = [
            "Chrome on Windows 11", "Safari on my iPhone", "the hospital mobile app (iOS)",
            "the Android portal app", "Firefox on my MacBook", "Edge browser on my tablet",
            "Chrome mobile browser", "iPad Safari browser"
        ]
        errors = [
            "Error 403 Forbidden", "Session Expired loop", "blank white screen",
            "password authentication failed", "two-factor authentication code not receiving",
            "network connection timeout", "HTTP 500 Internal Server Error", "invalid token error",
            "page redirect loop", "account locked after 3 attempts"
        ]
        actions_blocked = [
            "log into my patient portal account", "view my lab results tab", "sign the electronic consent form",
            "access the messaging center", "pay my copay online", "open my telehealth video visit link",
            "download my immunization record", "submit my pre-registration paperwork"
        ]

        while len(messages) < count:
            b = self.rng.choice(browsers)
            e = self.rng.choice(errors)
            ab = self.rng.choice(actions_blocked)
            style = self.rng.randint(1, 5)

            if urgency == "Routine":
                if style == 1:
                    text = f"I am unable to {ab} using {b}. It keeps showing '{e}'. Could technical support please assist with resetting my account?"
                elif style == 2:
                    text = f"Hello IT support, the mobile portal app crashes every time I try to {ab}. I am on {b}. Please let me know how to fix this."
                elif style == 3:
                    text = f"I forgot the email address associated with my clinic portal login. Can IT help me verify my username so I can {ab}?"
                elif style == 4:
                    text = f"My two-factor verification code is arriving very late to my phone, resulting in '{e}' when trying to {ab}. Can you assist?"
                else:
                    text = f"General technical assistance needed: The website displays '{e}' whenever I attempt to {ab} on {b}."
            else:
                if style == 1:
                    text = f"URGENT TECH SUPPORT: My virtual video doctor consultation starts in 15 minutes and the link throws '{e}'. I cannot {ab}!"
                elif style == 2:
                    text = f"Critical app malfunction: The portal locked me out with '{e}' right before my mandatory pre-op registration deadline today at noon. Unlock immediately!"
                elif style == 3:
                    text = f"Emergency tech alert: Unable to {ab} due to repeated '{e}'. My child needs urgent discharge instructions right now."
                elif style == 4:
                    text = f"Urgent: Cannot {ab} online because portal gives '{e}'. Surgery is first thing tomorrow morning and consents are required."
                else:
                    text = f"URGENT: Telehealth link for psychiatric evaluation scheduled for 1:00 PM failed with '{e}'. Need immediate technician assistance on {b}."

            if text not in self.generated_texts:
                self.generated_texts.add(text)
                messages.append(text)

        return messages

    def _build_urgent_review_messages(self, count: int, urgency: str) -> List[str]:
        messages = []
        procedures = [
            "knee replacement", "abdominal laparoscopic surgery", "cardiac catheterization",
            "gallbladder surgery", "skin lesion excision", "cataract surgery",
            "lumbar fusion", "hernia repair", "shoulder arthroscopy", "appendectomy",
            "thyroidectomy", "tonsillectomy"
        ]
        post_op_symptoms = [
            "the incision site is hot to the touch, swollen, and leaking cloudy yellowish fluid",
            "I developed a sudden spike in fever of 102.5F with shaking chills",
            "the surgical wound began bleeding through three layers of gauze pads",
            "I am experiencing shortness of breath and sudden calf pain when walking",
            "the numbness in my hand has spread to my entire arm since this morning",
            "severe nausea and continuous vomiting prevent me from keeping prescribed antibiotics down",
            "sudden severe dizziness and feeling like I might faint upon standing",
            "the pain medication is completely failing to control acute stabbing surgical pain"
        ]
        time_anchors = [
            "three days post-op", "since early this morning", "following my discharge yesterday",
            "over the past four hours", "since taking my morning medication", "late last night"
        ]
        routine_openers = [
            "Following up on the urgent review ticket regarding my {p}:",
            "Status check regarding yesterday's urgent alert for my {p}:",
            "Update to the urgent triage callback about my {p}:",
            "Administrative follow-up for ticket #{t_id} ({p}):",
            "Checking in following the urgent notification about my {p}:",
            "Closing the loop on the urgent nurse message regarding {p}:",
            "Regarding the urgent triage notification logged for my {p}:",
            "Routine update following earlier urgent escalation for my {p}:",
            "Chart update following the urgent triage inquiry for {p}:",
            "Notification regarding yesterday's urgent intake alert for {p}:"
        ]
        routine_statuses = [
            "the redness and swelling have completely resolved",
            "my temperature returned to normal (98.6F) overnight",
            "the bleeding stopped and the dressing is now clean and dry",
            "pain is now mild (1/10) and fully controlled with regular Tylenol",
            "the allergic skin rash vanished completely after stopping the medication",
            "my blood pressure reading stabilized to 120/78 this morning",
            "the nausea has subsided and I am able to drink fluids normally",
            "the incision site is healing smoothly with zero drainage",
            "the shortness of breath has totally cleared up after resting",
            "the dizziness disappeared completely and vitals are back to baseline"
        ]
        routine_requests = [
            "Please confirm if I still need to attend Friday's in-person checkup.",
            "Just updating my chart for the clinical care team during normal hours.",
            "Please let Dr. Miller know that everything is back to baseline.",
            "No urgent intervention is required anymore, please archive the escalation.",
            "Please file this note in my electronic records for next week's visit.",
            "I am feeling much better and just confirming my next routine appointment.",
            "Please have the clinic coordinator record this in my progress notes.",
            "Thank you for the quick assistance yesterday, everything is now stable."
        ]

        while len(messages) < count:
            p = self.rng.choice(procedures)
            sym = self.rng.choice(post_op_symptoms)
            ta = self.rng.choice(time_anchors)
            style = self.rng.randint(1, 5)

            if urgency == "Urgent":
                if style == 1:
                    text = f"URGENT REVIEW NEEDED: Had my {p} {ta}, and {sym}. Please have a triage nurse contact me immediately."
                elif style == 2:
                    text = f"Emergency clinical callback requested: Following my {p} {ta}, {sym}. Need immediate provider evaluation."
                elif style == 3:
                    text = f"Urgent post-surgical alert for {p}: {sym} {ta}. Please alert the on-call surgical team right away."
                elif style == 4:
                    text = f"URGENT TRIAGE: Experiencing acute complications after {p} {ta} — {sym}. Please advise immediately."
                else:
                    text = f"Priority medical inquiry: Post-operative patient for {p} reporting {sym} {ta}. Requires rapid clinical triage."
            else:
                ro = self.rng.choice(routine_openers)
                rs = self.rng.choice(routine_statuses)
                rr = self.rng.choice(routine_requests)
                tid = self.rng.randint(1000, 9999)
                text = f"{ro.format(p=p, t_id=tid)} {rs}. {rr}"

            if text not in self.generated_texts:
                self.generated_texts.add(text)
                messages.append(text)

        return messages

    def generate_dataset(self) -> List[Dict[str, any]]:
        """Generates the full canonical dataset matching target distributions."""
        all_records = []
        global_idx = 1

        for category, urgency_targets in self.config.category_urgency_targets.items():
            dept = self.config.category_to_department[category]
            
            for urgency, target_count in urgency_targets.items():
                if category == "Appointment":
                    texts = self._build_appointment_messages(target_count, urgency)
                elif category == "Billing":
                    texts = self._build_billing_messages(target_count, urgency)
                elif category == "Medication Refill":
                    texts = self._build_medication_refill_messages(target_count, urgency)
                elif category == "Report Request":
                    texts = self._build_report_request_messages(target_count, urgency)
                elif category == "Technical Issue":
                    texts = self._build_technical_issue_messages(target_count, urgency)
                elif category == "Urgent Review":
                    texts = self._build_urgent_review_messages(target_count, urgency)
                else:
                    raise ValueError(f"Unknown category: {category}")

                for text in texts:
                    msg_id = f"MSG-{global_idx:06d}"
                    timestamp = self._generate_timestamp(global_idx)
                    
                    record = PatientMessageRecord(
                        message_id=msg_id,
                        message_text=text,
                        category=category,
                        urgency=urgency,
                        department=dept,
                        timestamp=timestamp,
                        generation_source=f"synthetic_generator_{self.config.generator_version}",
                        dataset_version=self.config.dataset_version,
                    )
                    all_records.append(record.model_dump())
                    global_idx += 1

        # Shuffle deterministically to prevent category-sorted bias
        self.rng.shuffle(all_records)
        return all_records
