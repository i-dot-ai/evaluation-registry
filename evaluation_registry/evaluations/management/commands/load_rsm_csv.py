# flake8: noqa
import json

from django.core.management import BaseCommand

from evaluation_registry.evaluations.models import (
    Department,
    Evaluation,
    EventDate,
)


def parse_row(text):
    return json.loads(f"[{text}]")


# New
OAI = ("office-for-artificial-intelligence", "Office for Artificial Intelligence")
DBEIS = (
    "department-for-business-energy-and-industrial-strategy",
    "Department For Business, Energy & Industrial Strategy",
)
ETF = ("evaluation-task-force", "Evaluation Task Force")

# in OBT
DFT = ("department-for-transport", "Department for Transport (DfT)")
CMS = ("department-for-culture-media-and-sport", "Department for Culture, Media and Sport (DCMS)")
DSIT = ("department-for-science-innovation-and-technology", "Department for Science, Innovation and Technology (DSIT)")
DBT = ("department-for-business-and-trade", "Department for Business and Trade (DBT)")
BDUK = ("building-digital-uk", "Building Digital UK (BDUK)")
CO = ("cabinet-office", "Cabinet Office")
HO = ("home-office", "Home Office (Home Office)")
SCOT = ("the-scottish-government", "The Scottish Government (The Scottish Government)")
DFE = ("department-for-education", "Department for Education (DfE)")
DEFRA = ("department-for-environment-food-rural-affairs", "Department for Environment, Food & Rural Affairs (Defra)")

