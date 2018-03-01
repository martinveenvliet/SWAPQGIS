def fillswap(atmap, swaptpl, Bfil, BPfil, Cfil, RID, workdir):
    from PyQt4.QtGui import QMessageBox

    def Runyears(startdate, enddate):
        import datetime as dt
        startdate = dt.datetime.strptime(startdate, '%d-%b-%Y')
        enddate = dt.datetime.strptime(enddate, '%d-%b-%Y')
        startyear = startdate.year
        endyear = enddate.year
        amyears = endyear - startyear
        return startdate, enddate, startyear, endyear, amyears

    import datetime as dt
    import math
    from dateutil.relativedelta import relativedelta

    print('Calculating runYears')
    startdate, enddate, startyear, endyear, amyears = Runyears(atmap[u'StartSim'], atmap[u'EndSim'])

    print('Opening swaptpl')
    with open(swaptpl, 'r') as orgfile, open(workdir + 'SWAPRUN.swp', 'w') as newfile:
        for num, line in enumerate(orgfile, 0):
            if "%" not in line:
                newfile.write(line)
            elif '%output%' in line:
                newfile.write(line.replace('%output%', str(RID)))
            elif '%CropSwitch%' in line:
                if atmap.get(u'Crop1'):
                    newfile.write(line.replace('%CropSwitch%', '1'))
                else:
                    newfile.write(line.replace('%CropSwitch%', '0'))
            elif '%Crop%' in line:
                cropnum = 1
                while atmap.get(u'Crop' + str(cropnum)) and not atmap.get(u'Crop' + str(cropnum)) == 'NULL':
                    cropnum = cropnum + 1
                totalyear = 0
                cropnum = cropnum-1
                for x in range(0,int(math.ceil((amyears)/cropnum)+1)):
                    for y in range(1, cropnum+1):
                        for z in Cfil:
                            if z[2] == atmap.get(u'Crop' + unicode(y)):
                                CropIndex = Cfil.index(z)

                        Cstartdate = dt.datetime.strptime(str(Cfil[CropIndex][0]) + '-' + str(startyear),
                                                              '%d-%b-%Y') + relativedelta(years=totalyear)
                        Cenddate = dt.datetime.strptime(str(Cfil[CropIndex][1]) + '-' + str(startyear),
                                                            '%d-%b-%Y') + relativedelta(years=totalyear)

                        if int(atmap.get(u'Irrigation')) == 1:
                            Cropname = '\'' + str(atmap.get(u'Crop' + str(y)))[:-1] + 'i' + '\''
                            Cropfile = '\'' + str(atmap.get(u'Crop' + str(y))) + 'i' + '\''
                        else:
                            Cropname = '\'' + str(atmap.get(u'Crop' + str(y)))[:-1] + '\''
                            Cropfile = '\'' + str(atmap.get(u'Crop' + str(y))) + '\''

                        Croptype = Cfil[CropIndex][3]
                        Starttype = Cfil[CropIndex][4]
                        newfile.write('   ' + str(Starttype) + '      ' + dt.datetime.strftime(Cstartdate,
                                                                                                   '%d-%b-%Y') + '   ' +
                                          dt.datetime.strftime(Cenddate, '%d-%b-%Y') + '    ' + str(Cropname) + '    ' +
                                          str(Cropfile) + '      ' + str(Croptype) + '\n')
                        totalyear = totalyear + 1
            elif '%SOILDIV%' in line:
                amsoil = 0
                indexlist = list()
                for num, z in enumerate(Bfil, 0):
                    if z[0] == atmap.get(u'SoilType'):
                        indexlist.append(num)
                        amsoil = amsoil + 1
                        ISUBLAYER = str(1)
                        SOILLAYER = str(amsoil)
                        if amsoil <= 3: HCOMP = str(1.0)
                        else: HCOMP = str(2.5)
                        HSUBLAY = str(float(z[8]) - float(z[7]))
                        NCOMP = str(int(float(HSUBLAY) / float(HCOMP)))
                        newfile.write('    ' + ISUBLAYER + '      ' + SOILLAYER + '     ' \
                                      + HSUBLAY + '     ' + HCOMP + '        ' + NCOMP + '\n')
                newfile.write('    ' + str(2) + '      ' + str(amsoil) + '     ' \
                              + str(float(200 - 120)) + '     ' + str(5.0) + '        ' + str(
                    int((200 - 120) / 5)) + '\n')
                newfile.write('    ' + str(3) + '      ' + str(amsoil) + '     ' \
                              + str(float(500 - 200)) + '     ' + str(5.0) + '        ' + str(
                    int((500 - 200) / 5)) + '\n')
                newfile.write('    ' + str(4) + '      ' + str(amsoil) + '     ' \
                              + str(float(800)) + '     ' + str(10.0) + '        ' + str(80) + '\n')

            elif '%Soil%' in line:
                for num, z in enumerate(indexlist, 1):
                    Staring = Bfil[z][29]
                    BDENS = str(round(float(Bfil[z][26]) * 1000, 1))
                    for x in BPfil:
                        if x[0] == Staring:
                            Soilrow = x

                    newfile.write(
                        str(num) + '    ' + Soilrow[1] + '  ' + Soilrow[2] + '   ' + Soilrow[3] + '   ' + Soilrow[4] +
                        '    ' + Soilrow[5] + '   ' + Soilrow[6] + '   ' + Soilrow[7] + '  ' + '0.0' +
                        '     ' + Soilrow[8] + '   ' + BDENS + '\n')

            elif '%SOILHEAT%' in line:
                for num, z in enumerate(indexlist, 1):
                    Psilt = float(Bfil[z][15]) / 100
                    Pclay = float(Bfil[z][12]) / 100
                    Psand = round(float(1 - Psilt - Pclay), 3)
                    Phum = float(Bfil[z][12]) / 100
                    newfile.write('   ' + str(num) + '    ' + str(Psand) + '   ' + str(Psilt) + '    ' \
                                  + str(Pclay) + '    ' + str(Phum) + '\n')
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
                        msg.setText("Error: no matching word found in the shapefiles for " + word + ' in swap template file')
                        msg.setIcon(QMessageBox.Critical)
                        msg.show()
                        raise ValueError("Error: no matching word found in the shapefiles for " + word + " in swap template file")
                if not NULLval:
                    newfile.write(line)

    return amsoil

