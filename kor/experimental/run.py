"""Temporary code to experiment with extraction from the shell.

This file will likely be deleted to be replaced with notebook demos.
"""
import pprint

from kor import elements
from kor.elements import Option
from kor.extraction import extract
from kor.llms import OpenAICompletion


def get_test_form() -> elements.FlatForm:
    """Get a test form."""
    selection = elements.Selection(
        id="do",
        description="select what you want to do",
        options=[
            Option(
                id="eat",
                description="Specify that you want to eat",
                examples=["I'm hungry", "I want to eat"],
            ),
            Option(
                id="drink",
                description="Specify that you want to drink",
                examples=["I'm thirsty", "I want to drink"],
            ),
            Option(
                id="sleep",
                description="Specify that you want to sleep",
                examples=["I'm tired", "I want to go to bed"],
            ),
        ],
    )

    selection2 = elements.Selection(
        id="watch",
        description="select which movie you want to watch",
        options=[
            Option(
                id="bond",
                description="James Bond 007",
                examples=["watch james bond", "spy movie"],
            ),
            Option(
                id="leo",
                description="toddler movie about a dumptruck",
                examples=["dumptruck movie", "a movie for kids"],
            ),
            Option(
                id="alien",
                description="horror movie about aliens in space",
                examples=["something scary", "i want to watch a scary movie"],
            ),
        ],
    )

    selection3 = elements.Selection(
        id="sex",
        description="what's your sex",
        options=[
            Option(
                id="male",
                description="male",
                examples=[],
            ),
            Option(
                id="female",
                description="female",
                examples=[],
            ),
            Option(
                id="other",
                description="other",
                examples=[],
            ),
        ],
    )
    movie_date = elements.Date(
        id="watch-when",
        description="When do you want to watch the movie",
        examples=[
            ("I want to watch the movie on 2022-01-03", "2022-01-03"),
            ("I want to watch a movie after dinner", "after dinner"),
        ],
    )

    dentist_date = elements.Date(
        id="dentist-when",
        description="When will you go to the dentist",
        examples=[
            ("I am going to the dentist on 2022-01-03", "2022-01-03"),
            ("I am going to the dentist after dinner", "after dinner"),
        ],
    )

    nationality_input = elements.TextInput(
        id="nationality",
        description="What is your nationality. Please only use standard nationalities.",
        examples=[
            ("I am an american", "American"),
            ("je suis french", "French"),
        ],
    )

    form = elements.FlatForm(
        id="input-form",
        description="form to specify what to do and what to watch",
        elements=[
            selection,
            selection2,
            selection3,
            movie_date,
            dentist_date,
            nationality_input,
        ],
    )
    return form