DEPARTMENTS = {
    "Department for transport": [DFT],
    "Department for digital, culture, media & sport": [CMS],
    "Department for culture, media & sport": [CMS],
    "Department for science, innovation & technology": [DSIT],
    "Department for science, innovation and technology; office for artificial intelligence; department for digital, culture, media & sport; department for business, energy & industrial strategy": [
        DSIT,
        CMS,
        OAI,
        DBEIS,
    ],
    "Department for digital, culture media & sport; arts council england": [CMS],
    "Department for digital, culture, media & sport; office for artificial intelligence": [CMS, OAI],
    "Culture, media, and sport": [CMS],
    "Building digital uk | department for digital, culture, media & sport": [CMS],
    "Building digital uk": [BDUK],
    "Cabinet office": [CO],
    "Evaluation task force": [ETF],
    "Home office": [HO],
    "Uk commission for employment and skills": [],
    "Department for education": [DFE],
    "Department for levelling up, housing and communities": [],
    "Closed organisation: ministry of housing, communities & local government": [],
    "Department for levelling up, housing and communities | cabinet office": [CO],
    "Department for work and pensions": [],
    "Foreign, commonwealth & development office": [],
    "Uk commission for employment and skills (ukces)": [],
    "Department for business, energy & industrial strategy": [],
    "Department of energy and climate change": [],
    "Ministry of housing, communities and local government": [],
    "Hm revenue & customs": [],
    "Department for work and pensions.": [],
    "Closed organisation: department for international development": [],
    "Environment agency": [],
    "Uk health security agency": [],
    "Department for environment, food & rural affairs": [DEFRA],
    "Department for business innovation & skills": [],
    "Closed organisation: national college for teaching and leadership": [],
    "Ofsted": [],
    "Other (please state) parliament": [],
    "Ministry of justice": [],
    "Department for education & national college for teaching and leadership": [DFE],
    "Ofqual": [],
    "Hm government": [],
    "Dcms": [],
    "Senior salaries review body": [],
    "Hm prison and probation service": [],
    "Animal and plant health agency": [],
    "Office of manpower economics | home office": [HO],
    "Closed organisation: department for business, innovation & skills": [],
    "Driver & vehicle standards agency": [],
    "Highways england": [],
    "Office for zero emission vehicles": [],
    "Department for communities and local government": [],
    "Closed organisation: public health england": [],
    "Closed organisation: department of energy & climate change": [],
    "Government equalities office": [],
    "Department of energy and climate change (decc) and bis": [],
    "Highways agency": [],
    "Closed organisation: highways england": [],
    "Department of health and social care": [],
    "Scientific advisory group for emergencies": [],
    "Public health england": [],
    "Uk government": [],
    "Oxfordshire safeguarding children board (oscb)": [],
    "Department for international development": [],
    "Competition and markets authority": [],
    "Other (public health england)": [],
    "Other (department for international development)": [],
    "Other (department of health)": [],
    "Government social research profession": [],
    "Government social research": [],
    "Information not easily found within the report": [],
    "Department for transport (dft)": [DFT],
    "Department for work and pensions | department of health and social care": [],
    "Ministry of justice; hm courts & tribunals service": [],
    "Hm courts & tribunals service": [],
    "Closed organisation: highways agency": [],
    "Ministry for housing, communities and local government (mhclg)": [],
    "Ministry for housing, communities and local government": [],
    "Department for levelling up, housing & communities": [],
    "Hm treasury (hmt)": [],
    "Department of agriculture, environment and rural affairs": [DEFRA],
    "Department for environment, food & rural affairs | home office": [DEFRA, HO],
    "Land use policy group": [],
    "Hm revenue & customs | hm treasury": [],
    "Ministry of justice | hm prison and probation service": [],
    "Natural england": [],
    "Department for energy security & net zero": [],
    "The british business bank": [],
    "European parliament´s directorate for budgetary affairs": [],
    "Innovate uk": [],
    "British business bank": [],
    "Uk research and innovation": [],
    "Innovate uk | closed organisation: department for international development | engineering and physical sciences research council | biotechnology and biological sciences research council | department for business, energy & industrial strategy | uk research": [
        DSIT
    ],
    "Department for energy security and net zero": [],
    "Uk space agency": [],
    "Department of work and pensions": [],
    "Department of health policy research": [],
    "Department of health": [],
    "Other (uk health security agency)": [],
    "Other (national institute of health research)": [],
    "National health services; national institute of health and care excellence": [],
    "National health services": [],
    "Nihr": [],
    "Obesity policy research unit": [],
    "National institute for health research policy research programme": [],
    "National institute for health and care research": [],
    "Department of health and social care, department for education and nhs england and improvement": [DFE],
    "National institute for health research": [],
    "Nihr policy research unit in health and social care systems and commissioning": [],
    "National institute of health research": [],
    "National institute for health research (nihr)": [],
    "King's college london": [],
    "The institute for fiscal studies": [],
    "Public health agency, northern ireland": [],
    "Department of health policy research programme": [],
    "Other (please state) department for communities and local government": [],
    "Office for health improvement and disparities": [],
    "Uk trade & investment": [],
    "Department for science, innovation and technology": [DSIT],
    "Nuclear waste services": [],
    "Marine management organisation": [],
    "Driving standards agency (dsa)": [],
    "Regulator of social housing": [],
    "Office for budget responsibility": [],
    "Youth justice board for england and wales": [],
    "Department for business & trade": [],
    "Cabinet office | national leadership centre | leadership college for government": [CO],
    "Qualifications and curriculum authority": [],
    "Aqa": [],
    "Standards and testing agency": [],
    "Ministry of justice and national offender management service": [],
    "Ministry of justice and hm prison and probation service": [],
    "Hm prison & probation service": [],
    "The charity commission": [],
    "Department for business, energy & industrial strategy; and international climate finance (icf)": [],
    "Department for science, innovation and technology; department for digital, culture, media & sport": [DSIT, CMS],
    "Department for digital, culture, media and sport": [CMS],
    "Department for digital, culture, media & sport (dcms); and the ministry of housing, communities and local government (mchlg).": [
        CMS
    ],
    "Social mobility & child poverty commission": [],
    "Hmrc": [],
    "Committee on fuel poverty": [],
    "Department for energy security and net zero and department for business energy and industrial strategy": [],
    "Department for international trade": [],
    "Hm revenue and customs": [],
    "Department of energy & climate change": [],
    "Ministry of defence": [],
    "Department for energy security and net zero and department for business, energy & industrial strategy": [],
    "Cabinet office and crown commercial service": [CO],
    "Nhs": [],
    "Closed organisation: uk commission for employment and skills": [],
    "Senior salaries review body | office of manpower economics | home office": [],
    "Regulatory policy committee": [],
    "Rural development programme for england network": [],
    "Department for business, innovation & skills and higher education funding council for england": [],
    "Office of the secretary of state for wales and welsh government": [],
    "Department for culture, media and sport and department for digital, culture, media & sport": [CMS],
    "Ministry of justice and hm prison and probability": [],
    "Driver and vehicle standards agency": [],
    "Disability unit": [],
    "Low pay commission": [],
    "Commission on race and ethnic disparities": [],
    "Department for environment food & rural affairs": [DEFRA],
    "Closed organisation: foreign & commonwealth office | closed organisation: department for international development | ministry of defence": [],
    "Department for transport and transport for london": [DFT],
    "The maritime and coastguard agency": [],
    "Homes england": [],
    "Uk government's joint air quality unit": [],
    "The scottish government": [SCOT],
    "Scottish government": [SCOT],
    "Scottish government social research": [SCOT],
    "Scottish government crime and justice": [SCOT],
    "Agriculture and rural economy directorate (as part of business, industry and innovation, education, farming and rural)": [],
    "Scotland government": [SCOT],
    "Other (scottish government)": [SCOT],
    "Scottish government - environment and forestry directorate": [SCOT],
    "Scottish government - agriculture and rural economy directorate": [SCOT],
    "Scottish government - chief economist directorate": [SCOT],
    "Scottish government - director-general education and justice": [SCOT],
    "Scottish government - communities and third sector, equality and rights": [SCOT],
    "Scottish government - learning directorate": [SCOT],
    "Scottish government - communities and third sector": [SCOT],
    "Scottish government - health workforce directorate": [SCOT],
    "Scottish government - children and families directorate": [SCOT],
    "Scottish government - children and families, communities and third sector": [SCOT],
    "Scottish government - building, planning and design, communities and third sector": [SCOT],
    "Scottish government - director-general health and social care": [SCOT],
    "Scottish government - population health directorate": [SCOT],
    "Scottish government - housing": [SCOT],
    "Scottish government - children and families, law and order": [SCOT],
    "Scottish government - marine scotland directorate": [SCOT],
    "Scottish government - health and social care": [SCOT],
    "Other - scottish government": [SCOT],
    "Other - the scottish government": [SCOT],
    "Scottish government - marine and fisheries": [SCOT],
    "Scottish government - director-geberak education and justice": [SCOT],
    "Scottish government - cabinet secretary for education and skills": [SCOT],
    "Scottish government - director general communities": [SCOT],
    "Scottish government - cabinet secretary for nhs recovery , health and social care": [SCOT],
    "Scottish government - director-general net zero": [SCOT],
    "Scottish government - energy and climate change directorate; local government and housing directorate": [SCOT],
    "Scottish government - director-general communities": [SCOT],
    "Scottish government - energy and climate change directorate; economic development directorate; environment and forestry directorate; equality, inclusion and human rights directorate": [
        SCOT
    ],
    "Scottish government - economy, education, work and skills": [SCOT],
    "Scottish government - communications and ministerial support directorate": [SCOT],
    "Scottish government - tackling child poverty and social justice directorate": [SCOT],
    "Scottish government - mental health directorate; population health directorate": [SCOT],
    "Scottish government - early learning and childcare directorate; childcare and families directorate": [SCOT],
    "Scottish government - tackling child poverty and social justice directorate; equality, inclusion and human rights directorate": [
        SCOT
    ],
    "Scottish government - social security directorate": [SCOT],
    "The department for environment, food and rural affairs": [DEFRA],
    "Department of agricultural and food economics": [],
    "Department for environment, food and rural affairs": [DEFRA],
    "Ministry of agriculture fisheries and food welsh office, agriculture department": [],
    "Ministry of agriculture, fisheries & food": [],
    "Department of agriculture and rural development (dard)": [],
    "Uk centre for ecology & hydrology (ukceh)": [],
    "Other (please state) partnership for responsive policy analysis and research": [],
    "Other (please state) nutrients": [],
    "Other (please state) bmc public health": [],
    "Office of national statistics": [],
    "Other (please state) karandaaz pakistan": [],
    "Other (please state) international finance corporation": [],
    "Erdf": [],
    "Department for environment, food and rural affairs (defra)": [DEFRA],
    "Intellectual property office": [],
    "Uk department for transport": [DFT],
    "Who collaborating centre for infectious disease modelling mrc centre for global infectious disease analysis": [],
    "This work was supported by centre funding from the uk medical research council under a concordat with the uk department for international development, the nihr health protection research unit in modelling methodology and the abdul latif jameel foundation.": [],
    "Department of business energy and industrial strategy (beis)": [],
    "Office for life sciences": [],
    "Closed organisation: ministry of housing, communities & local government | department for levelling up, housing and communities": [],
    "Department for education (dfe)": [DFE],
    "Minister of state for health": [],
    "Department for business, innovation and skills": [],
    "The trading standards institute": [],
    "Department for business": [],
    ": hm revenue and customers": [],
    "Who collaborating centre for infectious disease modelling mrc centre for global infectious disease analysis jameel institute for disease and emergency analytics": [],
    "Charity commission for england and wales": [],
    "Nhs scotland directorate": [],
    "Population health directorate": [],
    "Children and families, communities and third sector, equality and rights": [],
    "Learning directorate": [],
    "Building, planning and design": [],
    "Children and families, health and social care": [],
    "Health and social care": [],
    "Director-general education and justice": [],
    "Cabinet secretary for education and skills": [],
    "Hm land registry (hmlr)": [],
    "Met office": [],
    "Geospatial commission": [],
    "Other - the ministry of agriculture fisheries and food": [],
    "Other - the department of agriculture and rural development (dard)": [],
    "Other - world bank": [],
    "Esf evaluation": [],
    "Other - the world bank": [],
    "Closed organisation: department for international development (bangladesh)": [],
    "Other - un women": [],
    "Other - unicef": [],
    "Overseas development administration": [],
    "World bank": [],
    "The joint evaluation of general budget support (gbs) was commissioned by a consortium of donor agencies and 7 partner governments* under the auspices of the dac network on development evaluation.": [],
    "Donors in collaboration with partner governments": [],
    "Management group for the joint evaluation of general budget support": [],
    "United nations": [],
    "Cgap council of governors": [],
    "Department for international evaluation": [],
    "Other - government social research": [],
    "Other - uk department for international development": [],
    "Other - migration advisory committee": [],
    "Office for national statistics": [],
    "Uk office of manpower economics (ome)": [],
    "Department for business, innovation and skills (bis)": [],
    "Ministry of justice (moj)": [],
    "Foreign, commonwealth & development office, dfid, mod": [],
    "The insolvency service": [],
    "Valuation office agency": [],
    "Centre for environment fisheries and aquaculture science": [],
    "Centre for data ethics and innovation": [],
    "Department for work and pensions | government social research profession": [],
    "Other (scotland)": [SCOT],
}

