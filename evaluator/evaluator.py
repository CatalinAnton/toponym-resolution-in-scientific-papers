'''
Created on Jun 11, 2018

@author: dweissen
'''

# to run evaluator:python evaluator.py input output Detection
# arg1: input folder path (for example, an .ann file outputed by the project
# arg2: output folder path (to have a file scores.txt
# arg3: evaluator mode: Detection | Disambiguation | Resolution
import logging as log
# from statistics import mean
import sys
import re
import os
import glob


class Annotation(object):
    """
    Basic class to read the annotation
    """

    def __init__(self, ID, typeAnn, startOff, endOff, text):
        self.id = ID
        self.type = typeAnn
        self.start = int(startOff)
        self.end = int(endOff)
        self.text = text
        self.typeCom = None
        self.comment = None

    def setComment(self, typeCom, comment):
        self.typeCom = typeCom
        self.comment = comment

    def getID(self):
        return self.id

    def getComment(self):
        if self.typeCom is None and self.comment is None:
            return None
        return [self.typeCom, self.comment]

    def getEndOffset(self):
        return self.end

    def getStartOffset(self):
        return self.start

    def getText(self):
        return self.text


class Toponym(object):
    """
    A convenient class to store the annotations of the toponym
    """

    def __init__(self, ID, startOffset, endOffset, text):
        self.id = ID
        self.start = int(startOffset)
        self.end = int(endOffset)
        assert self.start <= self.end, "The start offset {} < the end offset {}, which should not be.".format(
            self.start, self.end)
        self.text = text
        self.geoID = None
        self.long = None
        self.lat = None
        self.pop = None

    def getStartOffset(self):
        return self.start

    def getEndOffset(self):
        return self.end

    def getOffsets(self):
        return range(self.getStartOffset(), (self.getEndOffset() + 1))

    def getText(self):
        return self.text

    def setGeoID(self, geoID):
        if geoID == "-1":
            geoID = "NA"
        if geoID != "NA":
            assert geoID.isdigit(), "A geoID [{}] is incorrectly formated, should be all digits, check the data.".format(
                geoID)
        self.geoID = geoID

    def getGeoID(self):
        return self.geoID

    def setLatLong(self, latitude, longitude):
        self.lat = latitude
        self.long = longitude
        if self.lat is None and self.long is None:
            return None
        return [self.lat, self.long]

    def setPopulation(self, population):
        self.pop = population

    def getPopulation(self):
        return self.pop

    def __str__(self):
        topo = []
        topo.append(self.getText())
        topo.append(" @")
        topo.append(self.start)
        topo.append(", ")
        topo.append(self.end)
        if self.getGeoID() is not None:
            topo.append(" [geoID: ")
            topo.append(self.getGeoID())
            topo.append("]")
        return ''.join(map(str, topo))


class ExcludedSpan(object):
    """
    We have excluded some span of the text (ex. authors and references sections)
    The spans are noted with 2 annotations BEGIN and END
    """

    def __init__(self):
        pass

    def setBegin(self, ID, startOffset, endOffset, text):
        self.idBeg = ID
        self.startBeg = int(startOffset)
        self.endBeg = int(endOffset)
        self.textBeg = text

    def getStartOffset(self):
        return self.startBeg

    def setEnd(self, ID, startOffset, endOffset, text):
        self.idEnd = ID
        self.startEnd = int(startOffset)
        self.endEnd = int(endOffset)
        self.textEnd = text

    def getEndOffset(self):
        return self.endEnd

    def __str__(self):
        return 'START @{}: {}  --- END @{}: {} '.format(self.startBeg, self.textBeg, self.startEnd, self.textEnd)


