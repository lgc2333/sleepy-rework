from pathlib import Path

from sleepy_rework_types.api.http import HTTP_APIS, HttpApiInfo, __file__


def gen_method_anno(name: str, info: HttpApiInfo, is_async: bool = False) -> str:
    params = ["self"]
    if info.body:
        is_op = info.body.default is not Ellipsis
        anno = f"body: {info.body.type_anno}"
        if is_op:
            anno += f" = {info.body.default_type_anno}"
        params.append(anno)
        params.append("/")

    required_kw = []
    optional_kw = []
    for kw_n, param in (*info.path_params.items(), *info.query_params.items()):
        anno = f"{kw_n}: {param.type_anno}"
        is_op = param.default is not Ellipsis
        if is_op:
            anno += f" = {param.default_type_anno}"
            optional_kw.append(anno)
        else:
            required_kw.append(anno)

    if required_kw or optional_kw:
        params.append("*")
        params.extend(required_kw)
        params.extend(optional_kw)

    if info.response and info.response.type_anno is not Ellipsis:
        resp = info.response.type_anno
    else:
        resp = "None"

    if is_async:
        resp = f"t.Coroutine[t.Any, t.Any, {resp}]"

    return f"def {name}({', '.join(params)}) -> {resp}: ..."


def main():
    with (Path(__file__).parent / "types.pyi").open("w", encoding="utf-8") as f:
        f.write("import typing as t\n")
        f.write("import sleepy_rework_types as m\n")

        f.write("class SyncHttpApi:\n")
        for name, info in HTTP_APIS.items():
            f.write("    ")
            f.write(gen_method_anno(name, info))
            f.write("\n")

        f.write("class AsyncHttpApi:\n")
        for name, info in HTTP_APIS.items():
            f.write("    ")
            f.write(gen_method_anno(name, info, is_async=True))
            f.write("\n")


if __name__ == "__main__":
    main()
