def flatten(nested_list):
    def generator(nested_list):
        for sublist in nested_list:
            if isinstance(sublist, list):
                for item in sublist:
                    yield item
            else:
                yield sublist

    return list(generator(nested_list))


def extract_exceptions(results_with_exceptions):
    results, exceptions = zip(*results_with_exceptions)
    return (list(flatten(flatten(list(results)))), list(exceptions))
