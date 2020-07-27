import csv
import html
import matplotlib.pyplot as plt

def processCSV(filepath):
    nameCol = 1
    fusdAffiliationCol = 2
    schoolAffiliationCol = 3
    yearCol = 4
    otherAffiliationCol = 5
    commentCol = 6

    signatoriesByFUSDAffiliation = {}
    rawData = []
    otherAffiliationData = []
    commentBlocks = []
    totalNum = 0

    with open(filepath, "r") as f:
        reader = csv.reader(f)
        next(reader) # skip header
        for row in reader:
            totalNum += 1

            fusdAffiliation = row[fusdAffiliationCol]
            fusdAffiliation = html.escape(fusdAffiliation)
            if fusdAffiliation not in signatoriesByFUSDAffiliation:
                signatoriesByFUSDAffiliation[fusdAffiliation] = []

            name = row[nameCol]
            school = row[schoolAffiliationCol]
            year = row[yearCol]
            otherAffiliation = row[otherAffiliationCol]
            comment = row[commentCol]

            if "<" in name or ">" in name:
                print("HTML Cross-Site Scripting attack name", name)
                continue
            if "<" in school or ">" in school:
                print("HTML Cross-Site Scripting attack school", school)
                continue
            if "<" in year or ">" in year:
                print("HTML Cross-Site Scripting attack year", year)
                year = ""
            if "<" in otherAffiliation or ">" in otherAffiliation:
                print("HTML Cross-Site Scripting attack otherAffiliation", otherAffiliation)
                otherAffiliation = ""
            if "<" in comment or ">" in comment:
                print("HTML Cross-Site Scripting attack comment", comment)
                comment = ""

            # Correct anomalous form entries that mess up the webpage design
            if "Would have graduated 2014, left school in 2011" in year:
                otherAffiliation = year
                year = "2011"
            if "2014, 2015,  2018;  Kids suffered all the abuses from racist teachers." in year:
                otherAffiliation = year
                year = "2018"
            if otherAffiliation.lower().strip() in ["no", "n/a", "na", "none", "diversify the admin & teachers-need multi-ethnic group to match the student body in the school of attendance.", "alek gent-vincent"]:
                otherAffiliation = ""
            if comment.lower().strip()  in ["no", "n/a", "na", "none", "aaryan rustagi", "yes", "diya", "not as of now!!"]:
                comment = ""
            if comment.strip() == "Retired teacher":
                otherAffiliation = "Retired teacher"
                comment = ""
            if year == "202,120,222,026":
                year = "2021,2022,2026"
            if year == "Mission San Jose High 2023":
                year = "2023"
            if year == "i graduated from MSJ in FUSD in 1998.  I am currently a teacher for FUSD.":
                year = "(MSJHS 1998)"
            if year.lower().strip() == "n/a":
                year = ""
            if otherAffiliation == "Only my name":
                otherAffiliation = ""
            if comment == "Not as of now!!":
                comment = ""

            name = html.escape(name)
            school = html.escape(school)
            year = html.escape(year)
            otherAffiliation = html.escape(otherAffiliation)
            comment = html.escape(comment)

            rawData.append({
                "name" : name,
                "school" : school,
                "year" : year,
                "otherAffiliation" : otherAffiliation,
                "comment" : comment,
            })

            row = "<td>"+name
            rowNoHTML = name + " (" + fusdAffiliation;
            if (len(school.strip()) > 0 or len(year.strip()) > 0):
                row += " ("
                rowNoHTML += ", "
                if (len(school.strip()) > 0):
                    row += school
                    rowNoHTML += school
                    if (len(year.strip()) > 0):
                        row += " "
                        rowNoHTML += " "
                if (len(year.strip()) > 0):
                    row += year
                    rowNoHTML += year
                row += ")"
            if (len(otherAffiliation.strip()) > 0):
                otherAffiliationI = len(otherAffiliationData)
                row += '&nbsp;&nbsp;<i id="comment%d-button" class="fa fa-plus" aria-hidden="true"></i>' % otherAffiliationI
                otherAffiliationData.append(otherAffiliation)
            row += "</td>"
            rowNoHTML += ")"

            if (len(comment.strip()) > 0):
                commentBlock = '''<div class="comment-box"><div class="container">
          %s
          <small class="byline">%s</small>
        </div></div>
                ''' % (comment, rowNoHTML)
                commentBlocks.append(commentBlock)

            signatoriesByFUSDAffiliation[fusdAffiliation].append(row)

        return signatoriesByFUSDAffiliation, totalNum, otherAffiliationData, commentBlocks, rawData