def get_test_form_2():
    company_name = elements.TextInput(
        id="company-name",
        description="what is the name of the company you want to find",
        examples=[
            ("Apple inc", "Apple inc"),
            ("largest 10 banks in the world", ""),
            ("microsoft and apple", "microsoft,apple"),
        ],
    )
    selection_block = elements.Selection(
        multiple=True,
        id="do",
        description="select what you want to do",
        options=[
            Option(
                id="eat",
                description="Specify that you want to eat",
                examples=["I'm hungry", "I want to eat"],
            ),
            Option(
                id="drink",
                description="Specify that you want to drink",
                examples=["I'm thirsty", "I want to drink"],
            ),
            Option(
                id="sleep",
                description="Specify that you want to sleep",
                examples=["I'm tired", "I want to go to bed"],
            ),
        ],
    )
    industry_name = elements.TextInput(
        id="industry-name",
        description="what is the name of the company's industry",
        examples=[
            ("companies in the steel manufacturing industry", "steel manufacturing"),
            ("large banks", "banking"),
            ("military companies", "defense"),
            ("chinese companies", ""),
            ("companies that cell cigars", "cigars"),
        ],
    )

    geography_name = elements.TextInput(
        id="geography-name",
        description="where is the company based? Please use a single country name.",
        examples=[
            ("chinese companies", "china"),
            ("companies based in france", "france"),
            ("france, italy", ""),
        ],
    )

    foundation_date = elements.Date(
        id="foundation-date",
        description="Foundation date of the company",
        examples=[("companies founded in 2023", "2023")],
    )

    revenue = elements.Number(
        id="revenue",
        description="What is the revenue of the company?",  # Might want to model the currency
        examples=[
            ("Revenue of $1,000,000", "$1,000,000"),
            ("this company makes no revenue", "0"),
        ],
    )

    attribute_filter = elements.AbstractObjectInput(
        id="attribute-filter",
        description=(
            "Filter by a value of an attribute using a binary expression. Specify the attribute's name, "
            "an operator (>, <, =, !=, >=, <=, in, not in) and a value."
        ),
        examples=[
            (
                "Companies with revenue > 100",
                {
                    "attribute": "revenue",
                    "op": ">",
                    "value": "100",
                },
            ),
            (
                "number of employees between 50 and 1000",
                {"attribute": "employees", "op": "in", "value": ["50", "1000"]},
            ),
            (
                "blue or green color",
                {
                    "attribute": "color",
                    "op": "in",
                    "value": ["blue", "green"],
                },
            ),
            (
                "companies that do not sell in california",
                {
                    "attribute": "geography-sales",
                    "op": "not in",
                    "value": "california",
                },
            ),
        ],
    )

    # employee_range = elements.NumericRange(
    #     id="employees",
    #     description=(
    #         "The number of employees reported potentially as a range. May include"
    #         " either a max, a min or both."
    #     ),
    #     examples=[
    #         ("At least 100 employees", "(100, *)"),
    #         ("Less than twelve employees", "(*, 12)"),
    #         ("Fifty to sixty employees", "(50, 60)"),
    #     ],
    # )

    sales_geography = elements.TextInput(
        id="geography-sales",
        description=(
            "where is the company doing sales? Please use a single country name."
        ),
        examples=[
            ("companies with sales in france", "france"),
            ("companies that sell their products in germany", "germany"),
            ("france, italy", ""),
        ],
    )

    # attr_filter = elements.ObjectInput(
    #     id="attribute-filter",
    #     description="A filter on an attribute. Composed of attribute name, an operator and a value.",
    #     examples=[
    #         (
    #             "more than 100 employees",
    #             {"attribute": "employees", "operator": ">", "value": "100"},
    #         ),
    #         (
    #             "less than five buildings",
    #             {"attribute": "building", "operator": "<", "value": "5"},
    #         ),
    #         # TODO(Eugene): Refactor needed for
    #         # Edge-cases -- unable to handle `in` operator`
    #         # How to support range operator
    #         # ("blue or green car", {"operator": "in", "value": []}),
    #     ],
    # )

    attr_question_block = elements.TextInput(
        id="question",
        description="Asking about the value of a particular attribute",
        examples=[
            ("What is the revenue of tech companies?", "revenue"),
            ("market cap of apple?", "market cap"),
            ("number of employees of largest company", "number of employees"),
        ],
    )

    sort_by_attribute_block = elements.AbstractObjectInput(
        id="sort-block",
        description=(
            "Use to request to sort the results by a particular attribute. "
            "Can specify the direction"
        ),
        examples=[
            (
                "Largest by market-cap tech companies",
                {"direction": "descending", "attribute": "market-cap"},
            ),
            (
                "sort by companies with smallest revenue ",
                {"direction": "ascending", "attribute": "revenue"},
            ),
        ],
    )

    form = elements.FlatForm(
        id="search-for-companies",
        description="Search for companies matching the following criteria.",
        elements=[
            company_name,
            selection_block,
            geography_name,
            foundation_date,
            industry_name,
            revenue,
            sales_geography,
            attribute_filter,
            attr_question_block,
            sort_by_attribute_block,
            # employee_range,
        ],
    )
    return form


def main() -> None:
    form = get_test_form_2()
    llm = OpenAICompletion(verbose=True)

    while True:
        user_str = input("Please enter text to be parsed: ")
        if user_str in {"q", "Q"}:
            break
        parse = extract(user_str, form, llm)
        pprint.pprint(parse, indent=2, sort_dicts=True)


if __name__ == "__main__":
    main()
