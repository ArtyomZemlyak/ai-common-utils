"""
Utils for changing dict-like data from outer modules into storage-friendly.
"""


def parse_dict_2_solr(data: dict, additional_name: str = "NLP") -> list:
    solr_like = []
    try:
        for key, doc in data.items():
            inner_dict = {"id": key}
            _, _ = rec_dict_2_solr(inner_dict, additional_name, doc)
            solr_like.append(inner_dict)
    except Exception as e:
        print(f"Can't parse incoming dict: {e}")
    finally:
        return solr_like


def rec_dict_2_solr(inner_dict, name, outer_value):
    new_name = name
    inner_value = outer_value

    if not isinstance(outer_value, dict):
        return (
            name,
            outer_value.replace("\n", "")
            if isinstance(outer_value, str)
            else outer_value,
        )

    else:
        for key, value in outer_value.items():
            if key == "raw_text":
                new_name = key
                inner_value = value.replace("\n", "")
            else:
                new_name, inner_value = rec_dict_2_solr(
                    inner_dict, key + "_" + name, value
                )
            inner_dict[new_name] = inner_value
        return new_name, inner_value


def parse_solr_2_dict():
    pass
