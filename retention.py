import datetime
from collections import OrderedDict


runIndex = datetime.datetime.now()


def descriptionToPolicy(amountOfDaily, amountOfWeekly, amountOfMonthly, amountOfYearly):
    return {
        "amountOfDaily": amountOfDaily,
        "amountOfWeekly": amountOfWeekly,
        "amountOfMonthly": amountOfMonthly,
        "amountOfYearly": amountOfYearly,
    }


def currentBackupsOfPolicy(now, policy, sortedObjectsDesc):
    windowIndexToObjectIndex = OrderedDict()  # for each window, the oldest obj
    extraAmountHack = 1
    # now = datetime.datetime.combine((now - datetime.timedelta(hours=24)).date(), datetime.datetime.min.time())
    for windowType, windowDuration, windowAmount in reversed([
        ["daily", datetime.timedelta(days=1), policy["amountOfDaily"]+extraAmountHack,],
        ["weekly", datetime.timedelta(weeks=1), policy["amountOfWeekly"]+extraAmountHack,],
        ["monthly", datetime.timedelta(weeks=4), policy["amountOfMonthly"]+extraAmountHack,],
        ["yearly", datetime.timedelta(weeks=4*12), policy["amountOfYearly"]+extraAmountHack,],
    ]):
        windowTypeOldestBound = now - windowDuration * windowAmount
        # look for oldest backup of this window type
        oldestObjIndex = -1
        for objIndex, obj in enumerate(sortedObjectsDesc):
            objTime = obj["time"]
            # if windowOldestBound > objTime:
            # if objTime.date() >= windowOldestBound.date():
            if objTime >= windowTypeOldestBound:
                oldestObjIndex = objIndex
                # break
        if oldestObjIndex < 0:
            print('QWERTTYsFSDF')
            break  # go to next window type. Should Happens only when there is not any object
        else:
            print('youpi')
        windowTypeOldestObjTime = sortedObjectsDesc[oldestObjIndex]["time"]

        windowIndex = "{}#{}".format(windowType, windowAmount)
        windowIndexToObjectIndex[windowIndex] = oldestObjIndex

        # if windowTypeOldestObjTime
        windowTypeOldestBound = windowTypeOldestObjTime

        for windowNumber in range(1, windowAmount):
            windowIndex = "{}#{}".format(windowType, windowNumber)
            totalDuration = (windowNumber) * windowDuration
            # windowYoungestBound = windowTypeOldestBound + totalDuration
            windowOldestBound = windowTypeOldestBound + totalDuration
            k = 1
            # for objIndex, (obj, nextObj) in enumerate(zip(sortedObjectsDesc + [None], [None] + sortedObjectsDesc)):
            #     if nextObj and windowOldestBound > nextObj["time"] and obj:
            #         windowIndexToObjectIndex[windowIndex] = objIndex
            #         break

            windowObjIndex = -1
            for objIndex, obj in enumerate(sortedObjectsDesc):
                objTime = obj["time"]
                # if windowOldestBound > objTime:
                # if objTime.date() >= windowOldestBound.date():
                if objTime >= windowOldestBound:
                    windowObjIndex = objIndex
                    # break
                # if objTime >
            if windowObjIndex < 0:
                windowObjIndex = len(sortedObjectsDesc) - 1
            windowIndexToObjectIndex[windowIndex] = windowObjIndex
            # for objIndex, obj in enumerate(reversed(sortedObjectsDesc)):
            #     objTime = obj["time"]
            #     # if windowOldestBound > objTime:
            #     # if objTime.date() >= windowOldestBound.date():
            #     if windowYoungestBound >= objTime:
            #         windowIndexToObjectIndex[windowIndex] = objIndex
            #         # break
            #     if objTime >

            # if sortedObjectsDesc and not windowIndexToObjectIndex.get(windowIndex):
            #     windowIndexToObjectIndex[windowIndex] = len(sortedObjectsDesc) - 1
            # for objIndex, olderObjIndex in zip(range(len(sortedObjectsDesc)), range(1, len(sortedObjectsDesc) + 1)):
            #     if objIndex == len(sortedObjectsDesc) - 1:
            #         # objIndex is the last one
            #         if not windowIndexToObjectIndex.get(windowIndex):
            #             windowIndexToObjectIndex[windowIndex] = objIndex
            #     else:
            #         objTime = sortedObjectsDesc[objIndex]["time"]
            #         olderObjTime = sortedObjectsDesc[olderObjIndex]["time"]
            #         if objTime >= windowOldestBound > olderObjTime or \
            #            objTime > windowOldestBound >= olderObjTime:
            #             windowIndexToObjectIndex[windowIndex] = objIndex
            #             # durationToObjTime = abs(windowOldestBound - objTime)
            #             # durationToOlderObjTime = abs(windowOldestBound - olderObjTime)
            #             # if durationToObjTime <= durationToOlderObjTime:
            #             #     windowIndexToObjectIndex[windowIndex] = objIndex
            #             #     # break
            #             # else:
            #             #     windowIndexToObjectIndex[windowIndex] = olderObjIndex
            #             #     # break



    return windowIndexToObjectIndex


