from .models import TransferToMake


def get_min(arr, nr):
    min_ind = 0
    for i in range(1, nr):
        if arr[i] < arr[min_ind]:
            min_ind = i
    return min_ind


def get_max(arr, nr):
    max_ind = 0
    for i in range(1, nr):
        if arr[i] > arr[max_ind]:
            max_ind = i
    return max_ind


def min_of_2(x, y):
    return x if x < y else y


def min_cash_flow_rec(grp_users, balances):
    nr = len(balances)

    max_credit = get_max(balances, nr)
    max_debit = get_min(balances, nr)

    # recur until fully redistributed
    # <= 0.0099 fixes python error for adding floating values
    if balances[max_credit] <= 0.0009 and balances[max_debit] <= 0.0009:
        return 0

    smallest = min_of_2(-balances[max_debit], balances[max_credit])
    balances[max_credit] = round(balances[max_credit] - smallest, 2)
    balances[max_debit] = round(balances[max_debit] + smallest, 2)

    TransferToMake.objects.create(
        sender=grp_users[max_debit],
        receiver=grp_users[max_credit],
        amount=smallest,
        group=grp_users[0].group,
    )
    min_cash_flow_rec(grp_users, balances)