class BratSemEvalParser():
    """
    A convenient class to parse the annotations expected for the SemEval task 12 challenge
    """

    def parseAnnotations(self, filePath):
        """
        Reads the input annotations and returns the list of Toponyms and ExcludedSpans annotated
        :param filePath: a valid path+name to the file containing annotation in the Brat format defined for the challenge
        :return: a dictionary of 2 lists the excludedSpans (maybe empty) and the toponyms (may also be empty)
        """
        with open(filePath, 'r') as fileAnnotation:
            lines = fileAnnotation.readlines()
            excludedSpans = self.__parseExcludedSpan__(lines, filePath)
            toponyms = self.__parseToponyms__(lines, filePath)

            return {'excludedSpans': excludedSpans, 'toponyms': toponyms}

    def __parseExcludedSpan__(self, lines, filePath):
        """
        parse the excluded spans
        :return: the list of Excluded Spans objects found
        """
        # a map annotation ID -> Annotation
        annotations = {}
        index = 0
        # we first search the spans excluded
        for line in lines:
            if re.match("T[0-9]+\t.*", line):
                components = line.rstrip().split('\t')
                if len(components) > 3:
                    self.__getTextContainingTabs__(line, components)
                assert len(
                    components) == 3, "Unexpected format in the file {} for the line {}, was expecting 3 substrings tab separated.".format(
                    filePath, line)
                if re.match(r'Protein \d+ \d+', components[1]):
                    elements = components[1].split(' ', 1)
                    self.__getExtendedText__(index, lines, components)
                    offsets = elements[1].split(' ')
                    annotations[components[0][1:]] = Annotation(components[0][1:], elements[0], offsets[0], offsets[-1],
                                                                components[2])
            index = index + 1
        # we then retrieve their comments
        for line in lines:
            if re.match("#[0-9]+\t.*", line):
                components = line.rstrip().split('\t')
                assert len(
                    components) == 3, "Unexpected format in the file {} for the line {}, was expecting 3 substrings tab separated.".format(
                    filePath, line)
                #                 if components[0][1:] in annotations:# else is possible if we have a comment for the Location or other annotations
                #                     annotation = annotations[components[0][1:]]
                #                     assert annotation.getComment() is None, "Found an Excluded Span annotation that has more than one comment, in the file {} for the line {}".format(filePath, line)
                #                     annotation.setComment(components[1], components[2])
                assert components[1].startswith(
                    "AnnotatorNotes T"), "Unexpected format in the file {} for the line {}, was expecting AnnotatorNotes as second element of the comment".format(
                    filePath, line)
                if components[1][
                   16:] in annotations:  # else is possible if we have a comment for the Location or other annotations
                    annotation = annotations[components[1][16:]]
                    assert annotation.getComment() is None, "Found a Excluded Span annotation that has more than one comment, in the file {} for the line {}".format(
                        filePath, line)
                    annotation.setComment(components[1], components[2])
        # check that all ExcludedSpan annotations have found their comments
        for annotation in annotations.values():
            assert annotation.getComment() is not None, "Found an Excluded Span annotation that does not have a comment: {}".format(
                annotation.getID())

        # Now we create the list of ExcludedSpan objects
        spanEndOffsets = {}
        for annotation in annotations.values():
            assert annotation.getEndOffset() not in spanEndOffsets, "Found 2 excluded spans ending at the same position: {}, which should not, in file {}".format(
                annotation.getEndOffset(), filePath)
            spanEndOffsets[int(annotation.getEndOffset())] = annotation
        endOffsets = sorted(spanEndOffsets.keys())
        assert len(
            endOffsets) % 2 == 0, "Found an odd number of excluded spans' offsets: {}, one is probably missing, in file {}".format(
            len(spanEndOffsets), filePath)

        excludedSpans = []
        index = 0
        while index < len(endOffsets):
            beginSpanAnn = spanEndOffsets[endOffsets[index]]
            endSpanAnn = spanEndOffsets[endOffsets[index + 1]]

            assert beginSpanAnn.getComment()[1] == "BEGIN" and endSpanAnn.getComment()[
                1] == "END", "Found 2 successive offsets ({} and {}) that do not refer to a beginning and end of a Excluded span, in file {}".format(
                endOffsets[index], endOffsets[index + 1], filePath)
            exSpan = ExcludedSpan()
            exSpan.setBegin(beginSpanAnn.getID(), beginSpanAnn.getStartOffset(), beginSpanAnn.getEndOffset(),
                            beginSpanAnn.getText())
            exSpan.setEnd(endSpanAnn.getID(), endSpanAnn.getStartOffset(), endSpanAnn.getEndOffset(),
                          endSpanAnn.getText())
            excludedSpans.append(exSpan)
            index = index + 2

        return excludedSpans

    def __parseToponyms__(self, lines, filePath):
        """
        Parse the toponyms in the annotation file. Format expected is Brat format, for example:
        T15    Location 3612 3616    Asia
        #15    AnnotatorNotes T15    <latlng>29.84064,89.29688</latlng><pop>3812366000</pop><geoID>6255147</geoID>
        :return: the list of Toponyms objects found
        """
        # a map annotation ID -> Annotation
        annotations = {}
        # we first search the toponyms
        index = 0
        for line in lines:
            if re.match("T[0-9]+\t.*", line):
                components = line.rstrip().split('\t')
                if len(components) > 3:
                    self.__getTextContainingTabs__(line, components)
                assert len(
                    components) == 3, "Unexpected format in the file {} for the line {}, was expecting 3 substrings tab separated.".format(
                    filePath, line)
                if re.match(r'Location \d+ \d+', components[1]):
                    elements = components[1].split(' ', 1)
                    self.__getExtendedText__(index, lines, components)
                    # the offsets can come in discontinuous in that case we have: T12    Location 10720 10725;10726 10736    West Azerbaijan
                    # we are not interested in the details just first last positions, we assume continuous annotations
                    offsets = elements[1].split(' ')
                    annotations[components[0][1:]] = Annotation(components[0][1:], elements[0], offsets[0], offsets[-1],
                                                                components[2])
            index = index + 1
        # we then retrieve their comments
        for line in lines:
            if re.match("#[0-9]+\t.*", line):
                components = line.rstrip().split('\t')
                assert len(
                    components) == 3, "Unexpected format in the file {} for the line {}, was expecting 3 substrings tab separated.".format(
                    filePath, line)
                #                 if components[0][1:] in annotations:# else is possible if we have a comment for the Location or other annotations
                #                     annotation = annotations[components[0][1:]]
                #                     assert annotation.getComment() is None, "Found a Location annotation that has more than one comment, in the file {} for the line {}".format(filePath, line)
                #                     annotation.setComment(components[1], components[2])
                assert components[1].startswith(
                    "AnnotatorNotes T"), "Unexpected format in the file {} for the line {}, was expecting AnnotatorNotes as second element of the comment".format(
                    filePath, line)
                if components[1][
                   16:] in annotations:  # else is possible if we have a comment for the Location or other annotations
                    annotation = annotations[components[1][16:]]
                    assert annotation.getComment() is None, "Found a Location annotation that has more than one comment, in the file {} for the line {}".format(
                        filePath, line)
                    annotation.setComment(components[1], components[2])
        # check that all locations annotations have found their comments
        for annotation in annotations.values():
            assert annotation.getComment() is not None, "Found an Location annotation that does not have a comment: {}".format(
                annotation.getID())

        # Now we create the Toponyms objects
        geop = re.compile(r'<geoID> *(\d+?|NA|-1) *</geoID>')
        popp = re.compile(r'<pop>(.+?)</pop>')
        llp = re.compile(r'<latlng>(-?[\d.]+?,-?[\d.]+?)</latlng>')
        toponyms = []
        for annotation in annotations.values():
            topo = Toponym(annotation.getID(), annotation.getStartOffset(), annotation.getEndOffset(),
                           annotation.getText())
            m = geop.search(annotation.getComment()[1])
            if m:
                topo.setGeoID(m.group(1))
            m = popp.search(annotation.getComment()[1])
            if m:
                topo.setPopulation(m.group(1))
            m = llp.search(annotation.getComment()[1])
            if m:
                latlong = m.group(1).split(',')
                assert len(
                    latlong) == 2, "Found a longitude and latitude incorrectly formatted {}, in in the file {}".format(
                    annotation.getComment()[1], filePath)
                topo.setLatLong(latlong[0], latlong[1])
            toponyms.append(topo)

        return toponyms

    def __getTextContainingTabs__(self, line, components):
        """
        tabulations can occured in the text and be inserted inside the span annotated like in:
        T33    Location 6173 6182    Sri\tLanka
        #33    AnnotatorNotes T33    <latlng>7.75, 80.75</latlng><geoID>1227603 </geoID><pop>21513990</pop>
        This cause a problem when the annotation is read since the annotation is split with the tabs
        This checks the components and reassembles the third component with its initial tab(s), i.e.
        ['T33', 'Location 6173 6182', 'Sri\tLanka']
        """
        assert (re.match("T[0-9]+",
                         components[0])), "Unexpected format of the line, impossible to find the brat ID in: {}".format(
            line)
        assert (re.match("Location \d+ \d+", components[
            1])), "Unexpected format of the line, impossible to find the Location in: {}".format(line)
        components[2] = '\t'.join(components[2:])
        del components[3:]

    def __getExtendedText__(self, index, lines, components):
        """
        Brat allow multiple lines of texts, for ex.
        T17    Location 961 977;978 1039;1040 1106;1107 1149    virus are still
         poorly understood.
        #17    AnnotatorNotes T17    <latlng>29.84064,89.29688</latlng><pop>3812366000</pop><geoID>62551</geoID>
        This read the extended text and add it to the components
        """
        index = index + 1  # we pass the exact index of the T line
        while index < len(lines):
            if (re.match(r'^(T\d+)\t|(#\d+)\t.+', lines[index])):
                break
            else:
                components[2] = components[2] + '\n' + lines[index].rstrip()
            index = index + 1

    def displayAnnotationsParsed(self, annotations):
        """
        Display the annotations parsed from the file, to debug purpose
        :param annotations: list
        """
        for ann in annotations:
            print(str(ann))