def deleteUselessBackups(windowIndexToObjectIndex, now, policy, sortedObjectsDesc, doDryRun=False):
    requiredObjectIndexes = [objectIndex for _, objectIndex in windowIndexToObjectIndex.items()]
    youngerRequiredIndex = requiredObjectIndexes[0] if len(requiredObjectIndexes) > 0 else None
    requiredObjectIndexes = list(set(requiredObjectIndexes))
    dryRun = []
    newSortedObjectDesc = []

    aboutToBeEvicted = 0
    amountToKeep = policy["amountOfDaily"] + policy["amountOfWeekly"] + policy["amountOfMonthly"] + policy["amountOfYearly"]
    for objectIndex, obj in enumerate(sortedObjectsDesc):
        objRequiredByAwindow = objectIndex in requiredObjectIndexes
        # objYoungerThanFirstWindow = (youngerRequiredIndex is None or objectIndex < youngerRequiredIndex)
        objYoungerThanFirstWindow = (obj["time"] >= now - datetime.timedelta(hours=48))
        objAboutToBeEvicted = not (objRequiredByAwindow or objYoungerThanFirstWindow)
        aboutToBeEvicted += 1 if objAboutToBeEvicted else 0
        objTooYoungToBeEvicted = True if aboutToBeEvicted <= amountToKeep else False
        keep = objRequiredByAwindow or objYoungerThanFirstWindow  # or objTooYoungToBeEvicted
        dryRun.append((objectIndex, obj, keep, objRequiredByAwindow, objYoungerThanFirstWindow, objTooYoungToBeEvicted))
        if keep:
            newSortedObjectDesc.append(obj)

    if sortedObjectsDesc and (doDryRun or True):
        if len(sortedObjectsDesc) >= 2:  # 23:
            print("now: {}".format(now))
            for index, step in enumerate(dryRun):
                if index >= 2:  # 15:
                    print('{:<5} {:<15}: {:^5} ({:^5} {:^5} {:^5}) {:.>20} from now. {:.>20} from younger. {}'.format(
                        step[0],
                        str(step[1]["time"]),
                        "✓" if step[2] else "✗✗✗",
                        "✓" if step[3] else "✗✗✗",
                        "✓" if step[4] else "✗✗✗",
                        "✓" if step[5] else "✗✗✗",
                        str(now - step[1]["time"]),
                        str(dryRun[index-1][1]["time"] - (step[1]["time"] if index-1 > 0 else "")),
                        [windowIndex for windowIndex, objectIndex in windowIndexToObjectIndex.items() if step[0] == objectIndex]
                        ))
            # if str(now) == str(dryRun[16][1]["time"]):
            #     print("stop")
            m = 1
        # if len(sortedObjectsDesc) >= 23:

    typeToColor = {
        'nothing': '1',
        'daily': '2',
        'weekly': '3',
        'monthly': '4',
        'yearly': '5',
    }
    if sortedObjectsDesc and len(sortedObjectsDesc) >= 2 and abs(sortedObjectsDesc[0]["time"] - sortedObjectsDesc[-1]["time"]) > datetime.timedelta(days=1):
        from genVizualisationImage import vizualiseState
        vizualiseState(now, runIndex, stateIndex=now,
                       dates=[obj["time"] for obj in sortedObjectsDesc],
                       data=[
                           typeToColor[([windowIndex for windowIndex, objectIndex in windowIndexToObjectIndex.items() if sortedObjectIndex == objectIndex]+['nothing#0'])[0].split('#')[0]]
                             for sortedObjectIndex, _ in enumerate(sortedObjectsDesc)])
        m = 3

    if str(now) == "2019-01-09 01:00:00":
        j = 1

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


def main():
    policy = descriptionToPolicy(7, 4, 12, 10)

    sortedObjectsDesc = []
    now = datetime.datetime(2019, 1, 1)

    hoursBetweenEvents = 12
    # total = 24 * 365 * 3
    total = int((24/12) * 365 * 3)
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
            deleteUselessBackups(windowIndexToObjectIndex, now, policy,
                                 sortedObjectsDesc, doDryRun=True)
            print('')

        sortedObjectsDesc = deleteUselessBackups(windowIndexToObjectIndex, now, policy, sortedObjectsDesc)
        # print('')

        timeIncrement = datetime.timedelta(hours=hoursBetweenEvents)
        if not sortedObjectsDesc:
            newObj = {"time": now}
        else:
            newObj = {"time": sortedObjectsDesc[0]["time"] + timeIncrement}
        sortedObjectsDesc = [newObj] + sortedObjectsDesc
        now = now + timeIncrement
        previousUniqueWindowsAmount = currentUniqueWindowsAmount


if __name__ == '__main__':
    main()