if __name__ == "__main__":
    minNumSig = 1
    numSigCols = 2

    signatoriesByFUSDAffiliation, numSignatories, otherAffiliationData, commentBlocks, rawData = processCSV("FUSD Anti-Racism Petition (Responses) - Form Responses 1.csv")
    print(signatoriesByFUSDAffiliation)

    with open("template.template", "r") as templateFile:
        with open("index.html", "w") as finalFile:
            for line in templateFile.readlines():
                if ("{{" in line): # Check if we have to fill any template element
                    # This code assumes there is only one template element per line
                    templateElementStartI = line.index("{{")
                    templateElementEndI = line.index("}}")+2

                    beforeTemplateElement = line[:templateElementStartI]
                    templateElement = line[templateElementStartI:templateElementEndI]
                    afterTemplateElement = line[templateElementEndI:]

                    finalLines = []
                    if (templateElement == "{{#Total}}"):
                        if numSignatories < minNumSig:
                            finalLines = [beforeTemplateElement + afterTemplateElement]
                        else:
                            finalLines = [beforeTemplateElement + str(numSignatories) + afterTemplateElement]
                    elif (templateElement == "{{#Students}}"):
                        num = len(signatoriesByFUSDAffiliation["FUSD Student"]) if "FUSD Student" in signatoriesByFUSDAffiliation else 0
                        if num < minNumSig:
                            finalLines = [beforeTemplateElement + afterTemplateElement]
                        else:
                            finalLines = [beforeTemplateElement + str(num) + afterTemplateElement]
                    elif (templateElement == "{{StudentsList}}"):
                        if ("FUSD Student" in signatoriesByFUSDAffiliation):
                            for i in range(0, len(signatoriesByFUSDAffiliation["FUSD Student"]), numSigCols):
                                row = "<tr>"
                                for k in range(numSigCols):
                                    if i+k < len(signatoriesByFUSDAffiliation["FUSD Student"]):
                                        row += signatoriesByFUSDAffiliation["FUSD Student"][i+k]
                                    else:
                                        row += "<td></td>"
                                row += "</tr>"
                                finalLines.append(row)
                            # for row in signatoriesByFUSDAffiliation["FUSD Student"]:
                            #     finalLines.append(row)
                    elif (templateElement == "{{#Teachers}}"):
                        num = len(signatoriesByFUSDAffiliation["FUSD Teacher, Administration, or Staff (current or former)"]) if "FUSD Teacher, Administration, or Staff (current or former)" in signatoriesByFUSDAffiliation else 0
                        if num < minNumSig:
                            finalLines = [beforeTemplateElement + afterTemplateElement]
                        else:
                            finalLines = [beforeTemplateElement + str(num) + afterTemplateElement]
                    elif (templateElement == "{{TeachersList}}"):
                        if ("FUSD Teacher, Administration, or Staff (current or former)" in signatoriesByFUSDAffiliation):
                            for i in range(0, len(signatoriesByFUSDAffiliation["FUSD Teacher, Administration, or Staff (current or former)"]), numSigCols):
                                row = "<tr>"
                                for k in range(numSigCols):
                                    if i+k < len(signatoriesByFUSDAffiliation["FUSD Teacher, Administration, or Staff (current or former)"]):
                                        row += signatoriesByFUSDAffiliation["FUSD Teacher, Administration, or Staff (current or former)"][i+k]
                                    else:
                                        row += "<td></td>"
                                row += "</tr>"
                                finalLines.append(row)
                            # for row in signatoriesByFUSDAffiliation["FUSD Teacher, Administration, or Staff (current or former)"]:
                            #     finalLines.append(row)
                    elif (templateElement == "{{#Alumni}}"):
                        num = len(signatoriesByFUSDAffiliation["FUSD Alumni"]) if "FUSD Alumni" in signatoriesByFUSDAffiliation else 0
                        if num < minNumSig:
                            finalLines = [beforeTemplateElement + afterTemplateElement]
                        else:
                            finalLines = [beforeTemplateElement + str(num) + afterTemplateElement]
                    elif (templateElement == "{{AlumniList}}"):
                        if ("FUSD Alumni" in signatoriesByFUSDAffiliation):
                            for i in range(0, len(signatoriesByFUSDAffiliation["FUSD Alumni"]), numSigCols):
                                row = "<tr>"
                                for k in range(numSigCols):
                                    if i+k < len(signatoriesByFUSDAffiliation["FUSD Alumni"]):
                                        row += signatoriesByFUSDAffiliation["FUSD Alumni"][i+k]
                                    else:
                                        row += "<td></td>"
                                row += "</tr>"
                                finalLines.append(row)
                            # for row in signatoriesByFUSDAffiliation["FUSD Alumni"]:
                            #     finalLines.append(row)
                    elif (templateElement == "{{#Parents}}"):
                        num = len(signatoriesByFUSDAffiliation["FUSD Parent"]) if "FUSD Parent" in signatoriesByFUSDAffiliation else 0
                        if num < minNumSig:
                            finalLines = [beforeTemplateElement + afterTemplateElement]
                        else:
                            finalLines = [beforeTemplateElement + str(num) + afterTemplateElement]
                    elif (templateElement == "{{ParentsList}}"):
                        if ("FUSD Parent" in signatoriesByFUSDAffiliation):
                            for i in range(0, len(signatoriesByFUSDAffiliation["FUSD Parent"]), numSigCols):
                                row = "<tr>"
                                for k in range(numSigCols):
                                    if i+k < len(signatoriesByFUSDAffiliation["FUSD Parent"]):
                                        row += signatoriesByFUSDAffiliation["FUSD Parent"][i+k]
                                    else:
                                        row += "<td></td>"
                                row += "</tr>"
                                finalLines.append(row)
                            # for row in signatoriesByFUSDAffiliation["FUSD Parent"]:
                            #     finalLines.append(row)
                    elif (templateElement == "{{#FremontCommunityMembers}}"):
                        num = len(signatoriesByFUSDAffiliation["Fremont Community Member"]) if "Fremont Community Member" in signatoriesByFUSDAffiliation else 0
                        if num < minNumSig:
                            finalLines = [beforeTemplateElement + afterTemplateElement]
                        else:
                            finalLines = [beforeTemplateElement + str(num) + afterTemplateElement]
                    elif (templateElement == "{{FremontCommunityMembersList}}"):
                        if ("Fremont Community Member" in signatoriesByFUSDAffiliation):
                            for i in range(0, len(signatoriesByFUSDAffiliation["Fremont Community Member"]), numSigCols):
                                row = "<tr>"
                                for k in range(numSigCols):
                                    if i+k < len(signatoriesByFUSDAffiliation["Fremont Community Member"]):
                                        row += signatoriesByFUSDAffiliation["Fremont Community Member"][i+k]
                                    else:
                                        row += "<td></td>"
                                row += "</tr>"
                                finalLines.append(row)
                            # for row in signatoriesByFUSDAffiliation["Fremont Community Member"]:
                            #     finalLines.append(row)
                    elif (templateElement == "{{#Other}}"):
                        num = len(signatoriesByFUSDAffiliation["Other"]) if "Other" in signatoriesByFUSDAffiliation else 0
                        if num < minNumSig:
                            finalLines = [beforeTemplateElement + afterTemplateElement]
                        else:
                            finalLines = [beforeTemplateElement + str(num) + afterTemplateElement]
                    elif (templateElement == "{{OtherList}}"):
                        if ("Other" in signatoriesByFUSDAffiliation):
                            for i in range(0, len(signatoriesByFUSDAffiliation["Other"]), numSigCols):
                                row = "<tr>"
                                for k in range(numSigCols):
                                    if i+k < len(signatoriesByFUSDAffiliation["Other"]):
                                        row += signatoriesByFUSDAffiliation["Other"][i+k]
                                    else:
                                        row += "<td></td>"
                                row += "</tr>"
                                finalLines.append(row)
                            # for row in signatoriesByFUSDAffiliation["Other"]:
                            #     finalLines.append(row)
                    elif (templateElement == "{{Comments}}"):
                        for commentBlock in commentBlocks:
                            # print(commentBlock)
                            finalLines.append(commentBlock)
                    elif (templateElement == "{{Other_Affiliations}}"):
                        for i in range(len(otherAffiliationData)):
                            otherAffiliation = otherAffiliationData[i]
                            row = "tippy('#comment%d-button', {content: '%s'});" % (i, otherAffiliation)
                            finalLines.append(row)
                    finalFile.writelines(finalLines)
                else:
                    finalFile.writelines([line])

    # Save pie charts
    # affiliationLabels = [affiliation for affiliation in signatoriesByFUSDAffiliation]
    affiliationLabels = ["FUSD Teacher, Administration, or Staff (current or former)", "FUSD Student", "FUSD Parent", "Other", "FUSD Alumni", "Fremont Community Member"]
    affiliationCount = [len(signatoriesByFUSDAffiliation[affiliation]) for affiliation in affiliationLabels]
    totalCount = sum(affiliationCount)
    affiliationLabels[0] = "FUSD Teacher, Administration, \nor Staff (current or former)"

    def printPercent(pct):
        count = int(round(totalCount*pct/100))
        return '%1.1f%%\n(%d)' % (pct, count)

    fig = plt.figure(figsize=(8,6))
    ax = fig.subplots()
    ax.pie(affiliationCount, labels=affiliationLabels, autopct=printPercent)
    ax.set_title("Signatories by FUSD Affiliation (%d)" % totalCount)
    plt.savefig("signatoriesByFUSDAffiliation.png")

    schoolToAttendanceAreaAndLevel = {
        "American High" : ("American High School", "High"),
        "Ardenwood Elementary" : ("American High School", "Elementary"),
        "Brookvale Elementary" : ("American High School", "Elementary"),
        "Forest Park Elementary" : ("American High School", "Elementary"),
        "Oliveira Elementary" : ("American High School", "Elementary"),
        "Patterson Elementary" : ("American High School", "Elementary"),
        "Thornton Junior High" : ("American High School", "Middle"),
        "Warwick Elementary" : ("American High School", "Elementary"),
        "Green Elementary" : ("Irvington High School", "Elementary"),
        "Grimmer Elementary" : ("Irvington High School", "Elementary"),
        "Hirsch Elementary" : ("Irvington High School", "Elementary"),
        "Horner Middle School" : ("Irvington High School", "Middle"),
        "Horner Junior High" : ("Irvington High School", "Middle"),
        "Irvington High" : ("Irvington High School", "High"),
        "Leitch Elementary" : ("Irvington High School", "Elementary"),
        "Warm Springs Elementary" : ("Irvington High School", "Elementary"),
        "Weibel Elementary" : ("Irvington High School", "Elementary"),
        "Azevada Elementary" : ("Kennedy High School", "Elementary"),
        "Blacow Elementary" : ("Kennedy High School", "Elementary"),
        "Brier Elementary" : ("Kennedy High School", "Elementary"),
        "Bringhurst Elementary" : ("Kennedy High School", "Elementary"),
        "Durham Elementary" : ("Kennedy High School", "Elementary"),
        "Kennedy High" : ("Kennedy High School", "High"),
        "Mattos Elementary" : ("Kennedy High School", "Elementary"),
        "Millard Elementary" : ("Kennedy High School", "Elementary"),
        "Walters Middle" : ("Kennedy High School", "Middle"),
        "Chadbourne Elementary" : ("Mission San Jose High School", "Elementary"),
        "Gomes Elementary" : ("Mission San Jose High School", "Elementary"),
        "Hopkins Junior High" : ("Mission San Jose High School", "Middle"),
        "Mission San Jose Elementary" : ("Mission San Jose High School", "Elementary"),
        "Mission San Jose High" : ("Mission San Jose High School", "High"),
        "Mission Valley Elementary" : ("Mission San Jose High School", "Elementary"),
        "Cabrillo Elementary" : ("Washington High School", "Elementary"),
        "Centerville Junior High" : ("Washington High School", "Elementary"),
        "Glenmoor Elementary" : ("Washington High School", "Elementary"),
        "Maloney Elementary" : ("Washington High School", "Elementary"),
        "Niles Elementary" : ("Washington High School", "Elementary"),
        "Parkmont Elementary" : ("Washington High School", "Elementary"),
        "Vallejo Mill Elementary" : ("Washington High School", "Elementary"),
        "Washington High" : ("Washington High School", "High"),
        "Cal-SAFE" : ("Other", "Other"),
        "Circle of Independent Learning" : ("Other", "Other"),
        "Fremont Adult and Continuing Ed" : ("Other", "Other"),
        "Glankler Early Learning Center" : ("Other", "Other"),
        "Native American" : ("Other", "Other"),
        "Preschool" : ("Other", "Other"),
        "Robertson High" : ("Other", "Other"),
        "Vista Alternative" : ("Other", "Other"),
    }

    attendanceAreaLabelToCount = {}
    levelLabelToCount = {}
    for data in rawData:
        school = data["school"].strip()
        if len(school) > 0:
            attendanceArea = schoolToAttendanceAreaAndLevel[school][0]
            if attendanceArea not in attendanceAreaLabelToCount:
                attendanceAreaLabelToCount[attendanceArea] = 0
            attendanceAreaLabelToCount[attendanceArea] += 1
            level = schoolToAttendanceAreaAndLevel[school][1]
            if level not in levelLabelToCount:
                levelLabelToCount[level] = 0
            levelLabelToCount[level] += 1

    attendanceAreaLabels = [attendanceArea for attendanceArea in attendanceAreaLabelToCount]
    attendanceAreaLabels = ["Irvington High School", "Kennedy High School", "Washington High School", "American High School", "Mission San Jose High School", "Other"]
    attendanceAreaCount = [attendanceAreaLabelToCount[attendanceArea] for attendanceArea in attendanceAreaLabels]
    totalCount = sum(attendanceAreaCount)

    def printPercent(pct):
        count = int(round(totalCount*pct/100))
        return '%1.1f%%\n(%d)' % (pct, count)

    fig = plt.figure(figsize=(8,6))
    ax = fig.subplots()
    ax.pie(attendanceAreaCount, labels=attendanceAreaLabels, autopct=printPercent)
    ax.set_title("Signatories by Attendance Area (%d)" % totalCount)
    plt.savefig("signatoriesByAttendanceArea.png")

    levelLabels = [level for level in levelLabelToCount]
    levelCount = [levelLabelToCount[level] for level in levelLabels]
    totalCount = sum(levelCount)

    def printPercent(pct):
        count = int(round(totalCount*pct/100))
        return '%1.1f%%\n(%d)' % (pct, count)

    fig = plt.figure(figsize=(8,6))
    ax = fig.subplots()
    ax.pie(levelCount, labels=levelLabels, autopct=printPercent)
    ax.set_title("Signatories by School Level (%d)" % totalCount)
    plt.savefig("signatoriesBySchoolLevel.png")
