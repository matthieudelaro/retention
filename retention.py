import datetime
from collections import OrderedDict
from pprint import pprint as pp
from tqdm import tqdm
from genVizualisationImage import vizualiseState


runIndex = datetime.datetime.now()


def descriptionToPolicy(amountOfDaily, amountOfWeekly, amountOfMonthly, amountOfYearly):
    return {
        "amountOfDaily": amountOfDaily,
        "amountOfWeekly": amountOfWeekly,
        "amountOfMonthly": amountOfMonthly,
        "amountOfYearly": amountOfYearly,
    }


def checkCurrentState(now, policy, sortedObjectsDesc, oldestObjectTimeBeforeEviction):
    errors = {}
    if not sortedObjectsDesc and not oldestObjectTimeBeforeEviction:
        return errors
    oldestObject = sortedObjectsDesc[-1]
    oldestObjectTime = oldestObject["time"]
    amountToKeep = policy["amountOfDaily"] + policy["amountOfWeekly"] + policy[
        "amountOfMonthly"] + policy["amountOfYearly"] + 24  # hourly

    if len(sortedObjectsDesc) > amountToKeep * 1.20:
        errors['checkIsDeleting'] = 'Currently {} backups, instead of only {}'.format(len(sortedObjectsDesc), amountToKeep)
    oldestOfAllExpectationOldestBound = None
    for windowType, windowDuration, windowAmount in [
        ["daily", datetime.timedelta(days=1), policy["amountOfDaily"]],
        ["weekly", datetime.timedelta(weeks=1), policy["amountOfWeekly"]],
        ["monthly", datetime.timedelta(days=30), policy["amountOfMonthly"]],
        ["yearly", datetime.timedelta(days=365), policy["amountOfYearly"]],
    ]:
        for windowNumber in range(windowAmount):
            expectationYoungestBound = now - windowDuration * (windowNumber + 1)
            expectationOldestBound = now - windowDuration * (windowNumber + 2)

            found = False
            for obj in sortedObjectsDesc:
                if expectationYoungestBound >= obj["time"] >= expectationOldestBound:
                    found = True
                    break
            if not found:
                errorKey = '{}_{}'.format(windowType, windowNumber)
                if oldestObjectTime > expectationYoungestBound and not (expectationYoungestBound >= oldestObjectTimeBeforeEviction >= expectationOldestBound):
                    pass
                else:
                    sentence = \
                        'Nothing between {} and {} (oldest object is {})'.format(expectationYoungestBound, expectationOldestBound, oldestObjectTime)
                    errors[errorKey] = sentence

    # if oldestOfAllExpectationOldestBound is None:
    #     sentence = \
    #         'Checker is not working properly'
    #     errors['checkLastObjectNotWorking'] = sentence
    # if expectedOldestObjectTime:
    #     if oldestOfAllExpectationOldestBound > expectedOldestObjectTime:
    #         sentence = \
    #             'Expected oldest object ({}) has been removed. ' \
    #             'Oldest is {}'.format(expectedOldestObjectTime,
    #                                   oldestObjectTime)
    #         errors['checkLastObject'] = sentence
    return errors


def currentBackupsOfPolicy(now, policy, sortedObjectsDesc):
    windowIndexToObjectIndex = OrderedDict()  # for each window, the oldest obj
    if not sortedObjectsDesc:
        return windowIndexToObjectIndex
    windowExtraAmount = 1
    for windowType, windowDuration,                 windowContractualDuration,     windowAmount in reversed([
        ["daily",   datetime.timedelta(days=1),     datetime.timedelta(days=1),    policy["amountOfDaily"]+windowExtraAmount if policy["amountOfDaily"] else policy["amountOfDaily"],],
        ["weekly",  datetime.timedelta(weeks=1),    datetime.timedelta(days=7),    policy["amountOfWeekly"]+windowExtraAmount if policy["amountOfWeekly"] else policy["amountOfWeekly"],],
        ["monthly", datetime.timedelta(weeks=4),    datetime.timedelta(days=30.5), policy["amountOfMonthly"]+windowExtraAmount if policy["amountOfMonthly"] else policy["amountOfMonthly"],],
        ["yearly",  datetime.timedelta(weeks=4*12), datetime.timedelta(days=365),  policy["amountOfYearly"]+windowExtraAmount if policy["amountOfYearly"] else policy["amountOfYearly"],],
    ]):
        windowTypeOldestBound = now - windowContractualDuration * windowAmount
        windowNumber = 0
        while True:
            windowIndex = "{}#{}".format(windowType, windowNumber)
            totalDuration = (windowNumber) * windowDuration
            windowOldestBound = windowTypeOldestBound + totalDuration

            # look for oldest backup of this window type, beginning from oldest record
            windowObjIndex = -1
            for objIndex, obj in enumerate(reversed(sortedObjectsDesc)):
                objTime = obj["time"]
                if objTime >= windowOldestBound:
                    windowObjIndex = objIndex
                    break
            if windowObjIndex == -1:  # if not object was found for this window, then we are done with this windowType
                break
            else:
                windowObjIndex = len(sortedObjectsDesc) - 1 - windowObjIndex
                windowIndexToObjectIndex[windowIndex] = windowObjIndex
            if windowNumber == 0:  # if this is the first window of this windowType, then we consider it's backup as a reference for this windowType
                windowTypeOldestObjTime = sortedObjectsDesc[windowObjIndex]["time"]
                windowTypeOldestBound = windowTypeOldestObjTime
            windowNumber += 1
    return windowIndexToObjectIndex