MONTHS = {
    "January": 1,
    "February": 2,
    "March": 3,
    "April": 4,
    "May": 5,
    "June": 6,
    "Jul": 7,
    "July": 7,
    "August": 8,
    "September": 9,
    "October": 10,
    "Oct": 10,
    "November": 10,
    "December": 12,
}


def make_event_date(evaluation, kvp, category, key):
    pub_month = MONTHS.get(kvp[f"{key} (Month)"])
    if year := kvp[f"{key} (Year)"]:
        try:
            EventDate.objects.create(
                evaluation=evaluation,
                month=pub_month,
                year=int(year),
                category=category,
            )
        except ValueError:
            pass


class Command(BaseCommand):
    help = "Load RSM data from CSV"

    def add_arguments(self, parser):
        parser.add_argument("file", type=str)

    def handle(self, *args, **options):
        file = options["file"]
        self.stdout.write(self.style.SUCCESS('loading "%s"' % file))

        with open(file) as f:
            header = parse_row(next(f))
            for row in f:
                record = dict(zip(header, parse_row(row)))
                if lead_department := record["Client"]:
                    if department_list := DEPARTMENTS[lead_department]:
                        code, display = department_list[0]
                        lead_department, _ = Department.objects.get_or_create(code=code, display=display)
                        published_evaluation_link = record["gov_uk_link"]
                        if len(published_evaluation_link or "") > 1024:
                            published_evaluation_link = None

                        evaluation = Evaluation.objects.create(
                            title=record["Evaluation title"],
                            lead_department=lead_department,
                            brief_description=record["Evaluation summary"],
                            major_project_number=record["Major projects identifier"],
                            visibility=Evaluation.EvaluationVisibility.PUBLIC,
                            published_evaluation_link=published_evaluation_link,
                        )

                        make_event_date(
                            evaluation,
                            record,
                            EventDate.EventDateCategory.INTERVENTION_START_DATE,
                            "Intervention start date",
                        )
                        make_event_date(
                            evaluation,
                            record,
                            EventDate.EventDateCategory.INTERVENTION_END_DATE,
                            "Intervention end date",
                        )
                        make_event_date(
                            evaluation,
                            record,
                            EventDate.EventDateCategory.PUBLICATION_FINAL_RESULTS,
                            "Publication date",
                        )
                        make_event_date(evaluation, record, EventDate.EventDateCategory.OTHER, "Event start date")
