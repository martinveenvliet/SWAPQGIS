def filldrain(atmap, dratpl, SFWfil, amsoil, workdir):
    import os

    from PyQt4.QtGui import QMessageBox

    def findSFwater(atmap, SFWfil):
        SFName = atmap.get(u'SFIndex')
        for num, x in enumerate(SFWfil, 0):
            if x[1] == SFName:
                SFIndex = num
        return SFIndex

    def Runyears(startdate, enddate):
        import datetime as dt
        startdate = dt.datetime.strptime(startdate, '%d-%b-%Y')
        enddate = dt.datetime.strptime(enddate, '%d-%b-%Y')
        startyear = startdate.year
        endyear = enddate.year
        amyears = endyear - startyear
        return startdate, enddate, startyear, endyear, amyears

    def checklines(linelist, startdate, enddate, amyears, SFWfil, SFI):
        import datetime as dt

        writelist = list()
        weirlist = list()
        manper = 1
        lastvalue = True

        for num in range(0, amyears+1):
            if num == 0:
                for ind, u in enumerate(SFWfil[SFI][3:13], 0):
                    #TODO built in method for MNAP (Surface water dependant on land height
                    if dt.datetime.strptime(u+'-'+str(startdate.year), '%d-%b-%Y') > startdate:
                        line = linelist[ind].replace('%SFDATE%', u+'-'+str(startdate.year))
                        line = line.replace(str(ind + 1), str(manper), 1)
                        line = line.replace('%WSCAP%', atmap.get(u'WSCAP'))
                        line = line.replace('%WLDIP%', atmap.get(u'WLDIP'))
                        line = line.replace('%WLL%', atmap.get(u'WLL'))
                        manper = manper + 1
                        weirlist.append(SFWfil[SFI][13+ind])
                        writelist.append(line)
            elif num == amyears:
                for ind, u in enumerate(SFWfil[SFI][3:13], 0):
                    if dt.datetime.strptime(u+'-'+str(enddate.year), '%d-%b-%Y') < enddate:
                        line = linelist[ind].replace('%SFDATE%', u+'-'+str(enddate.year))
                        line = line.replace(str(ind + 1), str(manper), 1)
                        line = line.replace('%WSCAP%', atmap.get(u'WSCAP'))
                        line = line.replace('%WLDIP%', atmap.get(u'WLDIP'))
                        line = line.replace('%WLL%', atmap.get(u'WLL'))
                        manper = manper+1
                        weirlist.append(SFWfil[SFI][13+ind])
                        writelist.append(line)
                    elif dt.datetime.strptime(u+'-'+str(enddate.year), '%d-%b-%Y') >= enddate and lastvalue == True:
                        lastvalue = False
                        line = linelist[ind].replace('%SFDATE%', u + '-' + str(enddate.year))
                        line = line.replace(str(ind + 1), str(manper), 1)
                        line = line.replace('%WSCAP%', atmap.get(u'WSCAP'))
                        line = line.replace('%WLDIP%', atmap.get(u'WLDIP'))
                        line = line.replace('%WLL%', atmap.get(u'WLL'))
                        manper = manper + 1
                        weirlist.append(SFWfil[SFI][13 + ind])
                        writelist.append(line)

                    if u == SFWfil[SFI][12] and lastvalue == True:
                        lastvalue = False
                        line = linelist[ind].replace('%SFDATE%', enddate.strftime('%d-%b-%Y'))
                        line = line.replace(str(ind + 1), str(manper), 1)
                        line = line.replace('%WSCAP%', atmap.get(u'WSCAP'))
                        line = line.replace('%WLDIP%', atmap.get(u'WLDIP'))
                        line = line.replace('%WLL%', atmap.get(u'WLL'))
                        manper = manper + 1
                        weirlist.append(SFWfil[SFI][13 + ind])
                        writelist.append(line)
            else:
                for ind, u in enumerate(SFWfil[SFI][3:13], 0):
                    line = linelist[ind].replace('%SFDATE%', u+'-'+ str(startdate.year+num))
                    line = line.replace(str(ind+1), str(manper), 1)
                    line = line.replace('%WSCAP%', atmap.get(u'WSCAP'))
                    line = line.replace('%WLDIP%', atmap.get(u'WLDIP'))
                    line = line.replace('%WLL%', atmap.get(u'WLL'))
                    manper = manper+1
                    weirlist.append(SFWfil[SFI][13 + ind])
                    writelist.append(line)

        return manper, weirlist, writelist

    def sortDrains(lines):
        #Replace lev
        #move rest of line
        import re

        zbvalues = list()
        sortlist = list()
        for line in lines:
            zbvalues.append(float(line.split()[3]))

        zbvalues.sort()

        for num, zb in enumerate(zbvalues,1):
            written = False
            for line in lines:
                if str(zb) in line and not written:
                    line = line.replace(re.search(r'\d+', line).group(), str(num))
                    sortlist.append(line)
                    written = True

        return sortlist


    startdate, enddate, startyear, endyear, amyears = Runyears(atmap[u'StartSim'], atmap[u'EndSim'])
    SFI = findSFwater(atmap, SFWfil)
    lastvalue = True
    linelist = list()

    with open(dratpl, 'r') as orgfile, open(workdir + 'DRAINRUN.dra', 'w') as newfile:
        for line in orgfile:
            if not '%' in line:
                newfile.write(line)
            elif '%COFANI%' in line:
                newfile.write('COFANI = ')
                for l in range(0, amsoil):
                    newfile.write(' 1.0 ')
                newfile.write('\n')

            elif '%NumDrains%' in line:
                am=1
                while atmap.get(u'l' + str(am)) and not atmap.get(u'l'+str(am)) == 'NULL':
                   am=am+1
                newfile.write(line.replace('%NumDrains%', str(am-1)))
            elif '%StartLevel%' in line:
                newfile.write(line.replace('%StartLevel%', SFWfil[SFI][2]))
            elif '%Nman%' in line:
                import datetime as dt

                manper = 0
                for num in range(0, amyears + 1):
                    if num == 0:
                        for ind, u in enumerate(SFWfil[SFI][3:13], 0):
                            if dt.datetime.strptime(u + '-' + str(startdate.year), '%d-%b-%Y') > startdate:
                                manper = manper + 1
                    elif num == amyears:
                        for ind, u in enumerate(SFWfil[SFI][3:13], 0):
                            if dt.datetime.strptime(u + '-' + str(enddate.year), '%d-%b-%Y') < enddate:
                                manper = manper + 1
                            elif dt.datetime.strptime(u + '-' + str(enddate.year),
                                                      '%d-%b-%Y') >= enddate and lastvalue == True:
                                lastvalue = False
                                manper = manper + 1
                    else:
                        for u in enumerate(SFWfil[SFI][3:13], 0):
                            manper = manper + 1

                newfile.write(line.replace('%Nman%', str(manper+1)))
            elif '%SFDATE%' in line:
                linelist.append(line)
                if len(linelist) == 10:
                    manper, weirlist, writelist = checklines(linelist, startdate, enddate, amyears, SFWfil,
                                                                  SFI)
                    for x in writelist:
                        newfile.write(x)
            elif '%DischargeRel%' in line:
                alpha = 1.7 * float(atmap.get(u'weirwidth')) * 1.1
                beta = 1.5
                for u in range(1, manper):
                    newfile.write(
                        '  ' + str(u) + '  ' + weirlist[u - 1] + '   ' + str(alpha) + '     ' + str(beta) + '\n')
            else:
                NULLval = False
                while '%' in line and not NULLval:
                    word = line.split('%')[1]
                    if atmap.get(unicode(word)) == 'NULL':
                        NULLval = True
                    elif atmap.get(unicode(word)):
                        line = line.replace('%'+word+'%', atmap.get(unicode(word)))
                    else:
                        msg = QMessageBox()
                        msg.setText("Error: no matching word found in the shapefiles for " + word + ' in drain template file')
                        msg.setIcon(QMessageBox.Critical)
                        msg.show()
                        raise ValueError("Error: no matching word found in the shapefiles for " + word + " in drain template file")
                if not NULLval:
                    newfile.write(line)

    #sort drains based on Zbot (deepest drain first)
    with open(workdir + 'DRAINRUN.dra', 'r') as orgfile, open(workdir + 'DRAINRUN2.dra', 'w') as newfile:
        drainlines = False
        drainlist = list()
        sortdrain = list()
        for line in orgfile:
            if ('LEV' in line and 'SWDTYP' in line and 'L' in line and 'ZBOTDRE' in line):
                drainlines = True
                newfile.write(line)
            elif '* End_of_table' in line and drainlines:
                sortdrain = sortDrains(drainlist)
                for drain in sortdrain:
                    newfile.write(drain)
                drainlines = False
                newfile.write(line)
            elif drainlines:
                drainlist.append(line)
            else:
                newfile.write(line)

    os.remove(workdir + 'DRAINRUN.dra')
    os.rename(workdir + 'DRAINRUN2.dra', workdir + 'DRAINRUN.dra')