def deleteUselessBackups(windowIndexToObjectIndex, now, policy, sortedObjectsDesc, doDryRun=False):
    requiredObjectIndexes = [objectIndex for _, objectIndex in windowIndexToObjectIndex.items()]

    requiredObjectIndexes = list(set(requiredObjectIndexes))
    dryRun = []
    newSortedObjectDesc = []

    aboutToBeEvicted = 0
    amountToKeep = policy["amountOfDaily"] + policy["amountOfWeekly"] + policy["amountOfMonthly"] + policy["amountOfYearly"]
    for objectIndex, obj in enumerate(sortedObjectsDesc):
        objRequiredByAwindow = objectIndex in requiredObjectIndexes
        objYoungerThanOneDay = (obj["time"] >= now - datetime.timedelta(hours=24))
        keep = objRequiredByAwindow or objYoungerThanOneDay
        dryRun.append((objectIndex, obj, keep, objRequiredByAwindow, objYoungerThanOneDay))
        if keep:
            newSortedObjectDesc.append(obj)

    if False and sortedObjectsDesc and (doDryRun or False):
        if len(sortedObjectsDesc) >= 2:  # 23:
            print("now: {}".format(now))
            for index, step in enumerate(dryRun):
                if index >= 2:  # 15:
                    print('{:<5} {:<15}: {:^5} ({:^5} {:^5} {:.>20} from now. {:.>20} from younger. {}'.format(
                        step[0],
                        str(step[1]["time"]),
                        "✓" if step[2] else "✗✗✗",
                        "✓" if step[3] else "✗✗✗",
                        "✓" if step[4] else "✗✗✗",
                        str(now - step[1]["time"]),
                        str(dryRun[index-1][1]["time"] - (step[1]["time"] if index-1 > 0 else "")),
                        [windowIndex for windowIndex, objectIndex in windowIndexToObjectIndex.items() if step[0] == objectIndex]
                        ))
            # if str(now) == str(dryRun[16][1]["time"]):
            #     print("stop")
            m = 1
        # if len(sortedObjectsDesc) >= 23:

    # if sortedObjectsDesc and len(sortedObjectsDesc) >= 2 and abs(sortedObjectsDesc[0]["time"] - sortedObjectsDesc[-1]["time"]) > datetime.timedelta(days=1):
    #     vizualiseState(runIndex, windowIndexToObjectIndex, now, sortedObjectsDesc)

    # if str(now) == "2019-01-09 01:00:00":
    #     j = 1

    return sortedObjectsDesc if doDryRun else newSortedObjectDesc


def inspect(windowIndexToObjectIndex, now, policy, sortedObjectsDesc):
    # for obj in sortedObjectsDesc:
    #     print(obj["time"])
    print("now".ljust(17), now)
    if len(sortedObjectsDesc) >= 1:
        print("Youngest".ljust(10), str(0).ljust(6), sortedObjectsDesc[0]["time"])
    for previousWindowIndex, windowIndex in zip([None] + list(windowIndexToObjectIndex.keys()), list(windowIndexToObjectIndex.keys())):
        prevObjIndex = None
        objIndex = None
        if previousWindowIndex:
            prevObjIndex = windowIndexToObjectIndex[previousWindowIndex]
        if windowIndex:
            objIndex = windowIndexToObjectIndex[windowIndex]
        # if objIndex:
        # if objIndex and (objIndex != prevObjIndex or previousWindowIndex.split('#')[0] != windowIndex.split('#')[0]):  # don't print windows that duplicate previous ones
        if objIndex and (objIndex != prevObjIndex):  # will omit first weekly, first monthly, first yearly, because copy of last daily, last weekly, ...
            objTime = sortedObjectsDesc[objIndex]["time"]
            timeSinceLastWindow = '?'
            if prevObjIndex:
                prevObjTime = sortedObjectsDesc[prevObjIndex]["time"]
                timeSinceLastWindow = prevObjTime - objTime
            print(windowIndex.ljust(10), str(objIndex).ljust(6),
                  objTime,
                  str(now - objTime).ljust(20),
                  str(timeSinceLastWindow).ljust(20))
        pass

    if len(sortedObjectsDesc) >= 2:
        objTime = sortedObjectsDesc[-1]["time"]
        print("Oldest".ljust(10), str(len(sortedObjectsDesc)-1).ljust(6),
              str(objTime).ljust(20),
              str(now - objTime).ljust(20))

    pass