class Prediction(object):
    """
    A convenient class to store all information about a prediction made by the system: was it a FP, TP, FN?
    And what are the prediction and Reference associated by the system (None if none apply)
    """

    def __init__(self, value, toponymPredicted, toponymReference):
        """
        :param value: str equal to TP, FP or FN
        :param toponymPredicted: Toponym that has been predicted, can be None for FN
        :param toponymReference: Toponym reference, can be None for FP
        """
        self.value = value
        assert self.value == 'TP' or self.value == 'FP' or self.value == 'FN', "I found a value for the prediction different from what I expect ('TP', 'FP', 'FN'): {}, check the code.".format(
            value)
        self.topoPred = toponymPredicted
        self.topoRef = toponymReference

    def __str__(self):
        out = []
        out.append(self.value)
        out.append(": (Pred = ")
        if self.topoPred is None:
            out.append("None")
        else:
            out.append(str(self.topoPred))
        out.append(" ; Ref = ")
        if self.topoRef is None:
            out.append("None")
        else:
            out.append(str(self.topoRef))
        out.append(")")
        return ''.join(out)


class Answer(object):
    """
    A convenient class to represent the answer given by an oracle about a prediction
    """

    def __init__(self):
        self.ExcludedToponyms = []
        self.TPs = []
        self.FPs = []
        self.FNs = []
        self.Tcds = []
        self.Tids = []
        self.Tn = None

    def setExcludedToponyms(self, ExcludedToponyms):
        """
        :param ExcludedToponyms: dict
        """
        self.ExcludedToponyms = ExcludedToponyms

    def getExcludedToponyms(self):
        """
        :return: dict
        """
        return self.ExcludedToponyms

    def addTP(self, TP):
        """
        :param TP: Prediction object
        """
        self.TPs.append(TP)

    def getTPs(self):
        """
        :return: list
        """
        return self.TPs

    def addFP(self, FP):
        """
        :param FP: Prediction object
        """
        self.FPs.append(FP)

    def getFPs(self):
        """
        :return: list
        """
        return self.FPs

    def addFN(self, FN):
        """
        :param FN: Prediction object
        """
        self.FNs.append(FN)

    def getFNs(self):
        """
        :return: list
        """
        return self.FNs

    def addTcd(self, Tcd):
        """
        :param Tcd: Prediction object
        """
        if Tcd.topoPred is not None:
            assert Tcd.topoPred.getGeoID() is not None, "Found a toponym in a prediction {} which does not have a geoID or 'NA' value in the disambiguation or Resolution, check the data.".format(
                str(Tcd))
        if Tcd.topoRef is not None:
            assert Tcd.topoRef.getGeoID() is not None, "Found a toponym in a prediction {} which does not have a geoID or 'NA' value in the disambiguation or Resolution, check the data.".format(
                str(Tcd))
        self.Tcds.append(Tcd)

    def getTcds(self):
        """
        :return: list
        """
        return self.Tcds

    def addTid(self, Tid):
        """
        :param Tid: Prediction object
        """
        if Tid.topoPred is not None:
            assert Tid.topoPred.getGeoID() is not None, "Found a toponym in a prediction {} which does not have a geoID or 'NA' value in the disambiguation or Resolution, check the data.".format(
                str(Tid))
        if Tid.topoRef is not None:
            assert Tid.topoRef.getGeoID() is not None, "Found a toponym in a prediction {} which does not have a geoID or 'NA' value in the disambiguation or Resolution, check the data.".format(
                str(Tid))
        self.Tids.append(Tid)

    def getTids(self):
        """
        :return: list
        """
        return self.Tids

    def setTn(self, Tn):
        """
        :param Tn: int
        """
        self.Tn = Tn

    def getTn(self):
        """
        :return: int
        """
        return self.Tn

    def __str__(self):
        """
        display the oracle's answer computed for a given submission, used for debugging
        """
        log.fatal("TO REMOVE!!!")
        msg = ['TPs: ']
        for pred in self.getTPs():
            msg.append(str(pred))
            msg.append(" - ")
        msg.append("\nFPs: ")
        for pred in self.getFPs():
            msg.append(str(pred))
            msg.append(" - ")
        msg.append("\nFNs: ")
        for pred in self.getFNs():
            msg.append(str(pred))
            msg.append(" - ")
        msg.append("\nExcluded Toponyms: ")
        for pred in self.getExcludedToponyms():
            msg.append(str(pred))
            msg.append("; ")
        msg.append("\nTcds: ")
        for pred in self.getTcds():
            msg.append(str(pred))
            msg.append(" - ")
        msg.append("\nTids: ")
        for pred in self.getTids():
            msg.append(str(pred))
            msg.append(" - ")
        msg.append("\nTn: ")
        msg.append(str(self.getTn()))
        return ''.join(msg)


