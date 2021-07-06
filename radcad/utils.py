import itertools


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


def generate_cartesian_product_parameter_sweep(params):
    cartesian_product = list(itertools.product(*params.values()))
    param_sweep = {key: [x[i] for x in cartesian_product] for i, key in enumerate(params.keys())}
    return param_sweep