def test_nominalEvictAfterEachNewBackup():
    yearsToTest = 12
    policyAmountOfYears = 6
    hoursBetweenEvents = 12
    if yearsToTest < 2*policyAmountOfYears:
        raise AssertionError()
    policy = descriptionToPolicy(7, 4, 12, policyAmountOfYears)

    sortedObjectsDesc = []
    startingPoint = datetime.datetime(2019, 1, 1)
    now = startingPoint
    oldestObjectTimeBeforeEviction = None

    total = int((24/hoursBetweenEvents) * 365 * yearsToTest)
    for i in tqdm(range(total)):
        windowIndexToObjectIndex = currentBackupsOfPolicy(now, policy,
                                                          sortedObjectsDesc)
        if sortedObjectsDesc:
            oldestObjectTimeBeforeEviction = sortedObjectsDesc[-1]["time"]
        sortedObjectsDesc = deleteUselessBackups(windowIndexToObjectIndex, now, policy, sortedObjectsDesc)
        errors = checkCurrentState(now, policy, sortedObjectsDesc, oldestObjectTimeBeforeEviction)
        if errors:
            pp('now is {}'.format(now))
            pp(errors)
            print(' ')

        timeIncrement = datetime.timedelta(hours=hoursBetweenEvents)
        if not sortedObjectsDesc:
            newObj = {"time": now}
        else:
            newObj = {"time": sortedObjectsDesc[0]["time"] + timeIncrement}
        sortedObjectsDesc = [newObj] + sortedObjectsDesc
        now = now + timeIncrement
    # vizualiseState(runIndex, windowIndexToObjectIndex, now, sortedObjectsDesc)


def test_nominalEvictOnlyAtTheEnd():
    yearsToTest = 12
    policyAmountOfYears = 6
    hoursBetweenEvents = 12
    if yearsToTest < 2*policyAmountOfYears:
        raise AssertionError()
    policy = descriptionToPolicy(7, 4, 12, policyAmountOfYears)

    sortedObjectsDesc = []
    startingPoint = datetime.datetime(2019, 1, 1)
    now = startingPoint
    oldestObjectTimeBeforeEviction = None

    total = int((24/hoursBetweenEvents) * 365 * yearsToTest)
    for i in tqdm(range(total)):
        if sortedObjectsDesc:
            oldestObjectTimeBeforeEviction = sortedObjectsDesc[-1]["time"]

        timeIncrement = datetime.timedelta(hours=hoursBetweenEvents)
        if not sortedObjectsDesc:
            newObj = {"time": now}
        else:
            newObj = {"time": sortedObjectsDesc[0]["time"] + timeIncrement}
        sortedObjectsDesc = [newObj] + sortedObjectsDesc
        now = now + timeIncrement

    windowIndexToObjectIndex = currentBackupsOfPolicy(now, policy, sortedObjectsDesc)
    sortedObjectsDesc = deleteUselessBackups(windowIndexToObjectIndex, now, policy, sortedObjectsDesc)
    errors = checkCurrentState(now, policy, sortedObjectsDesc, oldestObjectTimeBeforeEviction)
    if errors:
        pp('now is {}'.format(now))
        pp(errors)
        print(' ')
    # vizualiseState(runIndex, windowIndexToObjectIndex, now, sortedObjectsDesc)