class Oracle(object):
    '''
    The oracle knows the answers and can be asked for an Answer containing TPs, FPs, FNs during evaluations
    '''

    def __init__(self, references):
        '''
        :param references: a dict containing a list of spans excluded from the annotation and a list of toponyms annotated
        '''
        self.excludedSpans = references['excludedSpans']
        self.toponymsReferences = references['toponyms']
        # the map contains all positions that have been annotated linked to the annotation itself
        # ex. position 4 -> toponym 1
        #     position 5 -> toponym 1
        #     position 8 -> excludedSpan 1
        #     position 9 -> excludedSpan 1
        # etc.
        self.mapIndexesAnnotated = {}
        self.__addAnnotationsToMap__(self.excludedSpans)
        self.__addAnnotationsToMap__(self.toponymsReferences)

    def __addAnnotationsToMap__(self, annotations):
        """
        add positions in the map indexing all positions annotated as excluded or toponyms
        :param annotations: list
        """
        for ann in annotations:
            startIndex = ann.getStartOffset()
            index = startIndex
            assert index <= ann.getEndOffset(), "Found a {} which offsets are incoherent start: {} > end: {}".format(
                type(ann), ann.getStartOffset(), ann.getEndOffset())
            while index <= ann.getEndOffset():
                assert index not in self.mapIndexesAnnotated, "Found an existing annotation {} at the positions {} when it should be empty for inserting annotation {}, check the code.".format(
                    self.mapIndexesAnnotated[index], index, str(ann))
                self.mapIndexesAnnotated[index] = ann
                index = index + 1

    def evalDetectionStrictMatching(self, toponymsPredictedWoExcluded):
        """
        Apply a strict matching to compute the TP, FP, FN given the toponyms references and toponyms predicted
        :param toponymsPredicted: the list of toponyms predicted by the system to compare against the toponyms of reference
        :return: an Answer containing the lists of ExcludedToponyms, TPs, FPs and FNs resulting from the comparison
        """
        answer = Answer()
        # start with FP and TP
        for topoPred in toponymsPredictedWoExcluded:
            if topoPred.getStartOffset() in self.mapIndexesAnnotated:
                # the position has been annotated either as excludedSpan or as toponym
                annotation = self.mapIndexesAnnotated[
                    topoPred.getStartOffset()]  # annotation can be an excluded span or toponym for annotation over-spanning
                if type(
                        annotation) == Toponym and topoPred.getStartOffset() == annotation.getStartOffset() and topoPred.getEndOffset() == annotation.getEndOffset():
                    # the predicted toponym has the same boundaries than a toponym annotation in the reference it should be a strict match
                    if topoPred.getText() != annotation.getText():
                        # the span are identical but the text are not, it can be caused by newline or spaces, I remove all and compare again
                        topopredWoSpace = "".join(re.split(r"\s", topoPred.getText()))
                        annotWoSpace = "".join(re.split(r"\s", annotation.getText()))
                        if topopredWoSpace != annotWoSpace:
                            # apparently not only newline and space, the last case is probaly a bug from Brat which may remove the hyphen like in "Ham-\nburg" (PMC4907427, 41948 41957), the annotation written is "Ham burg"
                            topopredWoSpaceWoHyphen = "".join(re.split("-", topopredWoSpace))
                            annotWoSpaceWoHyphen = "".join(re.split("-", annotWoSpace))
                            assert topopredWoSpaceWoHyphen == annotWoSpaceWoHyphen, "Found a predicted toponym {} and a reference toponym at the same position with different texts {} and {}, should not be check the data...".format(
                                str(topoPred), str(annotation), topoPred.getText(), annotation.getText())
                    answer.addTP(Prediction('TP', topoPred, annotation))
                else:
                    answer.addFP(Prediction('FP', topoPred, None))
            else:
                answer.addFP(Prediction('FP', topoPred, None))
        # then the FN
        for topoRef in self.toponymsReferences:
            found = False
            for topoPred in toponymsPredictedWoExcluded:
                if topoRef.getStartOffset() == topoPred.getStartOffset() and topoRef.getEndOffset() == topoPred.getEndOffset():
                    # the predicted toponym has the same boundaries than a toponym annotation in the reference it should be a strict match
                    if topoPred.getText() != topoRef.getText():
                        # the span are identical but the text are not, it can be caused by newline or spaces, I remove all and compare again
                        topopredWoSpace = "".join(re.split(r"\s", topoPred.getText()))
                        toporefWoSpace = "".join(re.split(r"\s", topoRef.getText()))
                        if topopredWoSpace != toporefWoSpace:
                            # apparently not only newline and space, the last case is probaly a bug from Brat which may remove the hyphen like in "Ham-\nburg" (PMC4907427, 41948 41957), the annotation written is "Ham burg"
                            topopredWoSpaceWoHyphen = "".join(re.split("-", topopredWoSpace))
                            toporefWoSpaceWoHyphen = "".join(re.split("-", toporefWoSpace))
                            assert topopredWoSpaceWoHyphen == toporefWoSpaceWoHyphen, "Found a predicted toponym {} and a reference toponym at the same position with different texts {} and {}, should not be check the data...".format(
                                str(topoPred), str(topoRef), topoPred.getText(), topoRef.getText())
                    found = True
                    break
            if not found:
                answer.addFN(Prediction('FN', None, topoRef))

        return answer

    def evalDisambiguationStrictMatching(self, answer):
        """
        Apply a strict matching to compute the Tcd, Tid, Tn given the toponyms references and toponyms predicted
        :param answer: the answer computed for the detection
        :return: an Answer containing the lists of ExcludedToponyms, Tcd, Tid, Tn resulting from the comparison
        """
        # Start computing Tcds and Tids:
        # Tcds correctly identified and disambiguated, so a subset of TPs
        # Tids are correctly identified but incorrectly disambiguated (so a subset of TPs) or FPs
        for tp in answer.getTPs():
            assert tp.value == 'TP', "The prediction in the oracle's answer is not a TP as expected, check the code."
            # for a given TP we just have to check if the geoID predicted is equal to the geoID of the reference
            if tp.topoPred.getGeoID() == tp.topoRef.getGeoID():
                # print("The toponym [{}] is correctly resolved (reference: {})".format(str(tp.topoPred), str(tp.topoRef)))
                answer.addTcd(tp)
            else:
                # print("The toponym [{}] is INCORRECTLY resolved (reference: {})".format(str(tp.topoPred), str(tp.topoRef)))
                answer.addTid(tp)
        # we complete the Tids
        for fp in answer.getFPs():
            assert fp.value == 'FP', "The prediction in the oracle's answer is not a FP as expected, check the code."
            # print("The FP [{}] is added in the Tids".format(str(fp)))
            answer.addTid(fp)
        # and we finish computing Tn
        answer.setTn(len(self.toponymsReferences))
        return answer

    def evalDetectionOverlapMatching(self, toponymsPredictedWoExcluded):
        """
        Apply a partial matching to compute the TPs, FPs, FNs given the toponyms references and toponyms predicted
        :param toponymsPredicted: the list of toponyms predicted by the system to compare against the toponyms of reference
        :return: an Answer containing the lists of ExcludedToponyms, TPs, FPs and FNs resulting from the comparison

        ideally we want a bijection between ref et pred toponyms.
        We implement an overlapping matching where all system's predictions are counted as TPs if they overlap with a least one reference
        possible ill cases 1) Ref: [New York] Pred:[New][York] will be counted as 2 TPs
                        or 2) Ref:[Adelaide],[Australia]; Pred:[Adelaide, Australia] will be counted as 2 TP (even if there is only on predicted toponym, since the toponym predicted overlaps both toponym references they are not FNs by definition of the overlapping metric)
        Note: these cases generate more TPs than there are references/predictions in the articles, but it is the same than strict matching which generate more FPs
        """
        answer = Answer()
        # start with FPs and TPs
        for topoPred in toponymsPredictedWoExcluded:
            # it's an overlapping matching, I start by creating the list of reference toponyms sharing a common position with the prediction
            topoRefHit = set()
            for index in topoPred.getOffsets():
                if index in self.mapIndexesAnnotated:
                    if type(self.mapIndexesAnnotated[index]) == Toponym:
                        topoRefHit.add(self.mapIndexesAnnotated[index])

            if len(topoRefHit) >= 1:  # we found one overlap or exact match between the predicted and a gold toponym
                for topoRef in topoRefHit:  # all are considered TPs
                    # print("TP: pred -> {} for Ref -> {}".format(topoPred, topoRef))
                    answer.addTP(Prediction('TP', topoPred, topoRef))
            else:
                # print("FP: pred -> {}".format(topoPred))
                answer.addFP(Prediction('FP', topoPred, None))

        # then FNs
        for topoRef in self.toponymsReferences:
            found = False
            for topoPred in toponymsPredictedWoExcluded:
                if not ((topoPred.getStartOffset() < topoRef.getStartOffset()) and (
                        topoPred.getEndOffset() < topoRef.getStartOffset()) or
                        (topoRef.getStartOffset() < topoPred.getStartOffset()) and (
                                topoRef.getEndOffset() < topoPred.getStartOffset())):
                    # print("Ref: ref -> {} is found overlapping Pred: -> {}".format(topoRef,topoPred))
                    found = True
                    break
            if not found:
                # print("FN: pred -> {}".format(topoRef))
                answer.addFN(Prediction('FN', None, topoRef))

        return answer

    def evalDisambiguationOverlapMatching(self, answer):
        """
        Apply a strict matching to compute the Tcd, Tid, Tn given the toponyms references and toponyms predicted
        :param answer: the answer computed for the detection
        :return: an Answer containing the lists of ExcludedToponyms, Tcd, Tid, Tn resulting from the comparison
        """
        # Start computing Tcds and Tids:
        # Tcds correctly identified and disambiguated, so a subset of TPs
        # Tids are correctly identified but incorrectly disambiguated (so a subset of TPs) or FPs
        for tp in answer.getTPs():
            assert tp.value == 'TP', "The prediction in the oracle's answer is not a TP as expected, check the code."
            # for a given TP we just have to check if the geoID predicted is equal to the geoID of the reference
            if tp.topoPred.getGeoID() == tp.topoRef.getGeoID():
                # print("The toponym [{}] is correctly resolved (reference: {})".format(str(tp.topoPred), str(tp.topoRef)))
                answer.addTcd(tp)
            else:
                # print("The toponym [{}] is INCORRECTLY resolved (reference: {})".format(str(tp.topoPred), str(tp.topoRef)))
                answer.addTid(tp)
        # we complete the Tids
        for fp in answer.getFPs():
            assert fp.value == 'FP', "The prediction in the oracle's answer is not a FP as expected, check the code."
            # print("The FP [{}] is added in the Tids".format(str(fp)))
            answer.addTid(fp)
        # and we finish computing Tn
        answer.setTn(len(self.toponymsReferences))
        return answer

    def removeToponymsInExcludedSpans(self, toponymsPredicted):
        """
        Given a list of toponyms remove from the list all toponyms that are in the excluded spans
        :return: a list of all toponyms outside the spans excluded form evaluation
        """
        ignoredToponyms = []
        for topoPred in toponymsPredicted:
            if topoPred.getStartOffset() in self.mapIndexesAnnotated:
                # the position has been annotated either as excludedSpan or as toponym
                annotation = self.mapIndexesAnnotated[topoPred.getStartOffset()]
                if type(annotation) == ExcludedSpan:
                    # we check that the toponym is fully included in the excluded span
                    if (annotation.getStartOffset() <= topoPred.getStartOffset()) and (
                            topoPred.getEndOffset() <= annotation.getEndOffset()):
                        log.debug(
                            "Toponym {} has been excluded from evaluation being within an excluded span {}".format(
                                str(topoPred), str(annotation)))
                        ignoredToponyms.append(topoPred)
        return [x for x in toponymsPredicted if x not in ignoredToponyms]


