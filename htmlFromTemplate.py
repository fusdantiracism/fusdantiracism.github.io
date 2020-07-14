import csv

def processCSV(filepath):
    nameCol = 1
    fusdAffiliationCol = 2
    schoolAffiliationCol = 3
    yearCol = 4
    otherAffiliationCol = 5
    commentCol = 6

    signatoriesByFUSDAffiliation = {}
    otherAffiliationData = []
    commentBlocks = []
    totalNum = 0

    with open(filepath, "r") as f:
        reader = csv.reader(f)
        next(reader) # skip header
        for row in reader:
            totalNum += 1

            fusdAffiliation = row[fusdAffiliationCol]
            if fusdAffiliation not in signatoriesByFUSDAffiliation:
                signatoriesByFUSDAffiliation[fusdAffiliation] = []

            name = row[nameCol]
            school = row[schoolAffiliationCol]
            year = row[yearCol]
            otherAffiliation = row[otherAffiliationCol]
            comment = row[commentCol]

            # Correct anomalous form entries that mess up the webpage design
            if "Would have graduated 2014, left school in 2011" in year:
                otherAffiliation = year
                year = "2011"
            if "2014, 2015,  2018;  Kids suffered all the abuses from racist teachers." in year:
                otherAffiliation = year
                year = "2018"
            if otherAffiliation.lower().strip() in ["no", "n/a", "na", "none"]:
                otherAffiliation = ""
            if comment.lower().strip()  in ["no", "n/a", "na", "none", "Aaryan Rustagi"]:
                comment = ""
            if year == "202,120,222,026":
                year = "2021,2022,2026"
            if year == "Mission San Jose High 2023":
                year = "2023"
            if otherAffiliation == "Only my name":
                otherAffiliation = ""
            if comment == "Not as of now!!":
                comment = ""

            row = "          <tr><td>"+name+"</td> <td>"
            rowNoHTML = name + " (" + fusdAffiliation;
            if (len(school.strip()) > 0 or len(year.strip()) > 0):
                row += "("
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
            row += "</td></tr>\n"
            rowNoHTML += ")"

            if (len(comment.strip()) > 0):
                commentBlock = '''<div class="comment-box"><div class="container">
          %s
          <small class="byline">%s</small>
        </div></div>
                ''' % (comment, rowNoHTML)
                commentBlocks.append(commentBlock)

            signatoriesByFUSDAffiliation[fusdAffiliation].append(row)

        return signatoriesByFUSDAffiliation, totalNum, otherAffiliationData, commentBlocks

if __name__ == "__main__":
    minNumSig = 1

    signatoriesByFUSDAffiliation, numSignatories, otherAffiliationData, commentBlocks = processCSV("FUSD Anti-Racism Petition (Responses) - Form Responses 1.csv")
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
                            for row in signatoriesByFUSDAffiliation["FUSD Student"]:
                                finalLines.append(row)
                    elif (templateElement == "{{#Teachers}}"):
                        num = len(signatoriesByFUSDAffiliation["FUSD Teacher, Administration, or Staff (current or former)"]) if "FUSD Teacher, Administration, or Staff (current or former)" in signatoriesByFUSDAffiliation else 0
                        if num < minNumSig:
                            finalLines = [beforeTemplateElement + afterTemplateElement]
                        else:
                            finalLines = [beforeTemplateElement + str(num) + afterTemplateElement]
                    elif (templateElement == "{{TeachersList}}"):
                        if ("FUSD Teacher, Administration, or Staff (current or former)" in signatoriesByFUSDAffiliation):
                            for row in signatoriesByFUSDAffiliation["FUSD Teacher, Administration, or Staff (current or former)"]:
                                finalLines.append(row)
                    elif (templateElement == "{{#Alumni}}"):
                        num = len(signatoriesByFUSDAffiliation["FUSD Alumni"]) if "FUSD Alumni" in signatoriesByFUSDAffiliation else 0
                        if num < minNumSig:
                            finalLines = [beforeTemplateElement + afterTemplateElement]
                        else:
                            finalLines = [beforeTemplateElement + str(num) + afterTemplateElement]
                    elif (templateElement == "{{AlumniList}}"):
                        if ("FUSD Alumni" in signatoriesByFUSDAffiliation):
                            for row in signatoriesByFUSDAffiliation["FUSD Alumni"]:
                                finalLines.append(row)
                    elif (templateElement == "{{#Parents}}"):
                        num = len(signatoriesByFUSDAffiliation["FUSD Parent"]) if "FUSD Parent" in signatoriesByFUSDAffiliation else 0
                        if num < minNumSig:
                            finalLines = [beforeTemplateElement + afterTemplateElement]
                        else:
                            finalLines = [beforeTemplateElement + str(num) + afterTemplateElement]
                    elif (templateElement == "{{ParentsList}}"):
                        if ("FUSD Parent" in signatoriesByFUSDAffiliation):
                            for row in signatoriesByFUSDAffiliation["FUSD Parent"]:
                                finalLines.append(row)
                    elif (templateElement == "{{#FremontCommunityMembers}}"):
                        num = len(signatoriesByFUSDAffiliation["Fremont Community Member"]) if "Fremont Community Member" in signatoriesByFUSDAffiliation else 0
                        if num < minNumSig:
                            finalLines = [beforeTemplateElement + afterTemplateElement]
                        else:
                            finalLines = [beforeTemplateElement + str(num) + afterTemplateElement]
                    elif (templateElement == "{{FremontCommunityMembersList}}"):
                        if ("Fremont Community Member" in signatoriesByFUSDAffiliation):
                            for row in signatoriesByFUSDAffiliation["Fremont Community Member"]:
                                finalLines.append(row)
                    elif (templateElement == "{{#Other}}"):
                        num = len(signatoriesByFUSDAffiliation["Other"]) if "Other" in signatoriesByFUSDAffiliation else 0
                        if num < minNumSig:
                            finalLines = [beforeTemplateElement + afterTemplateElement]
                        else:
                            finalLines = [beforeTemplateElement + str(num) + afterTemplateElement]
                    elif (templateElement == "{{OtherList}}"):
                        if ("Other" in signatoriesByFUSDAffiliation):
                            for row in signatoriesByFUSDAffiliation["Other"]:
                                finalLines.append(row)
                    elif (templateElement == "{{Comments}}"):
                        for commentBlock in commentBlocks:
                            print(commentBlock)
                            finalLines.append(commentBlock)
                    elif (templateElement == "{{Other_Affiliations}}"):
                        for i in range(len(otherAffiliationData)):
                            otherAffiliation = otherAffiliationData[i]
                            row = "tippy('#comment%d-button', {content: '%s'});" % (i, otherAffiliation)
                            finalLines.append(row)
                    finalFile.writelines(finalLines)
                else:
                    finalFile.writelines([line])
