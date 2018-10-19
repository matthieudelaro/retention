import datetime
from collections import OrderedDict


def descriptionToPolicy(amountOfDaily, amountOfWeekly, amountOfMonthly, amountOfYearly):
    return {
        "amountOfDaily": amountOfDaily,
        "amountOfWeekly": amountOfWeekly,
        "amountOfMonthly": amountOfMonthly,
        "amountOfYearly": amountOfYearly,
    }


def currentBackupsOfPolicy(now, policy, sortedObjectsDesc):
    windowIndexToObjectIndex = OrderedDict()  # for each window, the oldest obj
    extraAmountHack = 0
    for windowType, windowDuration, windowAmount in [
        ["daily", datetime.timedelta(days=1), policy["amountOfDaily"]+extraAmountHack,],
        ["weekly", datetime.timedelta(weeks=1), policy["amountOfWeekly"]+extraAmountHack,],
        ["monthly", datetime.timedelta(weeks=4), policy["amountOfMonthly"]+extraAmountHack,],
        ["yearly", datetime.timedelta(weeks=4*12), policy["amountOfYearly"],],
    ]:
        for windowNumber in range(1, windowAmount+1):
            totalDuration = (windowNumber) * windowDuration
            windowOldestBound = now - totalDuration
            windowIndex = "{}#{}".format(windowType, windowNumber)
            # for objIndex, (obj, nextObj) in enumerate(zip(sortedObjectsDesc + [None], [None] + sortedObjectsDesc)):
            #     if nextObj and windowOldestBound > nextObj["time"] and obj:
            #         windowIndexToObjectIndex[windowIndex] = objIndex
            #         break
            for objIndex, obj in enumerate(sortedObjectsDesc):
                objTime = obj["time"]
                if objTime >= windowOldestBound:
                    windowIndexToObjectIndex[windowIndex] = objIndex

    return windowIndexToObjectIndex


def deleteUselessBackups(windowIndexToObjectIndex, now, policy, sortedObjectsDesc):
    requiredObjectIndexes = [objectIndex for _, objectIndex in windowIndexToObjectIndex.items()]
    youngerRequiredIndex = requiredObjectIndexes[0] if len(requiredObjectIndexes) > 0 else None
    requiredObjectIndexes = list(set(requiredObjectIndexes))
    dryRun = []
    newSortedObjectDesc = []

    for objectIndex, obj in enumerate(sortedObjectsDesc):
        objRequiredByAwindow = objectIndex in requiredObjectIndexes
        objYoungerThanFirstWindow = (youngerRequiredIndex is None or objectIndex < youngerRequiredIndex)
        keep = objRequiredByAwindow or objYoungerThanFirstWindow
        dryRun.append((objectIndex, obj, keep, objRequiredByAwindow, objYoungerThanFirstWindow))
        if keep:
            newSortedObjectDesc.append(obj)

    if False:
        if len(sortedObjectsDesc) >= 23:
            print("now: {}".format(now))
            for index, step in enumerate(dryRun):
                if index > 15:
                    print('{:<5} {:<15}: {:^5} ({:^5} {:^5}) {:.>20} {}'.format(
                        step[0],
                        str(step[1]["time"]),
                        "✓" if step[2] else "✗✗✗",
                        "✓" if step[3] else "✗✗✗",
                        "✓" if step[4] else "✗✗✗",
                        str(now - step[1]["time"]),
                        [windowIndex for windowIndex, objectIndex in windowIndexToObjectIndex.items() if step[0] == objectIndex]
                        ))
            # if str(now) == str(dryRun[16][1]["time"]):
            #     print("stop")
            pass
        # if len(sortedObjectsDesc) >= 23:
    if str(now) == "2019-01-09 01:00:00":
        j = 1

    return newSortedObjectDesc


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


def main():
    policy = descriptionToPolicy(7, 4, 12, 10)

    sortedObjectsDesc = []
    now = datetime.datetime(2019, 1, 1)

    total = 24 * 365 * 3
    # total = 24 * 3
    # total = 24 * 30
    previousUniqueWindowsAmount = -1
    for i in range(total):
        windowIndexToObjectIndex = currentBackupsOfPolicy(now, policy,
                                                          sortedObjectsDesc)
        currentUniqueWindowsAmount = [key for key, value in windowIndexToObjectIndex.items() if value < max(windowIndexToObjectIndex.values())]
        # if True or i % (24 * 35) == 0:
        if previousUniqueWindowsAmount != currentUniqueWindowsAmount:
            inspect(windowIndexToObjectIndex, now, policy, sortedObjectsDesc)
            print('')

        sortedObjectsDesc = deleteUselessBackups(windowIndexToObjectIndex, now, policy, sortedObjectsDesc)
        # print('')

        timeIncrement = datetime.timedelta(hours=1)
        if not sortedObjectsDesc:
            newObj = {"time": now}
        else:
            newObj = {"time": sortedObjectsDesc[0]["time"] + timeIncrement}
        sortedObjectsDesc = [newObj] + sortedObjectsDesc
        now = now + timeIncrement
        previousUniqueWindowsAmount = currentUniqueWindowsAmount


if __name__ == '__main__':
    main()