class ToponymEvaluator(object):
    '''
    Main evaluator class for SemEval Task 12.

    The evaluator expects the predictions made for one article in one file. All prediction files should have the extension .ann and should follow the Brat format.
    All prediction files should be placed in one folder, without additional file or sub-folder.
    The evaluator expects the references in the same way, the references of one article in one file and all files in one directory.
    For instance, if the system S resolved the toponyms for the articles a1, a2 and a3, the system should output 3 files a1.ann, a2.ann and a3.ann stored in one folder named, for example, predictions.
    The references for the articles a1, a2, and a3 should be given in 3 files a1.ann, a2.ann, a3.ann and stored in one folder named, for example, references.
    The files in the predictions and references folders should have the same names and no other file or sub-folder should be present in the folders, otherwise an exception is raised.
    '''

    def __init__(self, pathDirPredictions, pathDirReferences):
        '''
        Constructor: parse the annotations files and instantiate the dictionary self.docAnnotations which contains docNumber => {'references' => [ExcludedSpans, Toponyms], 'predictions' => [Toponyms]}
        Create the main object: dict docAnnotations which maps the docname -> {'references' => {'excludedSpans', 'toponyms'}, 'predictions' => {'excludedSpans', 'toponyms'}}
        '''
        self.pathDirPredictions = pathDirPredictions
        self.pathDirReferences = pathDirReferences

        log.debug("Start parsing predictions and references files...")
        references = sorted([os.path.basename(x) for x in glob.glob(self.pathDirReferences + "/*.ann")])
        predictions = sorted([os.path.basename(x) for x in glob.glob(self.pathDirPredictions + "/*.ann")])

        # Sanity check between references and predictions
        assert len(predictions) == len(
            references), "The number of prediction files [{}] is not equal to the number of reference files [{}], check the data.".format(
            len(predictions), len(references))
        for index in range(len(predictions)):
            assert predictions[index] == references[
                index], "The folders of predictions and references do not contain exactly the same files, I found at index {} in the references folder the file {} where I expected the file {} as in the prediction folder.".format(
                index, references[index], predictions[index])

        # Start processing the annotation
        parser = BratSemEvalParser()
        # a Map to store the references and predictions per document
        self.docAnnotations = {}
        for index in range(len(predictions)):
            annotations = {}
            log.debug(os.path.join(self.pathDirReferences, references[index]))
            annotations["references"] = parser.parseAnnotations(os.path.join(self.pathDirReferences, references[index]))
            annotations["predictions"] = parser.parseAnnotations(
                os.path.join(self.pathDirPredictions, predictions[index]))
            # add the pair (doc, annotations (predictions, references))
            self.docAnnotations[references[index]] = annotations
        log.debug("End parsing predictions and references files.")

    def getAnnotations(self):
        """
        :return: the map containing docNumber => {'references' => {'excludedSpans', 'toponyms'}, 'predictions' => {'excludedSpans', 'toponyms'}}
        created by the parser during the instantiation of the Evaluator
        """
        return self.docAnnotations

    def __mean__(self, values):
        """
        Compute the simple mean of a list of values, the list should not be empty
        """
        assert len(values) > 0, "the list of values should not be empty to compute a mean"
        summ = 0.0
        for value in values:
            summ = summ + value
        return (float(summ) / float(len(values)))

    def __getPRF1__(self, oracleAnswers):
        """
        Compute the macro/micro precision, recall and F1 scores for the given oracle answers (strict or partial)
        :param oracleAnswers: a list of Answer containing Excluded Toponyms, TPs, FPs, FNs
        :return: a dict {'microP', 'microR', 'microF1', 'macroP', 'macroR', 'macroF1'}
        """

        def __getDetectionPrecision__(TPs, FPs):
            """
            :param TPs: int number of TPs
            :param FPs: int number of FPs
            :return: float
            """
            if TPs == 0 and FPs == 0:
                return 1.0
            return (float(TPs) / (float(TPs) + float(FPs)))

        def __getDetectionRecall__(TPs, FNs):
            """
            :param TPs: int number of TPs
            :param FNs: int number of FNs
            :return: float
            """
            if TPs == 0 and FNs == 0:
                return 1.0
            return (float(TPs) / (float(TPs) + float(FNs)))

        def __getDetectionF1__(Precision, Recall):
            """
            :param Precision: float number of TPs
            :param Recall: float number of FPs
            :return: float
            """
            if Precision == 0.0 and Recall == 0.0:
                return 0.0
            return (2 * ((Precision * Recall) / (Precision + Recall)))

        # We have the TPs, FPs, FNs we compute the Precision and Recall
        # Gate, https://gate.ac.uk/sale/tao/splitch10.html
        # Micro averaging essentially treats the corpus as one large document. Correct, spurious and missing counts span the entire corpus, and precision, recall and f-measure are calculated accordingly.
        micro = {'TPs': 0, 'FPs': 0, 'FNs': 0}
        # Gate, https://gate.ac.uk/sale/tao/splitch10.html
        # Macro averaging calculates precision, recall and f-measure on a per document basis, and then averages the results.
        macro = {'Precisions': [], 'Recalls': [], 'F1s': []}
        for doc, oracleAnswer in oracleAnswers.items():
            micro['TPs'] = micro['TPs'] + len(oracleAnswer.getTPs())
            micro['FPs'] = micro['FPs'] + len(oracleAnswer.getFPs())
            micro['FNs'] = micro['FNs'] + len(oracleAnswer.getFNs())

            macroPrecision = __getDetectionPrecision__(len(oracleAnswer.getTPs()), len(oracleAnswer.getFPs()))
            macro['Precisions'].append(macroPrecision)
            macroRecall = __getDetectionRecall__(len(oracleAnswer.getTPs()), len(oracleAnswer.getFNs()))
            macro['Recalls'].append(macroRecall)
            macro['F1s'].append(__getDetectionF1__(macroPrecision, macroRecall))

        results = {}
        results['microP'] = __getDetectionPrecision__(micro['TPs'], micro['FPs'])
        results['microR'] = __getDetectionPrecision__(micro['TPs'], micro['FNs'])
        results['microF1'] = __getDetectionF1__(results['microP'], results['microR'])

        results['macroP'] = self.__mean__(macro['Precisions'])
        results['macroR'] = self.__mean__(macro['Recalls'])
        results['macroF1'] = __getDetectionF1__(results['macroP'], results['macroR'])

        return results

    def __getPdsRdsF1ds__(self, oracleAnswers):
        """
        Compute the macro/micro Pds, Rds and F1ds scores for the given oracle answers (strict or partial)
        :param oracleAnswers: a list of Answer containing Tcds, Tids, Tn
        :return: a dict {'microPds', 'microRds', 'microF1ds', 'macroPds', 'macroRds', 'macroF1ds'}
        """

        def __getPds__(Tcd, Tid):
            """
            :param Tcd: int number of Tcds
            :param Tid: int number of Tids
            :return: float
            """
            if Tcd == 0 and Tid == 0:  # no toponym in the article, therefore 1.0 precision
                return 1.0
            return (float(Tcd) / (float(Tcd) + float(Tid)))

        def __getRds__(Tcd, Tn):
            """
            :param Tcd: int number of Tcds
            :param Tn: int number of Tn
            :return: float
            """
            if Tcd == 0 and Tn == 0:  # no toponym in the article, 1.0 recall...
                return 1.0
            assert Tn != 0, "When Tn=0, Tcd must be ==0 and we should never raise this exception, check the code."
            return (float(Tcd) / float(Tn))

        def __getF1ds__(Pcd, Rcd):
            """
            :param Pcd: float the Precision cd computed
            :param Rcd: float the Recall cd computed
            :return: float
            """
            if Pcd == 0.0 and Rcd == 0.0:
                return 0.0
            return (2 * ((Pcd * Rcd) / (Pcd + Rcd)))

        # We have the TPs, FPs, FNs we compute the Precision and Recall
        # Gate, https://gate.ac.uk/sale/tao/splitch10.html
        # Micro averaging essentially treats the corpus as one large document. Correct, spurious and missing counts span the entire corpus, and precision, recall and f-measure are calculated accordingly.
        micro = {'Tcds': 0, 'Tids': 0, 'Tns': 0}
        # Gate, https://gate.ac.uk/sale/tao/splitch10.html
        # Macro averaging calculates precision, recall and f-measure on a per document basis, and then averages the results.
        macro = {'Pdss': [], 'Rdss': [], 'F1dss': []}
        for doc, oracleAnswer in oracleAnswers.items():
            # print("Tcds:{} - Tids:{}".format(len(oracleAnswer.getTcds()), len(oracleAnswer.getTids())))

            micro['Tcds'] = micro['Tcds'] + len(oracleAnswer.getTcds())
            micro['Tids'] = micro['Tids'] + len(oracleAnswer.getTids())
            micro['Tns'] = micro['Tns'] + oracleAnswer.getTn()

            macroPds = __getPds__(len(oracleAnswer.getTcds()), len(oracleAnswer.getTids()))
            macro['Pdss'].append(macroPds)
            macroRds = __getRds__(len(oracleAnswer.getTcds()), oracleAnswer.getTn())
            macro['Rdss'].append(macroRds)
            macro['F1dss'].append(__getF1ds__(macroPds, macroRds))

        #             print("{}".format(macroPds))

        results = {}
        results['microPds'] = __getPds__(micro['Tcds'], micro['Tids'])
        results['microRds'] = __getRds__(micro['Tcds'], micro['Tns'])
        results['microF1ds'] = __getF1ds__(results['microPds'], results['microRds'])

        results['macroPds'] = self.__mean__(macro['Pdss'])
        results['macroRds'] = self.__mean__(macro['Rdss'])
        results['macroF1ds'] = __getF1ds__(results['macroPds'], results['macroRds'])

        return results

    def evalDetection(self, outFile):
        """
        Run the evaluation of the Detection skill only of the system on the predicted toponyms
        Write the scores in the file given in parameter
        """
        log.info("Evaluate the detection...")
        # All documents (reference, predicted) have been parsed, we loop on each and use the oracle to get FPs, TPs, FNs given the predictions
        oracleAnswersStrict = {}
        oracleAnswersOverlap = {}
        for doc, annotations in sorted(self.getAnnotations().items()):
            log.debug("Evaluate Doc: {}".format(doc))
            oracle = Oracle(annotations['references'])
            # start by removing the predictions made on the excluded spans
            toponymsPredictedWoExcluded = oracle.removeToponymsInExcludedSpans(annotations['predictions']['toponyms'])
            oracleAnswersStrict[doc] = oracle.evalDetectionStrictMatching(toponymsPredictedWoExcluded)
            oracleAnswersOverlap[doc] = oracle.evalDetectionOverlapMatching(toponymsPredictedWoExcluded)
            oracleAnswersStrict[doc].setExcludedToponyms(
                [x for x in annotations['predictions']['toponyms'] if x not in toponymsPredictedWoExcluded])
            oracleAnswersOverlap[doc].setExcludedToponyms(
                [x for x in annotations['predictions']['toponyms'] if x not in toponymsPredictedWoExcluded])

        #             print(str(oracleAnswersStrict[doc]))
        #             print(oracleAnswersOverlap[doc])
        log.info("Detection evaluated.")
        log.info("Start writing scores...")
        outFile.write("#Detection Strict:\n")
        self.__writeDetectionScores__(outFile, oracleAnswersStrict, 'strict')
        outFile.write("\n")
        outFile.write("#Detection Overlap:\n")
        self.__writeDetectionScores__(outFile, oracleAnswersOverlap, 'overlap')
        outFile.write("\n")
        log.info("Scores written. END")

    def evalDisambiguation(self, outFile):
        """
        Run the evaluation of the Disambiguation performance of the system, the toponyms are assumed to be given to the system
        Write the scores in the file given in parameter
        """
        log.info("Evaluate the disambiguation...")
        # All documents (reference, predicted) have been parsed, we loop on each and use the oracle to get FPs, TPs, FNs given the predictions
        oracleAnswersStrict = {}
        for doc, annotations in sorted(self.getAnnotations().items()):
            log.debug("Evaluate Doc: {}".format(doc))

            oracle = Oracle(annotations['references'])
            # start by removing the predictions made on the excluded spans
            toponymsPredictedWoExcluded = oracle.removeToponymsInExcludedSpans(annotations['predictions']['toponyms'])
            # we compute the FPs, TPs, FNs needed
            oracleAnswersStrict[doc] = oracle.evalDetectionStrictMatching(toponymsPredictedWoExcluded)
            oracleAnswersStrict[doc].setExcludedToponyms(
                [x for x in annotations['predictions']['toponyms'] if x not in toponymsPredictedWoExcluded])
            assert len(oracleAnswersStrict[doc].getFNs()) == 0 and len(oracleAnswersStrict[
                                                                           doc].getFPs()) == 0, "I found {} FNs and {} FPs which should both be ==0 since we are in desambiguation only, please check the data.".format(
                len(oracleAnswersStrict[doc].getFNs()), len(oracleAnswersStrict[doc].getFPs()))
            # the update with the Tcds, Tids, Tns
            oracleAnswersStrict[doc] = oracle.evalDisambiguationStrictMatching(oracleAnswersStrict[doc])

        #             print(str(oracleAnswersStrict[doc]))
        log.info("Disambiguation evaluated.")
        log.info("Start writing scores...")
        outFile.write("#Disambiguation Strict:\n")
        self.__writeDisambiguationScores__(outFile, oracleAnswersStrict, 'strict')
        outFile.write("\n")
        log.info("Scores written. END")

    def evalResolution(self, outFile):
        """
        Evaluate the performance of the system on the end-to-end task, i.e. 1. detection followed by 2. disambiguation on the toponyms detected during 1.
        Write the scores in the file given in parameter
        """
        log.info("Evaluate the resolution...")
        oracleAnswersStrict = {}
        oracleAnswersOverlap = {}
        for doc, annotations in sorted(self.getAnnotations().items()):
            log.debug("Evaluate Doc: {}".format(doc))
            oracle = Oracle(annotations['references'])
            # start by removing the predictions made on the excluded spans
            toponymsPredictedWoExcluded = oracle.removeToponymsInExcludedSpans(annotations['predictions']['toponyms'])
            # we compute the FPs, TPs, FNs needed
            oracleAnswersStrict[doc] = oracle.evalDetectionStrictMatching(toponymsPredictedWoExcluded)
            oracleAnswersOverlap[doc] = oracle.evalDetectionOverlapMatching(toponymsPredictedWoExcluded)
            # we add the toponyms excluded to the oracle answer
            oracleAnswersStrict[doc].setExcludedToponyms(
                [x for x in annotations['predictions']['toponyms'] if x not in toponymsPredictedWoExcluded])
            oracleAnswersOverlap[doc].setExcludedToponyms(
                [x for x in annotations['predictions']['toponyms'] if x not in toponymsPredictedWoExcluded])
            # then we compute the Tcds, Tids, Tns
            oracleAnswersStrict[doc] = oracle.evalDisambiguationStrictMatching(oracleAnswersStrict[doc])
            oracleAnswersOverlap[doc] = oracle.evalDisambiguationOverlapMatching(oracleAnswersOverlap[doc])

        #             print(str(oracleAnswersStrict[doc]))
        #             print(oracleAnswersOverlap[doc])

        log.info("Resolution evaluated.")
        log.info("Start writing scores...")
        outFile.write("#Detection Strict:\n")
        self.__writeDetectionScores__(outFile, oracleAnswersStrict, 'strict')
        outFile.write("\n")
        outFile.write("#Detection Overlap:\n")
        self.__writeDetectionScores__(outFile, oracleAnswersOverlap, 'overlap')
        outFile.write("\n")
        outFile.write("#Resolution Strict:\n")
        self.__writeDisambiguationScores__(outFile, oracleAnswersStrict, 'strict')
        outFile.write("\n")
        outFile.write("#Resolution Overlap:\n")
        self.__writeDisambiguationScores__(outFile, oracleAnswersOverlap, 'overlap')
        outFile.write("\n")
        log.info("Scores written.")

    def __writeDetectionScores__(self, outFile, oracleAnswers, mode):
        """
        Write the scores of the detection in the output file given
        :param outFile: the file to write the scores
        :param oracleAnswers: the answer of the oracle needed to compute the score
        :param mode: the mode strict or overlap to be added
        """
        results = self.__getPRF1__(oracleAnswers)
        outFile.write(mode)
        outFile.write('_macroP:')
        outFile.write(str(results['macroP']))
        outFile.write('\n')
        outFile.write(mode)
        outFile.write('_macroR:')
        outFile.write(str(results['macroR']))
        outFile.write('\n')
        outFile.write(mode)
        outFile.write('_macroF1:')
        outFile.write(str(results['macroF1']))
        outFile.write('\n')
        outFile.write(mode)
        outFile.write('_microP:')
        outFile.write(str(results['microP']))
        outFile.write('\n')
        outFile.write(mode)
        outFile.write('_microR:')
        outFile.write(str(results['microR']))
        outFile.write('\n')
        outFile.write(mode)
        outFile.write('_microF1:')
        outFile.write(str(results['microF1']))
        outFile.write('\n')

    def __writeDisambiguationScores__(self, outFile, oracleAnswers, mode):
        """
        Write the scores of the desambiguation in the output file given
        :param outFile: the file to write the scores
        :param oracleAnswers: the answer of the oracle needed to compute the score
        :param mode: the mode strict or overlap to be added
        """
        results = self.__getPdsRdsF1ds__(oracleAnswers)
        outFile.write(mode)
        outFile.write('_macroPds:')
        outFile.write(str(results['macroPds']))
        outFile.write('\n')
        outFile.write(mode)
        outFile.write('_macroRds:')
        outFile.write(str(results['macroRds']))
        outFile.write('\n')
        outFile.write(mode)
        outFile.write('_macroF1ds:')
        outFile.write(str(results['macroF1ds']))
        outFile.write('\n')
        outFile.write(mode)
        outFile.write('_microPds:')
        outFile.write(str(results['microPds']))
        outFile.write('\n')
        outFile.write(mode)
        outFile.write('_microRds:')
        outFile.write(str(results['microRds']))
        outFile.write('\n')
        outFile.write(mode)
        outFile.write('_microF1ds:')
        outFile.write(str(results['microF1ds']))
        outFile.write('\n')