def test_missingDayClosestIsOlder():
    policy = descriptionToPolicy(0, 4, 0, 0)
    startingPoint = datetime.datetime(2019, 1, 1)
    now = startingPoint
    sortedObjectsDesc = [
        {"time": datetime.datetime(2018, 12, 31)},
        {"time": datetime.datetime(2018, 12, 24)},


        {"time": datetime.datetime(2018, 12, 23)},  # very close to next one
        # {"time": datetime.datetime(2018, 12, 19)},    # two after
        # {"time": datetime.datetime(2018, 12, 18)},  # one after
        # {"time": datetime.datetime(2018, 12, 17)},  # the missing one
        {"time": datetime.datetime(2018, 12, 16)}, # one before, the one which should be chosen by algo
        # {"time": datetime.datetime(2018, 12, 15)},  # two before


        {"time": datetime.datetime(2018, 12, 10)},
        {"time": datetime.datetime(2018, 12,  3)},
        {"time": datetime.datetime(2018, 11,  26)},
        {"time": datetime.datetime(2018, 11,  19)},
        {"time": datetime.datetime(2018, 11,  12)},
        {"time": datetime.datetime(2018, 11,  1)},
    ]
    expectedOutput = [
        {"time": datetime.datetime(2018, 12, 31)},
        {"time": datetime.datetime(2018, 12, 24)},

        # {"time": datetime.datetime(2018, 12, 23)}, # very close to next one
        # {"time": datetime.datetime(2018, 12, 19)},    # two after
        # {"time": datetime.datetime(2018, 12, 18)},  # one after
        # {"time": datetime.datetime(2018, 12, 17)},  # the missing one
        {"time": datetime.datetime(2018, 12, 16)}, # one before, the one which should be chosen by algo
        # {"time": datetime.datetime(2018, 12, 15)},  # two before

        {"time": datetime.datetime(2018, 12, 10)},
        {"time": datetime.datetime(2018, 12,  3)},
        # later ones where too old
    ]
    oldestObjectTimeBeforeEviction = sortedObjectsDesc[-1]["time"]
    windowIndexToObjectIndex = currentBackupsOfPolicy(now, policy,
                                                      sortedObjectsDesc)
    vizualiseState(runIndex, windowIndexToObjectIndex, now, sortedObjectsDesc, True, False)
    sortedObjectsDesc = deleteUselessBackups(windowIndexToObjectIndex, now,
                                             policy, sortedObjectsDesc)
    if sortedObjectsDesc != expectedOutput:
        print('no expected result')
    errors = checkCurrentState(now, policy, sortedObjectsDesc, oldestObjectTimeBeforeEviction)
    if errors:
        pp(errors)
        print(' ')
    pass


def test_missingDayClosestIsYounger():
    policy = descriptionToPolicy(0, 4, 0, 0)
    startingPoint = datetime.datetime(2019, 1, 1)
    now = startingPoint
    sortedObjectsDesc = [
        {"time": datetime.datetime(2018, 12, 31)},
        {"time": datetime.datetime(2018, 12, 24)},


        {"time": datetime.datetime(2018, 12, 23)},  # very close to next one
        {"time": datetime.datetime(2018, 12, 19)},    # two younger
        {"time": datetime.datetime(2018, 12, 18)},  # one younger, the one which should be chosen by algo
        # {"time": datetime.datetime(2018, 12, 17)},  # the missing one
        # {"time": datetime.datetime(2018, 12, 16)},  # one older
        {"time": datetime.datetime(2018, 12, 15)},  # two older


        {"time": datetime.datetime(2018, 12, 10)},
        {"time": datetime.datetime(2018, 12,  3)},
        {"time": datetime.datetime(2018, 11,  26)},
        {"time": datetime.datetime(2018, 11,  19)},
        {"time": datetime.datetime(2018, 11,  12)},
        {"time": datetime.datetime(2018, 11,  1)},
    ]
    oldestObjectTimeBeforeEviction = sortedObjectsDesc[-1]["time"]
    windowIndexToObjectIndex = currentBackupsOfPolicy(now, policy,
                                                      sortedObjectsDesc)
    sortedObjectsDesc = deleteUselessBackups(windowIndexToObjectIndex, now,
                                             policy, sortedObjectsDesc)
    errors = checkCurrentState(now, policy, sortedObjectsDesc, oldestObjectTimeBeforeEviction)
    if errors:
        pp(errors)
        print(' ')
    if sortedObjectsDesc != [
        {"time": datetime.datetime(2018, 12, 31)},
        {"time": datetime.datetime(2018, 12, 24)},

        # {"time": datetime.datetime(2018, 12, 23)}, # very close to next one
        # {"time": datetime.datetime(2018, 12, 19)},    # two younger
        {"time": datetime.datetime(2018, 12, 18)},  # one younger, the one which should be chosen by algo
        # {"time": datetime.datetime(2018, 12, 17)},  # the missing one
        # {"time": datetime.datetime(2018, 12, 16)},  # one older
        # {"time": datetime.datetime(2018, 12, 15)},  # two older

        {"time": datetime.datetime(2018, 12, 10)},
        {"time": datetime.datetime(2018, 12,  3)},
        # later ones where too old
    ]:
        print('no expected result')
    pass


if __name__ == '__main__':
    test_missingDayClosestIsYounger()
    test_missingDayClosestIsOlder()
    test_nominalEvictOnlyAtTheEnd()
    test_nominalEvictAfterEachNewBackup()
