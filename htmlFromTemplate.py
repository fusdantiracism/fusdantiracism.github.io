import csv

def processCSV(filepath):
    nameCol = 1
    fusdAffiliationCol = 2
    schoolAffiliationCol = 3
    yearCol = 4
    otherAffiliationCol = 5

    signatoriesByFUSDAffiliation = {}
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

            row = "          <tr><td>"+name+"</td> <td>"
            if (len(school.strip()) > 0 or len(year.strip()) > 0 or len(otherAffiliation.strip()) > 0):
                row += "("
                if (len(school.strip()) > 0):
                    row += school
                    if (len(year.strip()) > 0):
                        if "Would have graduated 2014, left school in 2011" in year:
                            year = "2011"
                        row += " " + year
                    # if (len(otherAffiliation.strip()) > 0):
                    #     row += ", " + otherAffiliation
                elif (len(otherAffiliation.strip()) > 0):
                    row += otherAffiliation
                row += ")"
            row += "</td></tr>\n"

            signatoriesByFUSDAffiliation[fusdAffiliation].append(row)

        return signatoriesByFUSDAffiliation, totalNum

if __name__ == "__main__":
    minNumSig = 1

    signatoriesByFUSDAffiliation, numSignatories = processCSV("FUSD Anti-Racism Petition (Responses) - Form Responses 1.csv")
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
                        finalLines = []
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
                        finalLines = []
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
                        finalLines = []
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
                        finalLines = []
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
                        finalLines = []
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
                        finalLines = []
                        if ("Other" in signatoriesByFUSDAffiliation):
                            for row in signatoriesByFUSDAffiliation["Other"]:
                                finalLines.append(row)
                    finalFile.writelines(finalLines)
                else:
                    finalFile.write(line)