if __name__ == '__main__':
    LOG_FILENAME = 'E:\\faculty\\an3\\sem2\\ln\\gitProject\\evaluator\\ToponymDefaultDetection.log'
    # logging.basicConfig(filename=LOG_FILENAME,level=logging.DEBUG, format='%(asctime)s %(name)-12s %(levelname)-8s %(message)s')
    log.basicConfig(level=log.DEBUG,
                    format='%(asctime)s %(name)-12s %(levelname)-8s %(message)s',
                    handlers=[log.StreamHandler(sys.stdout), log.FileHandler(LOG_FILENAME)])

    [_, input_dir, output_dir, evaluation_mode] = sys.argv
    log.info('Start Evaluation in mode {}'.format(evaluation_mode))
    print('Start Evaluation in mode {}'.format(evaluation_mode))
    if evaluation_mode == 'Detection':
        pathDirPredictions = os.path.join(input_dir, 'res')
        print(pathDirPredictions)
        pathDirReferences = os.path.join(input_dir, 'ref/detection')
        print(pathDirReferences)
    elif evaluation_mode == 'Disambiguation':
        pathDirPredictions = os.path.join(input_dir, 'res')
        print(pathDirPredictions)
        pathDirReferences = os.path.join(input_dir, 'ref/disambiguation')
        print(pathDirReferences)
    elif evaluation_mode == 'Resolution':
        pathDirPredictions = os.path.join(input_dir, 'res')
        print(pathDirPredictions)
        pathDirReferences = os.path.join(input_dir, 'ref/resolution')
        print(pathDirReferences)
    else:
        log.fatal(
            "Unknown evaluation parameter received: [{}]. Expecting [Detection, Disambiguation, Resolution]".format(
                evaluation_mode))
        raise Exception(
            "Unknown evaluation parameter received: [{}]. Expecting [Detection, Disambiguation, Resolution]".format(
                evaluation_mode))

    #     #local path, to comment
    #     if evaluation_mode=='Detection':
    #         pathDirPredictions = "/home/dweissen/tal/Ecrit/Workshops/Accepted/Semeval19/SemEvalCodalab/testData/detection/submission/"
    #         #pathDirReferences = "/home/dweissen/tal/Ecrit/Workshops/Accepted/Semeval19/SemEvalCodalab/testData/detection/testInput/dev_data/"
    #         pathDirReferences = "/home/dweissen/tal/Ecrit/Workshops/Accepted/Semeval19/SemEvalCodalab/testData/detection/reference/"
    #     elif evaluation_mode=='Disambiguation':
    #         pathDirPredictions = "/home/dweissen/tal/Ecrit/Workshops/Accepted/Semeval19/SemEvalCodalab/testData/disambiguation/submission/"
    #         #pathDirReferences = "/home/dweissen/tal/Ecrit/Workshops/Accepted/Semeval19/SemEvalCodalab/testData/disambiguation/testInput/dev_data/"
    #         pathDirReferences = "/home/dweissen/tal/Ecrit/Workshops/Accepted/Semeval19/SemEvalCodalab/testData/disambiguation/reference/"
    #     elif evaluation_mode=='Resolution':
    #         pathDirPredictions = "/home/dweissen/tal/Ecrit/Workshops/Accepted/Semeval19/SemEvalCodalab/testData/resolution/submission/"
    #         #pathDirReferences = "/home/dweissen/tal/Ecrit/Workshops/Accepted/Semeval19/SemEvalCodalab/testData/resolution/testInput/dev_data/"
    #         pathDirReferences = "/home/dweissen/tal/Ecrit/Workshops/Accepted/Semeval19/SemEvalCodalab/testData/resolution/reference/"

    # the scores for the leaderboard must be in a file named "scores.txt"
    with open(os.path.join(output_dir, 'scores.txt'), 'w') as output_file:

        evalTopo = ToponymEvaluator(pathDirPredictions, pathDirReferences)
        if evaluation_mode == 'Detection':
            evalTopo.evalDetection(output_file)
        elif evaluation_mode == 'Disambiguation':
            evalTopo.evalDisambiguation(output_file)
        elif evaluation_mode == 'Resolution':
            evalTopo.evalResolution(output_file)
        else:
            log.fatal(
                "Unknown evaluation parameter received: [{}]. Expecting [Detection, Disambiguation, Resolution]".format(
                    evaluation_mode))
            raise Exception(
                "Unknown evaluation parameter received: [{}]. Expecting [Detection, Disambiguation, Resolution]".format(
                    evaluation_mode))
