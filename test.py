import json

def ratio(success_count, attempt_count):
    success_ratio = success_count / (attempt_count or 1)
    return "%d/%d=%d%%"%(success_count, attempt_count, int(success_ratio*100))

def test(func, get_parts):
    with open("training_data/isl.json") as f:
        data = json.load(f)
    failures = []
    failure_count = 0
    success_count = 0
    case_success_count = 0
    case_total_count = len(data)
    for case in data:
        successful = True
        content = case["content"]
        try:
            print(get_parts)
            print(get_parts("abc $def$ hi"))
            parts = get_parts(content)
        except:
            print("failed on parts")
            successful = False
            parts = []
        for expr in parts:
            try:
                func(expr)
                success_count += 1
            except:
                if successful:
                    print("Failed on part ", expr)
                successful = False
                failure_count += 1
                failures.append(expr)
        if successful:
            case_success_count += 1
    total_count = success_count + failure_count
    print("Failed expressions:\n", "\n".join(failures))
    print("Successful parts: %s"%ratio(success_count, total_count))
    print("Successful cases: %s"%ratio(case_success_count, case_total_count))
