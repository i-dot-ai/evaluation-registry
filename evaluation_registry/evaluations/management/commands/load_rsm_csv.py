# TODO: update this, pending dicussion with RSM team about data structures

# flake8: noqa
import json
from collections import Counter
from typing import Optional

from django.core.management import BaseCommand

from evaluation_registry.evaluations.models import (
    Department,
    Evaluation,
    EvaluationDepartmentAssociation,
    EvaluationDesignType,
    EvaluationDesignTypeDetail,
    EventDate,
    Report,
)


def parse_row(text):
    return json.loads(f"[{text}]")


DEPARTMENTS = {
    None: [],
    "Driver & vehicle standards agency": ["driver-and-vehicle-standards-agency"],
    "Department for transport": ["department-for-transport"],
    "Department for digital, culture, media & sport": ["department-for-culture-media-and-sport"],
    "Department for culture, media & sport": ["department-for-culture-media-and-sport"],
    "Department for science, innovation & technology": ["department-for-science-innovation-and-technology"],
    "Department for science, innovation and technology; office for artificial intelligence; department for digital, culture, media & sport; department for business, energy & industrial strategy": [
        "office-for-artificial-intelligence",
        "department-for-science-innovation-and-technology",
        "department-for-culture-media-and-sport",
        "department-for-business-energy-and-industrial-strategy",
    ],
    "Department for digital, culture media & sport; arts council england": ["department-for-culture-media-and-sport"],
    "Department for digital, culture, media & sport; office for artificial intelligence": [
        "office-for-artificial-intelligence",
        "department-for-culture-media-and-sport",
    ],
    "Culture, media, and sport": ["department-for-culture-media-and-sport"],
    "Building digital uk | department for digital, culture, media & sport": ["department-for-culture-media-and-sport"],
    "Building digital uk": ["building-digital-uk"],
    "Cabinet office": ["cabinet-office"],
    "Evaluation task force": ["evaluation-task-force"],
    "Home office": ["home-office"],
    "Uk commission for employment and skills": [],
    "Department for education": ["department-for-education"],
    "Department for levelling up, housing and communities": ["department-for-levelling-up-housing-and-communities"],
    "Closed organisation: ministry of housing, communities & local government": [],
    "Department for levelling up, housing and communities | cabinet office": [
        "department-for-levelling-up-housing-and-communities",
        "cabinet-office",
    ],
    "Department for work and pensions": ["department-for-work-pensions"],
    "Foreign, commonwealth & development office": ["foreign-commonwealth-development-office"],
    "Uk commission for employment and skills (ukces)": [],
    "Department for business, energy & industrial strategy": ["department-for-business-energy-and-industrial-strategy"],
    "Department of energy and climate change": [],
    "Ministry of housing, communities and local government": [],
    "Hm revenue & customs": ["hm-revenue-customs"],
    "Department for work and pensions.": ["department-for-work-pensions"],
    "Closed organisation: department for international development": [],
    "Environment agency": ["environment-agency"],
    "Uk health security agency": [],
    "Department for environment, food & rural affairs": ["department-for-environment-food-rural-affairs"],
    "Department for business innovation & skills": [],
    "Closed organisation: national college for teaching and leadership": [],
    "Ofsted": [],
    "Other (please state) parliament": [],
    "Ministry of justice": ["ministry-of-justice"],
    "Department for education & national college for teaching and leadership": ["department-for-education"],
    "Ofqual": [],
    "Hm government": [],
    "Dcms": [],
    "Senior salaries review body": [],
    "Hm prison and probation service": ["hm-prison-and-probation-service"],
    "Animal and plant health agency": [],
    "Office of manpower economics | home office": ["home-office"],
    "Closed organisation: department for business, innovation & skills": [],
    "Highways england": ["highways-england"],
    "Office for zero emission vehicles": [],
    "Department for communities and local government": [],
    "Closed organisation: public health england": [],
    "Closed organisation: department of energy & climate change": [],
    "Government equalities office": [],
    "Department of energy and climate change (decc) and bis": [],
    "Highways agency": ["highways-agency"],
    "Closed organisation: highways england": ["highways-england"],
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
    "Department for transport (dft)": ["department-for-transport"],
    "Department for work and pensions | department of health and social care": [
        "department-for-work-pensions",
        "department-of-health-and-social-care",
    ],
    "Ministry of justice; hm courts & tribunals service": ["ministry-of-justice"],
    "Hm courts & tribunals service": ["hm-courts-and-tribunals-service"],
    "Closed organisation: highways agency": ["highways-agency"],
    "Ministry for housing, communities and local government (mhclg)": [
        "ministry-of-housing-communities-and-local-government"
    ],
    "Ministry for housing, communities and local government": ["ministry-of-housing-communities-and-local-government"],
    "Department for levelling up, housing & communities": ["department-for-levelling-up-housing-and-communities"],
    "Hm treasury (hmt)": [],
    "Department of agriculture, environment and rural affairs": ["department-for-environment-food-rural-affairs"],
    "Department for environment, food & rural affairs | home office": [
        "department-for-environment-food-rural-affairs",
        "home-office",
    ],
    "Land use policy group": [],
    "Hm revenue & customs | hm treasury": ["hm-revenue-customs"],
    "Ministry of justice | hm prison and probation service": ["ministry-of-justice", "hm-prison-and-probation-service"],
    "Natural england": ["natural-england"],
    "Department for energy security & net zero": ["department-for-energy-security-and-net-zero"],
    "The british business bank": [],
    "European parliament´s directorate for budgetary affairs": [],
    "Innovate uk": [],
    "British business bank": [],
    "Uk research and innovation": [],
    "Innovate uk | closed organisation: department for international development | engineering and physical sciences research council | biotechnology and biological sciences research council | department for business, energy & industrial strategy | uk research": [
        "department-for-science-innovation-and-technology",
        "department-for-business-energy-and-industrial-strategy",
    ],
    "Department for energy security and net zero": ["department-for-energy-security-and-net-zero"],
    "Uk space agency": ["uk-space-agency"],
    "Department of work and pensions": ["department-for-work-pensions"],
    "Department of health policy research": ["department-of-health-and-social-care"],
    "Department of health": ["department-of-health-and-social-care"],
    "Other (uk health security agency)": [],
    "Other (national institute of health research)": [],
    "National health services; national institute of health and care excellence": [],
    "National health services": [],
    "Nihr": [],
    "Obesity policy research unit": [],
    "National institute for health research policy research programme": [],
    "National institute for health and care research": [],
    "Department of health and social care, department for education and nhs england and improvement": [
        "department-of-health-and-social-care",
        "department-for-education",
    ],
    "National institute for health research": [],
    "Nihr policy research unit in health and social care systems and commissioning": [],
    "National institute of health research": [],
    "National institute for health research (nihr)": [],
    "King's college london": [],
    "The institute for fiscal studies": [],
    "Public health agency, northern ireland": [],
    "Department of health policy research programme": ["department-of-health-and-social-care"],
    "Other (please state) department for communities and local government": [],
    "Office for health improvement and disparities": [],
    "Uk trade & investment": [],
    "Department for science, innovation and technology": ["department-for-science-innovation-and-technology"],
    "Nuclear waste services": [],
    "Marine management organisation": [],
    "Driving standards agency (dsa)": ["driver-and-vehicle-standards-agency"],
    "Regulator of social housing": [],
    "Office for budget responsibility": [],
    "Youth justice board for england and wales": [],
    "Department for business & trade": [],
    "Cabinet office | national leadership centre | leadership college for government": ["cabinet-office"],
    "Qualifications and curriculum authority": [],
    "Aqa": [],
    "Standards and testing agency": [],
    "Ministry of justice and national offender management service": ["ministry-of-justice"],
    "Ministry of justice and hm prison and probation service": [
        "ministry-of-justice",
        "hm-prison-and-probation-service",
    ],
    "Hm prison & probation service": ["hm-prison-and-probation-service"],
    "The charity commission": [],
    "Department for business, energy & industrial strategy; and international climate finance (icf)": [
        "department-for-business-energy-and-industrial-strategy"
    ],
    "Department for science, innovation and technology; department for digital, culture, media & sport": [
        "department-for-science-innovation-and-technology",
        "department-for-culture-media-and-sport",
    ],
    "Department for digital, culture, media and sport": ["department-for-culture-media-and-sport"],
    "Department for digital, culture, media & sport (dcms); and the ministry of housing, communities and local government (mchlg).": [
        "department-for-culture-media-and-sport",
        "ministry-of-housing-communities-and-local-government",
    ],
    "Social mobility & child poverty commission": [],
    "Hmrc": ["hm-revenue-customs"],
    "Committee on fuel poverty": [],
    "Department for energy security and net zero and department for business energy and industrial strategy": [
        "department-for-energy-security-and-net-zero",
        "department-for-business-energy-and-industrial-strategy",
    ],
    "Department for international trade": ["department-for-international-trade"],
    "Hm revenue and customs": ["hm-revenue-customs"],
    "Department of energy & climate change": [],
    "Ministry of defence": ["ministry-of-defence"],
    "Department for energy security and net zero and department for business, energy & industrial strategy": [
        "department-for-energy-security-and-net-zero",
        "department-for-business-energy-and-industrial-strategy",
    ],
    "Cabinet office and crown commercial service": ["cabinet-office"],
    "Nhs": [],
    "Closed organisation: uk commission for employment and skills": [],
    "Senior salaries review body | office of manpower economics | home office": ["home-office"],
    "Regulatory policy committee": [],
    "Rural development programme for england network": [],
    "Department for business, innovation & skills and higher education funding council for england": [],
    "Office of the secretary of state for wales and welsh government": [],
    "Department for culture, media and sport and department for digital, culture, media & sport": [
        "department-for-culture-media-and-sport"
    ],
    "Ministry of justice and hm prison and probability": ["ministry-of-justice"],
    "Driver and vehicle standards agency": ["driver-and-vehicle-standards-agency"],
    "Disability unit": [],
    "Low pay commission": [],
    "Commission on race and ethnic disparities": ["commission-on-race-and-ethnic-disparities"],
    "Department for environment food & rural affairs": ["department-for-environment-food-rural-affairs"],
    "Closed organisation: foreign & commonwealth office | closed organisation: department for international development | ministry of defence": [
        "foreign-commonwealth-development-office",
        "ministry-of-defence",
    ],
    "Department for transport and transport for london": ["department-for-transport"],
    "The maritime and coastguard agency": ["maritime-and-coastguard-agency"],
    "Homes england": ["homes-england"],
    "Uk government's joint air quality unit": [],
    "The scottish government": ["the-scottish-government"],
    "Scottish government": ["the-scottish-government"],
    "Scottish government social research": ["the-scottish-government"],
    "Scottish government crime and justice": ["the-scottish-government"],
    "Agriculture and rural economy directorate (as part of business, industry and innovation, education, farming and rural)": [],
    "Scotland government": ["the-scottish-government"],
    "Other (scottish government)": ["the-scottish-government"],
    "Scottish government - environment and forestry directorate": ["the-scottish-government"],
    "Scottish government - agriculture and rural economy directorate": ["the-scottish-government"],
    "Scottish government - chief economist directorate": ["the-scottish-government"],
    "Scottish government - director-general education and justice": ["the-scottish-government"],
    "Scottish government - communities and third sector, equality and rights": ["the-scottish-government"],
    "Scottish government - learning directorate": ["the-scottish-government"],
    "Scottish government - communities and third sector": ["the-scottish-government"],
    "Scottish government - health workforce directorate": ["the-scottish-government"],
    "Scottish government - children and families directorate": ["the-scottish-government"],
    "Scottish government - children and families, communities and third sector": ["the-scottish-government"],
    "Scottish government - building, planning and design, communities and third sector": ["the-scottish-government"],
    "Scottish government - director-general health and social care": ["the-scottish-government"],
    "Scottish government - population health directorate": ["the-scottish-government"],
    "Scottish government - housing": ["the-scottish-government"],
    "Scottish government - children and families, law and order": ["the-scottish-government"],
    "Scottish government - marine scotland directorate": ["the-scottish-government"],
    "Scottish government - health and social care": ["the-scottish-government"],
    "Other - scottish government": ["the-scottish-government"],
    "Other - the scottish government": ["the-scottish-government"],
    "Scottish government - marine and fisheries": ["the-scottish-government"],
    "Scottish government - director-geberak education and justice": ["the-scottish-government"],
    "Scottish government - cabinet secretary for education and skills": ["the-scottish-government"],
    "Scottish government - director general communities": ["the-scottish-government"],
    "Scottish government - cabinet secretary for nhs recovery , health and social care": ["the-scottish-government"],
    "Scottish government - director-general net zero": ["the-scottish-government"],
    "Scottish government - energy and climate change directorate; local government and housing directorate": [
        "the-scottish-government"
    ],
    "Scottish government - director-general communities": ["the-scottish-government"],
    "Scottish government - energy and climate change directorate; economic development directorate; environment and forestry directorate; equality, inclusion and human rights directorate": [
        "the-scottish-government"
    ],
    "Scottish government - economy, education, work and skills": ["the-scottish-government"],
    "Scottish government - communications and ministerial support directorate": ["the-scottish-government"],
    "Scottish government - tackling child poverty and social justice directorate": ["the-scottish-government"],
    "Scottish government - mental health directorate; population health directorate": ["the-scottish-government"],
    "Scottish government - early learning and childcare directorate; childcare and families directorate": [
        "the-scottish-government"
    ],
    "Scottish government - tackling child poverty and social justice directorate; equality, inclusion and human rights directorate": [
        "the-scottish-government"
    ],
    "Scottish government - social security directorate": ["the-scottish-government"],
    "The department for environment, food and rural affairs": ["department-for-environment-food-rural-affairs"],
    "Department of agricultural and food economics": [],
    "Department for environment, food and rural affairs": ["department-for-environment-food-rural-affairs"],
    "Ministry of agriculture fisheries and food welsh office, agriculture department": [
        "department-for-environment-food-rural-affairs"
    ],
    "Ministry of agriculture, fisheries & food": ["department-for-environment-food-rural-affairs"],
    "Department of agriculture and rural development (dard)": [],
    "Uk centre for ecology & hydrology (ukceh)": [],
    "Other (please state) partnership for responsive policy analysis and research": [],
    "Other (please state) nutrients": [],
    "Other (please state) bmc public health": [],
    "Office of national statistics": ["office-for-national-statistics"],
    "Other (please state) karandaaz pakistan": [],
    "Other (please state) international finance corporation": [],
    "Erdf": [],
    "Department for environment, food and rural affairs (defra)": ["department-for-environment-food-rural-affairs"],
    "Intellectual property office": [],
    "Uk department for transport": ["department-for-transport"],
    "Who collaborating centre for infectious disease modelling mrc centre for global infectious disease analysis": [],
    "This work was supported by centre funding from the uk medical research council under a concordat with the uk department for international development, the nihr health protection research unit in modelling methodology and the abdul latif jameel foundation.": [],
    "Department of business energy and industrial strategy (beis)": [
        "department-for-business-energy-and-industrial-strategy"
    ],
    "Office for life sciences": [],
    "Closed organisation: ministry of housing, communities & local government | department for levelling up, housing and communities": [
        "department-for-levelling-up-housing-and-communities"
    ],
    "Department for education (dfe)": ["department-for-education"],
    "Minister of state for health": [],
    "Department for business, innovation and skills": [],
    "The trading standards institute": [],
    "Department for business": [],
    ": hm revenue and customers": ["hm-revenue-customs"],
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
    "Hm land registry (hmlr)": ["land-registry"],
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
    "Office for national statistics": ["office-for-national-statistics"],
    "Uk office of manpower economics (ome)": [],
    "Department for business, innovation and skills (bis)": [],
    "Ministry of justice (moj)": ["ministry-of-justice"],
    "Foreign, commonwealth & development office, dfid, mod": ["foreign-commonwealth-development-office"],
    "The insolvency service": [],
    "Valuation office agency": [],
    "Centre for environment fisheries and aquaculture science": [
        "centre-for-environment-fisheries-and-aquaculture-science"
    ],
    "Centre for data ethics and innovation": [],
    "Department for work and pensions | government social research profession": ["department-for-work-pensions"],
    "Other (scotland)": ["the-scottish-government"],
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
            header, *rows = map(parse_row, f)
            records = [dict(zip(header, row)) for row in rows]

        counts = Counter(x["Evaluation ID"] for x in records)
        simple_evaluation_ids = {evaluation_id for evaluation_id, count in counts.items() if count == 1}

        for simple_evaluation_id in simple_evaluation_ids:
            record = next(x for x in records if x["Evaluation ID"] == simple_evaluation_id)
            published_evaluation_link = record["gov_uk_link"]

            if len(published_evaluation_link or "") > 1024:
                published_evaluation_link = None

            if record["Major projects identifier"] == "Y":
                continue

            if record["Evaluation title"] is None:
                self.stdout.write(self.style.WARNING(f"No title found, skipping evaluation"))
                continue

            is_other_type = record["Other evaluation type (please state)"] not in (
                None,
                "Information not easily found within the report",
                "N",
            )
            evaluation = Evaluation.objects.create(
                rsm_evaluation_id=simple_evaluation_id,
                title=record["Evaluation title"],
                brief_description=record["Evaluation summary"],
                # major_project_number=record["Major projects identifier"],
                visibility=Evaluation.Visibility.PUBLIC,
            )

            Report.objects.create(
                title=record["Report title"],
                link=published_evaluation_link,
                rsm_report_id=record["Report ID"],
                evaluation=evaluation,
            )

            for evaluation_type in "Process", "Impact", "Economic":
                if record[evaluation_type] == "Y":
                    EvaluationDesignTypeDetail.objects.create(
                        evaluation=evaluation,
                        design_type=EvaluationDesignType.objects.get(code=evaluation_type.lower()),
                    )
            if is_other_type:
                EvaluationDesignTypeDetail.objects.create(
                    evaluation=evaluation,
                    design_type=EvaluationDesignType.objects.get(code="other"),
                    text=record["Other evaluation type (please state)"],
                )

            make_event_date(
                evaluation,
                record,
                EventDate.Category.INTERVENTION_START_DATE,
                "Intervention start date",
            )
            make_event_date(
                evaluation,
                record,
                EventDate.Category.INTERVENTION_END_DATE,
                "Intervention end date",
            )
            make_event_date(
                evaluation,
                record,
                EventDate.Category.PUBLICATION_FINAL_RESULTS,
                "Publication date",
            )
            make_event_date(evaluation, record, EventDate.Category.OTHER, "Event start date")

            self.stdout.write(self.style.SUCCESS('Successfully created Evaluation "%s"' % record["Evaluation title"]))

            for department in Department.objects.filter(code__in=DEPARTMENTS[record["Client"]]):
                EvaluationDepartmentAssociation.objects.create(
                    evaluation=evaluation,
                    department=department,
                )

                self.stdout.write(self.style.SUCCESS(f'Associated "{evaluation.title}" with "{department.display}"'))
