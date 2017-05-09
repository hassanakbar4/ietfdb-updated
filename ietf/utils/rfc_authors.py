#!/usr/bin/python

# DANGER WILL ROBINSON
# This code was used in the construction of person migrations 0016 through 0019 and doc migration 0029
# The original intent was to provide a utility that could be run periodically, but the need for manual
# inspection of the results was too great. It is here as a _starting point_ for future exploration of
# updating rfc documentauthor sets. Be careful to check that assumptions haven't changed in the interim.

import os, sys
import django
import argparse
from collections import namedtuple
import subprocess
from tempfile import mkstemp

basedir = os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)), '../..'))
sys.path.insert(0, basedir)
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "ietf.settings")

django.setup()

from ietf.person.models import Email, Person
from ietf.doc.models import Document
from ietf import settings

import debug

# This is a snapshot dump from the RFC Editor in late April 2017
rfced_data = """RFC1          ||      S. Crocker         ||         
  RFC2          ||       B. Duvall         ||         
  RFC3          ||       S.D. Crocker         ||         
  RFC4          ||       E.B. Shapiro         ||         
  RFC5          ||      J. Rulifson         ||       
  RFC6          ||       S.D. Crocker         ||         
  RFC7          ||       G. Deloche         ||         
  RFC8          ||      G. Deloche         ||       
  RFC9          ||      G. Deloche         ||       
  RFC10          ||       S.D. Crocker         ||         
  RFC11          ||      G. Deloche         ||       
  RFC12          ||       M. Wingfield         ||         
  RFC13          ||       V. Cerf         ||         
  RFC14          ||               ||         
  RFC15          ||       C.S. Carr         ||         
  RFC16          ||       S. Crocker         ||         
  RFC17          ||       J.E. Kreznar         ||         
  RFC18          ||       V. Cerf         ||         
  RFC19          ||       J.E. Kreznar         ||         
  RFC20          ||      V.G. Cerf         ||       
  RFC21          ||       V.G. Cerf         ||         
  RFC22          ||       V.G. Cerf         ||         
  RFC23          ||       G. Gregg         ||         
  RFC24          ||       S.D. Crocker         ||         
  RFC25          ||       S.D. Crocker         ||         
  RFC26          ||               ||         
  RFC27          ||       S.D. Crocker         ||         
  RFC28          ||       W.K. English         ||         
  RFC29          ||       R.E. Kahn         ||         
  RFC30          ||       S.D. Crocker         ||         
  RFC31          ||      D. Bobrow, W.R. Sutherland         ||         
  RFC32          ||       J. Cole         ||         
  RFC33          ||       S.D. Crocker         ||         
  RFC34          ||       W.K. English         ||         
  RFC35          ||       S.D. Crocker         ||         
  RFC36          ||       S.D. Crocker         ||         
  RFC37          ||       S.D. Crocker         ||         
  RFC38          ||       S.M. Wolfe         ||         
  RFC39          ||       E. Harslem, J.F. Heafner         ||         
  RFC40          ||       E. Harslem, J.F. Heafner         ||         
  RFC41          ||       J.T. Melvin         ||         
  RFC42          ||       E. Ancona         ||         
  RFC43          ||       A.G. Nemeth         ||         
  RFC44          ||       A. Shoshani, R. Long, A. Landsberg         ||         
  RFC45          ||       J. Postel, S.D. Crocker         ||         
  RFC46          ||       E. Meyer         ||         
  RFC47          ||       J. Postel, S. Crocker         ||         
  RFC48          ||       J. Postel, S.D. Crocker         ||         
  RFC49          ||       E. Meyer         ||         
  RFC50          ||       E. Harslen, J. Heafner         ||         
  RFC51          ||      M. Elie         ||       
  RFC52          ||       J. Postel, S.D. Crocker         ||         
  RFC53          ||       S.D. Crocker         ||         
  RFC54          ||       S.D. Crocker, J. Postel, J. Newkirk, M. Kraley         ||         
  RFC55          ||       J. Newkirk, M. Kraley, J. Postel, S.D. Crocker         ||         
  RFC56          ||       E. Belove, D. Black, R. Flegal, L.G. Farquar         ||         
  RFC57          ||       M. Kraley, J. Newkirk         ||         
  RFC58          ||       T.P. Skinner         ||         
  RFC59          ||       E. Meyer         ||         
  RFC60          ||      R. Kalin         ||       
  RFC61          ||       D.C. Walden         ||         
  RFC62          ||       D.C. Walden         ||         
  RFC63          ||       V.G. Cerf         ||         
  RFC64          ||       M. Elie         ||         
  RFC65          ||       D.C. Walden         ||         
  RFC66          ||       S.D. Crocker         ||         
  RFC67          ||       W.R. Crowther         ||         
  RFC68          ||       M. Elie         ||         
  RFC69          ||       A.K. Bhushan         ||         
  RFC70          ||       S.D. Crocker         ||         
  RFC71          ||       T. Schipper         ||         
  RFC72          ||       R.D. Bressler         ||         
  RFC73          ||       S.D. Crocker         ||         
  RFC74          ||      J.E. White         ||       
  RFC75          ||       S.D. Crocker         ||         
  RFC76          ||       J. Bouknight, J. Madden, G.R. Grossman         ||         
  RFC77          ||       J. Postel         ||         
  RFC78          ||       E. Harslem, J.F. Heafner, J.E. White         ||         
  RFC79          ||       E. Meyer         ||         
  RFC80          ||       E. Harslem, J.F. Heafner         ||         
  RFC81          ||       J. Bouknight         ||         
  RFC82          ||       E. Meyer         ||         
  RFC83          ||       R.H. Anderson, E. Harslem, J.F. Heafner         ||         
  RFC84          ||       J.B. North         ||         
  RFC85          ||       S.D. Crocker         ||         
  RFC86          ||      S.D. Crocker         ||       
  RFC87          ||       A. Vezza         ||         
  RFC88          ||       R.T. Braden, S.M. Wolfe         ||         
  RFC89          ||       R.M. Metcalfe         ||         
  RFC90          ||       R.T. Braden         ||         
  RFC91          ||       G.H. Mealy         ||         
  RFC92          ||               ||         
  RFC93          ||       A.M. McKenzie         ||         
  RFC94          ||       E. Harslem, J.F. Heafner         ||         
  RFC95          ||      S. Crocker         ||       
  RFC96          ||       R.W. Watson         ||         
  RFC97          ||      J.T. Melvin, R.W. Watson         ||       
  RFC98          ||       E. Meyer, T. Skinner         ||         
  RFC99          ||       P.M. Karp         ||         
  RFC100          ||       P.M. Karp         ||         
  RFC101          ||       R.W. Watson         ||         
  RFC102          ||       S.D. Crocker         ||         
  RFC103          ||       R.B. Kalin         ||         
  RFC104          ||       J.B. Postel, S.D. Crocker         ||         
  RFC105          ||       J.E. White         ||         
  RFC106          ||       T.C. O'Sullivan         ||         
  RFC107          ||       R.D. Bressler, S.D. Crocker, W.R. Crowther, G.R. Grossman, R.S. Tomlinson, J.E. White         ||         
  RFC108          ||       R.W. Watson         ||         
  RFC109          ||      J. Winett         ||       
  RFC110          ||      J. Winett         ||       
  RFC111          ||       S.D. Crocker         ||         
  RFC112          ||      T.C. O'Sullivan         ||       
  RFC113          ||       E. Harslem, J.F. Heafner, J.E. White         ||         
  RFC114          ||       A.K. Bhushan         ||         
  RFC115          ||       R.W. Watson, J.B. North         ||         
  RFC116          ||       S.D. Crocker         ||         
  RFC117          ||       J. Wong         ||         
  RFC118          ||       R.W. Watson         ||         
  RFC119          ||      M. Krilanovich         ||       
  RFC120          ||       M. Krilanovich         ||         
  RFC121          ||       M. Krilanovich         ||         
  RFC122          ||       J.E. White         ||         
  RFC123          ||       S.D. Crocker         ||         
  RFC124          ||       J.T. Melvin         ||         
  RFC125          ||       J. McConnell         ||         
  RFC126          ||       J. McConnell         ||         
  RFC127          ||       J. Postel         ||         
  RFC128          ||       J. Postel         ||         
  RFC129          ||       E. Harslem, J. Heafner, E. Meyer         ||         
  RFC130          ||       J.F. Heafner         ||         
  RFC131          ||       E. Harslem, J.F. Heafner         ||         
  RFC132          ||       J.E. White         ||         
  RFC133          ||       R.L. Sunberg         ||         
  RFC134          ||       A. Vezza         ||         
  RFC135          ||       W. Hathaway         ||         
  RFC136          ||       R.E. Kahn         ||         
  RFC137          ||       T.C. O'Sullivan         ||         
  RFC138          ||       R.H. Anderson, V.G. Cerf, E. Harslem, J.F. Heafner, J. Madden, R.M. Metcalfe, A. Shoshani, J.E. White, D.C.M. Wood         ||         
  RFC139          ||       T.C. O'Sullivan         ||         
  RFC140          ||       S.D. Crocker         ||         
  RFC141          ||       E. Harslem, J.F. Heafner         ||         
  RFC142          ||       C. Kline, J. Wong         ||         
  RFC143          ||       W. Naylor, J. Wong, C. Kline, J. Postel         ||         
  RFC144          ||       A. Shoshani         ||         
  RFC145          ||       J. Postel         ||         
  RFC146          ||       P.M. Karp, D.B. McKay, D.C.M. Wood         ||         
  RFC147          ||       J.M. Winett         ||         
  RFC148          ||       A.K. Bhushan         ||         
  RFC149          ||       S.D. Crocker         ||         
  RFC150          ||       R.B. Kalin         ||         
  RFC151          ||       A. Shoshani         ||         
  RFC152          ||       M. Wilber         ||         
  RFC153          ||       J.T. Melvin, R.W. Watson         ||         
  RFC154          ||       S.D. Crocker         ||         
  RFC155          ||       J.B. North         ||         
  RFC156          ||       J. Bouknight         ||         
  RFC157          ||       V.G. Cerf         ||         
  RFC158          ||      T.C. O'Sullivan         ||       
  RFC159          ||               ||         
  RFC160          ||       Network Information Center. Stanford Research Institute         ||         
  RFC161          ||       A. Shoshani         ||         
  RFC162          ||       M. Kampe         ||         
  RFC163          ||       V.G. Cerf         ||         
  RFC164          ||       J.F. Heafner         ||         
  RFC165          ||      J. Postel         ||       
  RFC166          ||       R.H. Anderson, V.G. Cerf, E. Harslem, J.F. Heafner, J. Madden, R.M. Metcalfe, A. Shoshani, J.E. White, D.C.M. Wood         ||         
  RFC167          ||       A.K. Bhushan, R.M. Metcalfe, J.M. Winett         ||         
  RFC168          ||       J.B. North         ||         
  RFC169          ||      S.D. Crocker         ||       
  RFC170          ||       Network Information Center. Stanford Research Institute         ||         
  RFC171          ||       A. Bhushan, B. Braden, W. Crowther, E. Harslem, J. Heafner, A. McKenize, J. Melvin, B. Sundberg, D. Watson, J. White         ||         
  RFC172          ||       A. Bhushan, B. Braden, W. Crowther, E. Harslem, J. Heafner, A. McKenzie, J. Melvin, B. Sundberg, D. Watson, J. White         ||         
  RFC173          ||       P.M. Karp, D.B. McKay         ||         
  RFC174          ||       J. Postel, V.G. Cerf         ||         
  RFC175          ||       E. Harslem, J.F. Heafner         ||         
  RFC176          ||       A.K. Bhushan, R. Kanodia, R.M. Metcalfe, J. Postel         ||         
  RFC177          ||       J. McConnell         ||         
  RFC178          ||       I.W. Cotton         ||         
  RFC179          ||       A.M. McKenzie         ||         
  RFC180          ||       A.M. McKenzie         ||         
  RFC181          ||       J. McConnell         ||         
  RFC182          ||       J.B. North         ||         
  RFC183          ||      J.M. Winett         ||       
  RFC184          ||       K.C. Kelley         ||         
  RFC185          ||       J.B. North         ||         
  RFC186          ||       J.C. Michener         ||         
  RFC187          ||       D.B. McKay, D.P. Karp         ||         
  RFC188          ||       P.M. Karp, D.B. McKay         ||         
  RFC189          ||       R.T. Braden         ||         
  RFC190          ||       L.P. Deutsch         ||         
  RFC191          ||       C.H. Irby         ||         
  RFC192          ||       R.W. Watson         ||         
  RFC193          ||       E. Harslem, J.F. Heafner         ||         
  RFC194          ||       V. Cerf, E. Harslem, J. Heafner, B. Metcalfe, J. White         ||         
  RFC195          ||       G.H. Mealy         ||         
  RFC196          ||       R.W. Watson         ||         
  RFC197          ||       A. Shoshani, E. Harslem         ||         
  RFC198          ||       J.F. Heafner         ||         
  RFC199          ||      T. Williams         ||       
  RFC200          ||       J.B. North         ||         
  RFC201          ||               ||         
  RFC202          ||       S.M. Wolfe, J. Postel         ||         
  RFC203          ||       R.B. Kalin         ||         
  RFC204          ||       J. Postel         ||         
  RFC205          ||       R.T. Braden         ||         
  RFC206          ||      J. White         ||       
  RFC207          ||       A. Vezza         ||         
  RFC208          ||       A.M. McKenzie         ||         
  RFC209          ||       B. Cosell         ||         
  RFC210          ||       W. Conrad         ||         
  RFC211          ||      J.B. North         ||       
  RFC212          ||       Information Sciences Institute University of Southern California         ||         
  RFC213          ||       B. Cosell         ||         
  RFC214          ||       E. Harslem         ||         
  RFC215          ||       A.M. McKenzie         ||         
  RFC216          ||      J.E. White         ||       
  RFC217          ||       J.E. White         ||         
  RFC218          ||       B. Cosell         ||         
  RFC219          ||       R. Winter         ||         
  RFC220          ||               ||         
  RFC221          ||       R.W. Watson         ||         
  RFC222          ||       R.M. Metcalfe         ||         
  RFC223          ||       J.T. Melvin, R.W. Watson         ||         
  RFC224          ||       A.M. McKenzie         ||         
  RFC225          ||       E. Harslem, R. Stoughton         ||         
  RFC226          ||       P.M. Karp         ||         
  RFC227          ||       J.F. Heafner, E. Harslem         ||         
  RFC228          ||       D.C. Walden         ||         
  RFC229          ||       J. Postel         ||         
  RFC230          ||       T. Pyke         ||         
  RFC231          ||       J.F. Heafner, E. Harslem         ||         
  RFC232          ||       A. Vezza         ||         
  RFC233          ||       A. Bhushan, R. Metcalfe         ||         
  RFC234          ||       A. Vezza         ||         
  RFC235          ||       E. Westheimer         ||         
  RFC236          ||       J. Postel         ||         
  RFC237          ||       R.W. Watson         ||         
  RFC238          ||       R.T. Braden         ||         
  RFC239          ||       R.T. Braden         ||         
  RFC240          ||       A.M. McKenzie         ||         
  RFC241          ||       A.M. McKenzie         ||         
  RFC242          ||       L. Haibt, A.P. Mullery         ||         
  RFC243          ||       A.P. Mullery         ||         
  RFC244          ||               ||         
  RFC245          ||       C. Falls         ||         
  RFC246          ||       A. Vezza         ||         
  RFC247          ||       P.M. Karp         ||         
  RFC248          ||               ||         
  RFC249          ||       R.F. Borelli         ||         
  RFC250          ||       H. Brodie         ||         
  RFC251          ||       D. Stern         ||         
  RFC252          ||       E. Westheimer         ||         
  RFC253          ||       J.A. Moorer         ||         
  RFC254          ||      A. Bhushan         ||       
  RFC255          ||       E. Westheimer         ||         
  RFC256          ||      B. Cosell         ||       
  RFC257          ||               ||         
  RFC258          ||               ||         
  RFC259          ||               ||         
  RFC260          ||               ||         
  RFC261          ||               ||         
  RFC262          ||               ||         
  RFC263          ||       A.M. McKenzie         ||         
  RFC264          ||       A. Bhushan, B. Braden, W. Crowther, E. Harslem, J. Heafner, A. McKenize, B. Sundberg, D. Watson, J. White         ||         
  RFC265          ||       A. Bhushan, B. Braden, W. Crowther, E. Harslem, J. Heafner, A. McKenzie, J. Melvin, B. Sundberg, D. Watson, J. White         ||         
  RFC266          ||       E. Westheimer         ||         
  RFC267          ||       E. Westheimer         ||         
  RFC268          ||       J. Postel         ||         
  RFC269          ||       H. Brodie         ||         
  RFC270          ||       A.M. McKenzie         ||         
  RFC271          ||       B. Cosell         ||         
  RFC272          ||               ||         
  RFC273          ||       R.W. Watson         ||         
  RFC274          ||       E. Forman         ||         
  RFC275          ||               ||         
  RFC276          ||       R.W. Watson         ||         
  RFC277          ||               ||         
  RFC278          ||       A.K. Bhushan, R.T. Braden, E. Harslem, J.F. Heafner, A.M. McKenzie, J.T. Melvin, R.L. Sundberg, R.W. Watson, J.E. White         ||         
  RFC279          ||               ||         
  RFC280          ||       R.W. Watson         ||         
  RFC281          ||       A.M. McKenzie         ||         
  RFC282          ||       M.A. Padlipsky         ||         
  RFC283          ||       R.T. Braden         ||         
  RFC284          ||               ||         
  RFC285          ||       D. Huff         ||         
  RFC286          ||       E. Forman         ||         
  RFC287          ||       E. Westheimer         ||         
  RFC288          ||       E. Westheimer         ||         
  RFC289          ||       R.W. Watson         ||         
  RFC290          ||       A.P. Mullery         ||         
  RFC291          ||       D.B. McKay         ||         
  RFC292          ||      J.C. Michener, I.W. Cotton, K.C. Kelley, D.E. Liddle, E. Meyer         ||       
  RFC293          ||       E. Westheimer         ||         
  RFC294          ||       A.K. Bhushan         ||         
  RFC295          ||       J. Postel         ||         
  RFC296          ||      D.E. Liddle         ||       
  RFC297          ||       D.C. Walden         ||         
  RFC298          ||       E. Westheimer         ||         
  RFC299          ||       D. Hopkin         ||         
  RFC300          ||       J.B. North         ||         
  RFC301          ||       R. Alter         ||         
  RFC302          ||       R.F. Bryan         ||         
  RFC303          ||       Network Information Center. Stanford Research Institute         ||         
  RFC304          ||      D.B. McKay         ||       
  RFC305          ||       R. Alter         ||         
  RFC306          ||       E. Westheimer         ||         
  RFC307          ||       E. Harslem         ||         
  RFC308          ||       M. Seriff         ||         
  RFC309          ||       A.K. Bhushan         ||         
  RFC310          ||       A.K. Bhushan         ||         
  RFC311          ||       R.F. Bryan         ||         
  RFC312          ||       A.M. McKenzie         ||         
  RFC313          ||       T.C. O'Sullivan         ||         
  RFC314          ||       I.W. Cotton         ||         
  RFC315          ||       E. Westheimer         ||         
  RFC316          ||       D.B. McKay, A.P. Mullery         ||         
  RFC317          ||       J. Postel         ||         
  RFC318          ||       J. Postel         ||         
  RFC319          ||       E. Westheimer         ||         
  RFC320          ||      R. Reddy         ||       
  RFC321          ||       P.M. Karp         ||         
  RFC322          ||       V. Cerf, J. Postel         ||         
  RFC323          ||       V. Cerf         ||         
  RFC324          ||       J. Postel         ||         
  RFC325          ||       G. Hicks         ||         
  RFC326          ||       E. Westheimer         ||         
  RFC327          ||       A.K. Bhushan         ||         
  RFC328          ||       J. Postel         ||         
  RFC329          ||       Network Information Center. Stanford Research Institute         ||         
  RFC330          ||       E. Westheimer         ||         
  RFC331          ||       J.M. McQuillan         ||         
  RFC332          ||       E. Westheimer         ||         
  RFC333          ||       R.D. Bressler, D. Murphy, D.C. Walden         ||         
  RFC334          ||       A.M. McKenzie         ||         
  RFC335          ||       R.F. Bryan         ||         
  RFC336          ||       I.W. Cotton         ||         
  RFC337          ||               ||         
  RFC338          ||       R.T. Braden         ||         
  RFC339          ||       R. Thomas         ||         
  RFC340          ||       T.C. O'Sullivan         ||         
  RFC341          ||               ||         
  RFC342          ||       E. Westheimer         ||         
  RFC343          ||       A.M. McKenzie         ||         
  RFC344          ||       E. Westheimer         ||         
  RFC345          ||       K.C. Kelley         ||         
  RFC346          ||       J. Postel         ||         
  RFC347          ||       J. Postel         ||         
  RFC348          ||       J. Postel         ||         
  RFC349          ||       J. Postel         ||         
  RFC350          ||       R. Stoughton         ||         
  RFC351          ||       D. Crocker         ||         
  RFC352          ||       D. Crocker         ||         
  RFC353          ||       E. Westheimer         ||         
  RFC354          ||       A.K. Bhushan         ||         
  RFC355          ||       J. Davidson         ||         
  RFC356          ||       R. Alter         ||         
  RFC357          ||       J. Davidson         ||         
  RFC358          ||               ||         
  RFC359          ||       D.C. Walden         ||         
  RFC360          ||      C. Holland         ||       
  RFC361          ||       R.D. Bressler         ||         
  RFC362          ||       E. Westheimer         ||         
  RFC363          ||       Network Information Center. Stanford Research Institute         ||         
  RFC364          ||       M.D. Abrams         ||         
  RFC365          ||       D.C. Walden         ||         
  RFC366          ||       E. Westheimer         ||         
  RFC367          ||       E. Westheimer         ||         
  RFC368          ||       R.T. Braden         ||         
  RFC369          ||       J.R. Pickens         ||         
  RFC370          ||       E. Westheimer         ||         
  RFC371          ||       R.E. Kahn         ||         
  RFC372          ||       R.W. Watson         ||         
  RFC373          ||       J. McCarthy         ||         
  RFC374          ||       A.M. McKenzie         ||         
  RFC375          ||               ||         
  RFC376          ||       E. Westheimer         ||         
  RFC377          ||       R.T. Braden         ||         
  RFC378          ||       A.M. McKenzie         ||         
  RFC379          ||       R. Braden         ||         
  RFC380          ||               ||         
  RFC381          ||       J.M. McQuillan         ||         
  RFC382          ||       L. McDaniel         ||         
  RFC383          ||               ||         
  RFC384          ||       J.B. North         ||         
  RFC385          ||       A.K. Bhushan         ||         
  RFC386          ||       B. Cosell, D.C. Walden         ||         
  RFC387          ||       K.C. Kelley, J. Meir         ||         
  RFC388          ||       V. Cerf         ||         
  RFC389          ||       B. Noble         ||         
  RFC390          ||       R.T. Braden         ||         
  RFC391          ||       A.M. McKenzie         ||         
  RFC392          ||       G. Hicks, B.D. Wessler         ||         
  RFC393          ||       J.M. Winett         ||         
  RFC394          ||       J.M. McQuillan         ||         
  RFC395          ||       J.M. McQuillan         ||         
  RFC396          ||       S. Bunch         ||         
  RFC397          ||               ||         
  RFC398          ||      J.R. Pickens, E. Faeh         ||       
  RFC399          ||       M. Krilanovich         ||         
  RFC400          ||       A.M. McKenzie         ||         
  RFC401          ||       J. Hansen         ||         
  RFC402          ||       J.B. North         ||         
  RFC403          ||      G. Hicks         ||       
  RFC404          ||       A.M. McKenzie         ||         
  RFC405          ||       A.M. McKenzie         ||         
  RFC406          ||       J.M. McQuillan         ||         
  RFC407          ||       R.D. Bressler, R. Guida, A.M. McKenzie         ||         
  RFC408          ||       A.D. Owen, J. Postel         ||         
  RFC409          ||       J.E. White         ||         
  RFC410          ||       J.M. McQuillan         ||         
  RFC411          ||       M.A. Padlipsky         ||         
  RFC412          ||       G. Hicks         ||         
  RFC413          ||       A.M. McKenzie         ||         
  RFC414          ||       A.K. Bhushan         ||         
  RFC415          ||       H. Murray         ||         
  RFC416          ||       J.C. Norton         ||         
  RFC417          ||       J. Postel, C. Kline         ||         
  RFC418          ||      W. Hathaway         ||       
  RFC419          ||       A. Vezza         ||         
  RFC420          ||       H. Murray         ||         
  RFC421          ||       A.M. McKenzie         ||         
  RFC422          ||       A.M. McKenzie         ||         
  RFC423          ||       B. Noble         ||         
  RFC424          ||               ||         
  RFC425          ||       R.D. Bressler         ||         
  RFC426          ||       R. Thomas         ||         
  RFC427          ||               ||         
  RFC428          ||               ||         
  RFC429          ||       J. Postel         ||         
  RFC430          ||       R.T. Braden         ||         
  RFC431          ||       M. Krilanovich         ||         
  RFC432          ||       N. Neigus         ||         
  RFC433          ||       J. Postel         ||         
  RFC434          ||       A.M. McKenzie         ||         
  RFC435          ||       B. Cosell, D.C. Walden         ||         
  RFC436          ||       M. Krilanovich         ||         
  RFC437          ||       E. Faeh         ||         
  RFC438          ||       R. Thomas, R. Clements         ||         
  RFC439          ||       V. Cerf         ||         
  RFC440          ||       D.C. Walden         ||         
  RFC441          ||       R.D. Bressler, R. Thomas         ||         
  RFC442          ||       V. Cerf         ||         
  RFC443          ||       A.M. McKenzie         ||         
  RFC444          ||               ||         
  RFC445          ||       A.M. McKenzie         ||         
  RFC446          ||       L.P. Deutsch         ||         
  RFC447          ||       A.M. McKenzie         ||         
  RFC448          ||       R.T. Braden         ||         
  RFC449          ||       D.C. Walden         ||         
  RFC450          ||       M.A. Padlipsky         ||         
  RFC451          ||       M.A. Padlipsky         ||         
  RFC452          ||      J. Winett         ||       
  RFC453          ||       M.D. Kudlick         ||         
  RFC454          ||       A.M. McKenzie         ||         
  RFC455          ||       A.M. McKenzie         ||         
  RFC456          ||       M.D. Kudlick         ||         
  RFC457          ||       D.C. Walden         ||         
  RFC458          ||       R.D. Bressler, R. Thomas         ||         
  RFC459          ||       W. Kantrowitz         ||         
  RFC460          ||       C. Kline         ||         
  RFC461          ||       A.M. McKenzie         ||         
  RFC462          ||       J. Iseli, D. Crocker         ||         
  RFC463          ||       A.K. Bhushan         ||         
  RFC464          ||       M.D. Kudlick         ||         
  RFC465          ||               ||         
  RFC466          ||       J.M. Winett         ||         
  RFC467          ||       J.D. Burchfiel, R.S. Tomlinson         ||         
  RFC468          ||       R.T. Braden         ||         
  RFC469          ||       M.D. Kudlick         ||         
  RFC470          ||       R. Thomas         ||         
  RFC471          ||       R. Thomas         ||         
  RFC472          ||       S. Bunch         ||         
  RFC473          ||       D.C. Walden         ||         
  RFC474          ||       S. Bunch         ||         
  RFC475          ||      A.K. Bhushan         ||       
  RFC476          ||       A.M. McKenzie         ||         
  RFC477          ||       M. Krilanovich         ||         
  RFC478          ||       R.D. Bressler, R. Thomas         ||         
  RFC479          ||       J.E. White         ||         
  RFC480          ||       J.E. White         ||         
  RFC481          ||               ||         
  RFC482          ||      A.M. McKenzie         ||       
  RFC483          ||       M.D. Kudlick         ||         
  RFC484          ||               ||         
  RFC485          ||       J.R. Pickens         ||         
  RFC486          ||       R.D. Bressler         ||         
  RFC487          ||       R.D. Bressler         ||         
  RFC488          ||       M.F. Auerbach         ||         
  RFC489          ||       J. Postel         ||         
  RFC490          ||       J.R. Pickens         ||         
  RFC491          ||       M.A. Padlipsky         ||         
  RFC492          ||       E. Meyer         ||         
  RFC493          ||      J.C. Michener, I.W. Cotton, K.C. Kelley, D.E. Liddle, E. Meyer         ||       
  RFC494          ||       D.C. Walden         ||         
  RFC495          ||      A.M. McKenzie         ||       
  RFC496          ||       M.F. Auerbach         ||         
  RFC497          ||      A.M. McKenzie         ||       
  RFC498          ||       R.T. Braden         ||         
  RFC499          ||      B.R. Reussow         ||       
  RFC500          ||      A. Shoshani, I. Spiegler         ||       
  RFC501          ||       K.T. Pogran         ||         
  RFC502          ||               ||         
  RFC503          ||       N. Neigus, J. Postel         ||         
  RFC504          ||       R. Thomas         ||         
  RFC505          ||       M.A. Padlipsky         ||         
  RFC506          ||       M.A. Padlipsky         ||         
  RFC507          ||               ||         
  RFC508          ||       L. Pfeifer, J. McAfee         ||         
  RFC509          ||       A.M. McKenzie         ||         
  RFC510          ||       J.E. White         ||         
  RFC511          ||       J.B. North         ||         
  RFC512          ||       W. Hathaway         ||         
  RFC513          ||       W. Hathaway         ||         
  RFC514          ||       W. Kantrowitz         ||         
  RFC515          ||       R. Winter         ||         
  RFC516          ||       J. Postel         ||         
  RFC517          ||               ||         
  RFC518          ||       N. Vaughan, E.J. Feinler         ||         
  RFC519          ||      J.R. Pickens         ||       
  RFC520          ||       J.D. Day         ||         
  RFC521          ||       A.M. McKenzie         ||         
  RFC522          ||      A.M. McKenzie         ||       
  RFC523          ||       A.K. Bhushan         ||         
  RFC524          ||       J.E. White         ||         
  RFC525          ||       W. Parrish, J.R. Pickens         ||         
  RFC526          ||       W.K. Pratt         ||         
  RFC527          ||       R. Merryman         ||         
  RFC528          ||       J.M. McQuillan         ||         
  RFC529          ||       A.M. McKenzie, R. Thomas, R.S. Tomlinson, K.T. Pogran         ||         
  RFC530          ||      A.K. Bhushan         ||       
  RFC531          ||       M.A. Padlipsky         ||         
  RFC532          ||       R.G. Merryman         ||         
  RFC533          ||       D.C. Walden         ||         
  RFC534          ||       D.C. Walden         ||         
  RFC535          ||      R. Thomas         ||       
  RFC536          ||               ||         
  RFC537          ||       S. Bunch         ||         
  RFC538          ||      A.M. McKenzie         ||       
  RFC539          ||       D. Crocker, J. Postel         ||         
  RFC540          ||               ||         
  RFC541          ||               ||         
  RFC542          ||      N. Neigus         ||       
  RFC543          ||       N.D. Meyer         ||         
  RFC544          ||       N.D. Meyer, K. Kelley         ||         
  RFC545          ||       J.R. Pickens         ||         
  RFC546          ||       R. Thomas         ||         
  RFC547          ||       D.C. Walden         ||         
  RFC548          ||       D.C. Walden         ||         
  RFC549          ||       J.C. Michener         ||         
  RFC550          ||       L.P. Deutsch         ||         
  RFC551          ||      Y. Feinroth, R. Fink         ||       
  RFC552          ||       A.D. Owen         ||         
  RFC553          ||       C.H. Irby, K. Victor         ||         
  RFC554          ||               ||         
  RFC555          ||       J.E. White         ||         
  RFC556          ||      A.M. McKenzie         ||       
  RFC557          ||      B.D. Wessler         ||       
  RFC558          ||               ||         
  RFC559          ||       A.K. Bushan         ||         
  RFC560          ||      D. Crocker, J. Postel         ||       
  RFC561          ||      A.K. Bhushan, K.T. Pogran, R.S. Tomlinson, J.E. White         ||       
  RFC562          ||      A.M. McKenzie         ||       
  RFC563          ||       J. Davidson         ||         
  RFC564          ||               ||         
  RFC565          ||       D. Cantor         ||         
  RFC566          ||      A.M. McKenzie         ||       
  RFC567          ||       L.P. Deutsch         ||         
  RFC568          ||       J.M. McQuillan         ||         
  RFC569          ||       M.A. Padlipsky         ||         
  RFC570          ||       J.R. Pickens         ||         
  RFC571          ||      R. Braden         ||       
  RFC572          ||               ||         
  RFC573          ||      A. Bhushan         ||       
  RFC574          ||      M. Krilanovich         ||       
  RFC575          ||               ||         
  RFC576          ||      K. Victor         ||       
  RFC577          ||      D. Crocker         ||       
  RFC578          ||      A.K. Bhushan, N.D. Ryan         ||       
  RFC579          ||      A.M. McKenzie         ||       
  RFC580          ||       J. Postel         ||         
  RFC581          ||      D. Crocker, J. Postel         ||       
  RFC582          ||       R. Clements         ||         
  RFC583          ||               ||         
  RFC584          ||       J. Iseli, D. Crocker, N. Neigus         ||         
  RFC585          ||       D. Crocker, N. Neigus, E.J. Feinler, J. Iseli         ||         
  RFC586          ||      A.M. McKenzie         ||       
  RFC587          ||      J. Postel         ||       
  RFC588          ||      A. Stokes         ||       
  RFC589          ||       R.T. Braden         ||         
  RFC590          ||       M.A. Padlipsky         ||         
  RFC591          ||       D.C. Walden         ||         
  RFC592          ||      R.W. Watson         ||       
  RFC593          ||       A.M. McKenzie, J. Postel         ||         
  RFC594          ||      J.D. Burchfiel         ||       
  RFC595          ||       W. Hathaway         ||         
  RFC596          ||       E.A. Taft         ||         
  RFC597          ||       N. Neigus, E.J. Feinler         ||         
  RFC598          ||      Network Information Center. Stanford Research Institute         ||       
  RFC599          ||       R.T. Braden         ||         
  RFC600          ||      A. Berggreen         ||       
  RFC601          ||       A.M. McKenzie         ||         
  RFC602          ||       R.M. Metcalfe         ||         
  RFC603          ||       J.D. Burchfiel         ||         
  RFC604          ||       J. Postel         ||         
  RFC605          ||               ||         
  RFC606          ||       L.P. Deutsch         ||         
  RFC607          ||       M. Krilanovich, G. Gregg         ||         
  RFC608          ||       M.D. Kudlick         ||         
  RFC609          ||       B. Ferguson         ||         
  RFC610          ||       R. Winter, J. Hill, W. Greiff         ||         
  RFC611          ||       D.C. Walden         ||         
  RFC612          ||       A.M. McKenzie         ||         
  RFC613          ||       A.M. McKenzie         ||         
  RFC614          ||       K.T. Pogran, N. Neigus         ||         
  RFC615          ||      D. Crocker         ||       
  RFC616          ||      D. Walden         ||       
  RFC617          ||       E.A. Taft         ||         
  RFC618          ||       E.A. Taft         ||         
  RFC619          ||       W. Naylor, H. Opderbeck         ||         
  RFC620          ||       B. Ferguson         ||         
  RFC621          ||       M.D. Kudlick         ||         
  RFC622          ||       A.M. McKenzie         ||         
  RFC623          ||       M. Krilanovich         ||         
  RFC624          ||       M. Krilanovich, G. Gregg, W. Hathaway, J.E. White         ||         
  RFC625          ||       M.D. Kudlick, E.J. Feinler         ||         
  RFC626          ||       L. Kleinrock, H. Opderbeck         ||         
  RFC627          ||       M.D. Kudlick, E.J. Feinler         ||         
  RFC628          ||       M.L. Keeney         ||         
  RFC629          ||       J.B. North         ||         
  RFC630          ||       J. Sussman         ||         
  RFC631          ||       A. Danthine         ||         
  RFC632          ||       H. Opderbeck         ||         
  RFC633          ||       A.M. McKenzie         ||         
  RFC634          ||       A.M. McKenzie         ||         
  RFC635          ||       V. Cerf         ||         
  RFC636          ||       J.D. Burchfiel, B. Cosell, R.S. Tomlinson, D.C. Walden         ||         
  RFC637          ||       A.M. McKenzie         ||         
  RFC638          ||       A.M. McKenzie         ||         
  RFC639          ||               ||         
  RFC640          ||       J. Postel         ||         
  RFC641          ||               ||         
  RFC642          ||       J.D. Burchfiel         ||         
  RFC643          ||       E. Mader         ||         
  RFC644          ||       R. Thomas         ||         
  RFC645          ||      D. Crocker         ||       
  RFC646          ||               ||         
  RFC647          ||      M.A. Padlipsky         ||       
  RFC648          ||               ||         
  RFC649          ||               ||         
  RFC650          ||               ||         
  RFC651          ||       D. Crocker         ||         
  RFC652          ||       D. Crocker         ||         
  RFC653          ||       D. Crocker         ||         
  RFC654          ||       D. Crocker         ||         
  RFC655          ||       D. Crocker         ||         
  RFC656          ||       D. Crocker         ||         
  RFC657          ||       D. Crocker         ||         
  RFC658          ||       D. Crocker         ||         
  RFC659          ||       J. Postel         ||         
  RFC660          ||       D.C. Walden         ||         
  RFC661          ||      J. Postel         ||       
  RFC662          ||       R. Kanodia         ||         
  RFC663          ||       R. Kanodia         ||         
  RFC664          ||               ||         
  RFC665          ||               ||         
  RFC666          ||       M.A. Padlipsky         ||         
  RFC667          ||      S.G. Chipman         ||       
  RFC668          ||               ||         
  RFC669          ||      D.W. Dodds         ||       
  RFC670          ||               ||         
  RFC671          ||      R. Schantz         ||       
  RFC672          ||       R. Schantz         ||         
  RFC673          ||               ||         
  RFC674          ||       J. Postel, J.E. White         ||         
  RFC675          ||      V. Cerf, Y. Dalal, C. Sunshine         ||       
  RFC676          ||               ||         
  RFC677          ||       P.R. Johnson, R. Thomas         ||         
  RFC678          ||       J. Postel         ||         
  RFC679          ||      D.W. Dodds         ||       
  RFC680          ||       T.H. Myer, D.A. Henderson         ||         
  RFC681          ||       S. Holmgren         ||         
  RFC682          ||               ||         
  RFC683          ||       R. Clements         ||         
  RFC684          ||       R. Schantz         ||         
  RFC685          ||       M. Beeler         ||         
  RFC686          ||       B. Harvey         ||         
  RFC687          ||       D.C. Walden         ||         
  RFC688          ||       D.C. Walden         ||         
  RFC689          ||       R. Clements         ||         
  RFC690          ||       J. Postel         ||         
  RFC691          ||       B. Harvey         ||         
  RFC692          ||       S.M. Wolfe         ||         
  RFC693          ||               ||         
  RFC694          ||      J. Postel         ||       
  RFC695          ||       M. Krilanovich         ||         
  RFC696          ||      V.G. Cerf         ||       
  RFC697          ||       J. Lieb         ||         
  RFC698          ||      T. Mock         ||       
  RFC699          ||       J. Postel, J. Vernon         ||         
  RFC700          ||      E. Mader, W.W. Plummer, R.S. Tomlinson         ||       
  RFC701          ||      D.W. Dodds         ||       
  RFC702          ||      D.W. Dodds         ||       
  RFC703          ||      D.W. Dodds         ||       
  RFC704          ||       P.J. Santos         ||         
  RFC705          ||       R.F. Bryan         ||         
  RFC706          ||       J. Postel         ||         
  RFC707          ||       J.E. White         ||         
  RFC708          ||       J.E. White         ||         
  RFC709          ||               ||         
  RFC710          ||               ||         
  RFC711          ||               ||       
  RFC712          ||      J.E. Donnelley         ||       
  RFC713          ||       J. Haverty         ||         
  RFC714          ||      A.M. McKenzie         ||       
  RFC715          ||               ||       
  RFC716          ||       D.C. Walden, J. Levin         ||         
  RFC717          ||       J. Postel         ||         
  RFC718          ||       J. Postel         ||         
  RFC719          ||       J. Postel         ||         
  RFC720          ||       D. Crocker         ||         
  RFC721          ||      L.L. Garlick         ||       
  RFC722          ||       J. Haverty         ||         
  RFC723          ||               ||       
  RFC724          ||       D. Crocker, K.T. Pogran, J. Vittal, D.A. Henderson         ||         
  RFC725          ||       J.D. Day, G.R. Grossman         ||         
  RFC726          ||       J. Postel, D. Crocker         ||         
  RFC727          ||       M.R. Crispin         ||         
  RFC728          ||       J.D. Day         ||         
  RFC729          ||       D. Crocker         ||         
  RFC730          ||       J. Postel         ||         
  RFC731          ||       J.D. Day         ||         
  RFC732          ||       J.D. Day         ||         
  RFC733          ||       D. Crocker, J. Vittal, K.T. Pogran, D.A. Henderson         ||         
  RFC734          ||      M.R. Crispin         ||       
  RFC735          ||       D. Crocker, R.H. Gumpertz         ||         
  RFC736          ||       M.R. Crispin         ||         
  RFC737          ||       K. Harrenstien         ||         
  RFC738          ||       K. Harrenstien         ||         
  RFC739          ||       J. Postel         ||         
  RFC740          ||       R.T. Braden         ||         
  RFC741          ||       D. Cohen         ||         
  RFC742          ||       K. Harrenstien         ||         
  RFC743          ||       K. Harrenstien         ||         
  RFC744          ||       J. Sattley         ||         
  RFC745          ||       M. Beeler         ||         
  RFC746          ||       R. Stallman         ||         
  RFC747          ||       M.R. Crispin         ||         
  RFC748          ||       M.R. Crispin         ||         
  RFC749          ||       B. Greenberg         ||         
  RFC750          ||       J. Postel         ||         
  RFC751          ||       P.D. Lebling         ||         
  RFC752          ||       M.R. Crispin         ||         
  RFC753          ||       J. Postel         ||         
  RFC754          ||       J. Postel         ||         
  RFC755          ||       J. Postel         ||         
  RFC756          ||       J.R. Pickens, E.J. Feinler, J.E. Mathis         ||         
  RFC757          ||       D.P. Deutsch         ||         
  RFC758          ||       J. Postel         ||         
  RFC759          ||       J. Postel         ||         
  RFC760          ||       J. Postel         ||         
  RFC761          ||      J. Postel         ||       
  RFC762          ||       J. Postel         ||         
  RFC763          ||       M.D. Abrams         ||         
  RFC764          ||       J. Postel         ||         
  RFC765          ||       J. Postel         ||         
  RFC766          ||       J. Postel         ||         
  RFC767          ||       J. Postel         ||         
  RFC768          ||       J. Postel         ||         
  RFC769          ||       J. Postel         ||         
  RFC770          ||       J. Postel         ||         
  RFC771          ||       V.G. Cerf, J. Postel         ||         
  RFC772          ||      S. Sluizer, J. Postel         ||       
  RFC773          ||       V.G. Cerf         ||         
  RFC774          ||       J. Postel         ||         
  RFC775          ||       D. Mankins, D. Franklin, A.D. Owen         ||         
  RFC776          ||       J. Postel         ||         
  RFC777          ||      J. Postel         ||       
  RFC778          ||       D.L. Mills         ||         
  RFC779          ||      E. Killian         ||       
  RFC780          ||      S. Sluizer, J. Postel         ||       
  RFC781          ||       Z. Su         ||         
  RFC782          ||       J. Nabielsky, A.P. Skelton         ||         
  RFC783          ||       K.R. Sollins         ||         
  RFC784          ||       S. Sluizer, J. Postel         ||         
  RFC785          ||       S. Sluizer, J. Postel         ||         
  RFC786          ||       S. Sluizer, J. Postel         ||         
  RFC787          ||       A.L. Chapin         ||         
  RFC788          ||      J. Postel         ||       
  RFC789          ||       E.C. Rosen         ||         
  RFC790          ||       J. Postel         ||         
  RFC791          ||      J. Postel         ||       
  RFC792          ||      J. Postel         ||       
  RFC793          ||      J. Postel         ||       
  RFC794          ||      V.G. Cerf         ||       
  RFC795          ||       J. Postel         ||         
  RFC796          ||      J. Postel         ||       
  RFC797          ||       A.R. Katz         ||         
  RFC798          ||       A.R. Katz         ||         
  RFC799          ||       D.L. Mills         ||         
  RFC800          ||       J. Postel, J. Vernon         ||         
  RFC801          ||       J. Postel         ||         
  RFC802          ||       A.G. Malis         ||         
  RFC803          ||       A. Agarwal, M.J. O'Connor, D.L. Mills         ||         
  RFC804          ||       International Telegraph and Telephone Consultative Committee of the International Telecommunication Union         ||         
  RFC805          ||       J. Postel         ||         
  RFC806          ||       National Bureau of Standards         ||         
  RFC807          ||       J. Postel         ||         
  RFC808          ||       J. Postel         ||         
  RFC809          ||       T. Chang         ||         
  RFC810          ||       E.J. Feinler, K. Harrenstien, Z. Su, V. White         ||         
  RFC811          ||       K. Harrenstien, V. White, E.J. Feinler         ||         
  RFC812          ||       K. Harrenstien, V. White         ||         
  RFC813          ||      D.D. Clark         ||       
  RFC814          ||      D.D. Clark         ||       
  RFC815          ||       D.D. Clark         ||         
  RFC816          ||      D.D. Clark         ||       
  RFC817          ||      D.D. Clark         ||       
  RFC818          ||       J. Postel         ||         
  RFC819          ||      Z. Su, J. Postel         ||       
  RFC820          ||       J. Postel         ||         
  RFC821          ||       J. Postel         ||         
  RFC822          ||       D. Crocker         ||         
  RFC823          ||      R.M. Hinden, A. Sheltzer         ||       bob.hinden@gmail.com
  RFC824          ||       W.I. MacGregor, D.C. Tappan         ||         
  RFC825          ||       J. Postel         ||         
  RFC826          ||      D. Plummer         ||       
  RFC827          ||       E.C. Rosen         ||         
  RFC828          ||       K. Owen         ||         
  RFC829          ||       V.G. Cerf         ||         
  RFC830          ||       Z. Su         ||         
  RFC831          ||       R.T. Braden         ||         
  RFC832          ||       D. Smallberg         ||         
  RFC833          ||       D. Smallberg         ||         
  RFC834          ||       D. Smallberg         ||         
  RFC835          ||       D. Smallberg         ||         
  RFC836          ||       D. Smallberg         ||         
  RFC837          ||       D. Smallberg         ||         
  RFC838          ||       D. Smallberg         ||         
  RFC839          ||       D. Smallberg         ||         
  RFC840          ||       J. Postel         ||         
  RFC841          ||       National Bureau of Standards         ||         
  RFC842          ||       D. Smallberg         ||         
  RFC843          ||       D. Smallberg         ||         
  RFC844          ||       R. Clements         ||         
  RFC845          ||       D. Smallberg         ||         
  RFC846          ||       D. Smallberg         ||         
  RFC847          ||       A. Westine, D. Smallberg, J. Postel         ||         
  RFC848          ||       D. Smallberg         ||         
  RFC849          ||       M.R. Crispin         ||         
  RFC850          ||       M.R. Horton         ||         
  RFC851          ||       A.G. Malis         ||         
  RFC852          ||      A.G. Malis         ||       
  RFC853          ||               ||       
  RFC854          ||      J. Postel, J.K. Reynolds         ||       
  RFC855          ||       J. Postel, J.K. Reynolds         ||         
  RFC856          ||      J. Postel, J. Reynolds         ||         
  RFC857          ||      J. Postel, J. Reynolds         ||         
  RFC858          ||       J. Postel, J. Reynolds         ||         
  RFC859          ||       J. Postel, J. Reynolds         ||         
  RFC860          ||       J. Postel, J. Reynolds         ||         
  RFC861          ||      J. Postel, J. Reynolds         ||       
  RFC862          ||       J. Postel         ||         
  RFC863          ||       J. Postel         ||         
  RFC864          ||       J. Postel         ||         
  RFC865          ||       J. Postel         ||         
  RFC866          ||       J. Postel         ||         
  RFC867          ||       J. Postel         ||         
  RFC868          ||       J. Postel, K. Harrenstien         ||         
  RFC869          ||      R. Hinden         ||       bob.hinden@gmail.com
  RFC870          ||       J.K. Reynolds, J. Postel         ||         
  RFC871          ||       M.A. Padlipsky         ||         
  RFC872          ||      M.A. Padlipsky         ||       
  RFC873          ||       M.A. Padlipsky         ||         
  RFC874          ||       M.A. Padlipsky         ||         
  RFC875          ||       M.A. Padlipsky         ||         
  RFC876          ||       D. Smallberg         ||         
  RFC877          ||       J.T. Korb         ||         
  RFC878          ||       A.G. Malis         ||         
  RFC879          ||      J. Postel         ||       
  RFC880          ||       J.K. Reynolds, J. Postel         ||         
  RFC881          ||       J. Postel         ||         
  RFC882          ||       P.V. Mockapetris         ||         
  RFC883          ||       P.V. Mockapetris         ||         
  RFC884          ||       M. Solomon, E. Wimmers         ||         
  RFC885          ||       J. Postel         ||         
  RFC886          ||       M.T. Rose         ||         
  RFC887          ||       M. Accetta         ||         
  RFC888          ||       L. Seamonson, E.C. Rosen         ||         
  RFC889          ||      D.L. Mills         ||       
  RFC890          ||       J. Postel         ||         
  RFC891          ||       D.L. Mills         ||         
  RFC892          ||       International Organization for Standardization         ||         
  RFC893          ||      S. Leffler, M.J. Karels         ||       
  RFC894          ||      C. Hornig         ||       
  RFC895          ||      J. Postel         ||       
  RFC896          ||      J. Nagle         ||       
  RFC897          ||       J. Postel         ||         
  RFC898          ||      R.M. Hinden, J. Postel, M. Muuss, J.K. Reynolds         ||       bob.hinden@gmail.com
  RFC899          ||       J. Postel, A. Westine         ||         
  RFC900          ||       J.K. Reynolds, J. Postel         ||         
  RFC901          ||       J.K. Reynolds, J. Postel         ||         
  RFC902          ||       J.K. Reynolds, J. Postel         ||         
  RFC903          ||      R. Finlayson, T. Mann, J.C. Mogul, M. Theimer         ||       
  RFC904          ||      D.L. Mills         ||       
  RFC905          ||      ISO         ||       
  RFC906          ||       R. Finlayson         ||         
  RFC907          ||      Bolt Beranek and Newman Laboratories         ||         
  RFC908          ||      D. Velten, R.M. Hinden, J. Sax         ||       bob.hinden@gmail.com
  RFC909          ||       C. Welles, W. Milliken         ||         
  RFC910          ||       H.C. Forsdick         ||         
  RFC911          ||       P. Kirton         ||         
  RFC912          ||       M. St. Johns         ||         
  RFC913          ||       M. Lottor         ||         
  RFC914          ||       D.J. Farber, G. Delp, T.M. Conte         ||         
  RFC915          ||       M.A. Elvy, R. Nedved         ||         
  RFC916          ||       G.G. Finn         ||         
  RFC917          ||       J.C. Mogul         ||         
  RFC918          ||       J.K. Reynolds         ||         
  RFC919          ||       J.C. Mogul         ||         
  RFC920          ||       J. Postel, J.K. Reynolds         ||         
  RFC921          ||       J. Postel         ||         
  RFC922          ||       J.C. Mogul         ||         
  RFC923          ||       J.K. Reynolds, J. Postel         ||         
  RFC924          ||       J.K. Reynolds, J. Postel         ||         
  RFC925          ||       J. Postel         ||         
  RFC926          ||       International Organization for Standardization         ||         
  RFC927          ||       B.A. Anderson         ||         
  RFC928          ||       M.A. Padlipsky         ||         
  RFC929          ||       J. Lilienkamp, R. Mandell, M.A. Padlipsky         ||         
  RFC930          ||       M. Solomon, E. Wimmers         ||         
  RFC931          ||       M. St. Johns         ||         
  RFC932          ||       D.D. Clark         ||         
  RFC933          ||       S. Silverman         ||         
  RFC934          ||       M.T. Rose, E.A. Stefferud         ||         
  RFC935          ||       J.G. Robinson         ||         
  RFC936          ||       M.J. Karels         ||         
  RFC937          ||       M. Butler, J. Postel, D. Chase, J. Goldberger, J.K. Reynolds         ||         
  RFC938          ||       T. Miller         ||         
  RFC939          ||       National Research Council         ||         
  RFC940          ||      Gateway Algorithms and Data Structures Task Force         ||       
  RFC941          ||      International Organization for Standardization         ||       
  RFC942          ||       National Research Council         ||         
  RFC943          ||      J.K. Reynolds, J. Postel         ||       
  RFC944          ||      J.K. Reynolds, J. Postel         ||       
  RFC945          ||       J. Postel         ||         
  RFC946          ||       R. Nedved         ||         
  RFC947          ||       K. Lebowitz, D. Mankins         ||         
  RFC948          ||       I. Winston         ||         
  RFC949          ||       M.A. Padlipsky         ||         
  RFC950          ||      J.C. Mogul, J. Postel         ||       
  RFC951          ||      W.J. Croft, J. Gilmore         ||       
  RFC952          ||      K. Harrenstien, M.K. Stahl, E.J. Feinler         ||       
  RFC953          ||       K. Harrenstien, M.K. Stahl, E.J. Feinler         ||         
  RFC954          ||       K. Harrenstien, M.K. Stahl, E.J. Feinler         ||         
  RFC955          ||       R.T. Braden         ||         
  RFC956          ||       D.L. Mills         ||         
  RFC957          ||       D.L. Mills         ||         
  RFC958          ||       D.L. Mills         ||         
  RFC959          ||      J. Postel, J. Reynolds         ||       
  RFC960          ||       J.K. Reynolds, J. Postel         ||         
  RFC961          ||       J.K. Reynolds, J. Postel         ||         
  RFC962          ||       M.A. Padlipsky         ||         
  RFC963          ||       D.P. Sidhu         ||         
  RFC964          ||      D.P. Sidhu, T. Blumer         ||       
  RFC965          ||       L. Aguilar         ||         
  RFC966          ||       S.E. Deering, D.R. Cheriton         ||         
  RFC967          ||       M.A. Padlipsky         ||         
  RFC968          ||       V.G. Cerf         ||         
  RFC969          ||       D.D. Clark, M.L. Lambert, L. Zhang         ||         
  RFC970          ||      J. Nagle         ||       
  RFC971          ||       A.L. DeSchon         ||         
  RFC972          ||       F.J. Wancho         ||         
  RFC973          ||       P.V. Mockapetris         ||         
  RFC974          ||      C. Partridge         ||       
  RFC975          ||       D.L. Mills         ||         
  RFC976          ||       M.R. Horton         ||         
  RFC977          ||       B. Kantor, P. Lapsley         ||         
  RFC978          ||       J.K. Reynolds, R. Gillman, W.A. Brackenridge, A. Witkowski, J. Postel         ||         
  RFC979          ||       A.G. Malis         ||         
  RFC980          ||       O.J. Jacobsen, J. Postel         ||         
  RFC981          ||       D.L. Mills         ||         
  RFC982          ||      H.W. Braun         ||       
  RFC983          ||      D.E. Cass, M.T. Rose         ||       
  RFC984          ||       D.D. Clark, M.L. Lambert         ||         
  RFC985          ||       National Science Foundation, Network Technical Advisory Group         ||         
  RFC986          ||       R.W. Callon, H.W. Braun         ||         
  RFC987          ||       S.E. Kille         ||         
  RFC988          ||       S.E. Deering         ||         
  RFC989          ||       J. Linn         ||         
  RFC990          ||       J.K. Reynolds, J. Postel         ||         
  RFC991          ||       J.K. Reynolds, J. Postel         ||         
  RFC992          ||       K.P. Birman, T.A. Joseph         ||         
  RFC993          ||       D.D. Clark, M.L. Lambert         ||         
  RFC994          ||       International Organization for Standardization         ||         
  RFC995          ||      International Organization for Standardization         ||       
  RFC996          ||       D.L. Mills         ||         
  RFC997          ||       J.K. Reynolds, J. Postel         ||         
  RFC998          ||       D.D. Clark, M.L. Lambert, L. Zhang         ||         
  RFC999          ||      A. Westine, J. Postel         ||       
  RFC1000          ||       J.K. Reynolds, J. Postel         ||         
  RFC1001          ||       NetBIOS Working Group in the Defense Advanced Research Projects Agency, Internet Activities Board, End-to-End Services Task Force         ||         
  RFC1002          ||       NetBIOS Working Group in the Defense Advanced Research Projects Agency, Internet Activities Board, End-to-End Services Task Force         ||         
  RFC1003          ||       A.R. Katz         ||         
  RFC1004          ||      D.L. Mills         ||       
  RFC1005          ||       A. Khanna, A.G. Malis         ||         
  RFC1006          ||       M.T. Rose, D.E. Cass         ||         
  RFC1007          ||       W. McCoy         ||         
  RFC1008          ||       W. McCoy         ||         
  RFC1009          ||       R.T. Braden, J. Postel         ||         
  RFC1010          ||       J.K. Reynolds, J. Postel         ||         
  RFC1011          ||      J.K. Reynolds, J. Postel         ||       
  RFC1012          ||       J.K. Reynolds, J. Postel         ||         
  RFC1013          ||       R.W. Scheifler         ||         
  RFC1014          ||       Sun Microsystems         ||         
  RFC1015          ||       B.M. Leiner         ||         
  RFC1016          ||      W. Prue, J. Postel         ||       
  RFC1017          ||       B.M. Leiner         ||         
  RFC1018          ||      A.M. McKenzie         ||       
  RFC1019          ||       D. Arnon         ||         
  RFC1020          ||       S. Romano, M.K. Stahl         ||         
  RFC1021          ||       C. Partridge, G. Trewitt         ||         
  RFC1022          ||       C. Partridge, G. Trewitt         ||         
  RFC1023          ||       G. Trewitt, C. Partridge         ||         
  RFC1024          ||       C. Partridge, G. Trewitt         ||         
  RFC1025          ||       J. Postel         ||         
  RFC1026          ||       S.E. Kille         ||         
  RFC1027          ||       S. Carl-Mitchell, J.S. Quarterman         ||         
  RFC1028          ||       J. Davin, J.D. Case, M. Fedor, M.L. Schoffstall         ||         
  RFC1029          ||       G. Parr         ||         
  RFC1030          ||       M.L. Lambert         ||         
  RFC1031          ||       W.D. Lazear         ||         
  RFC1032          ||       M.K. Stahl         ||         
  RFC1033          ||      M. Lottor         ||       
  RFC1034          ||      P.V. Mockapetris         ||       
  RFC1035          ||      P.V. Mockapetris         ||       
  RFC1036          ||      M.R. Horton, R. Adams         ||       
  RFC1037          ||       B. Greenberg, S. Keene         ||         
  RFC1038          ||       M. St. Johns         ||         
  RFC1039          ||       D. Latham         ||         
  RFC1040          ||       J. Linn         ||         
  RFC1041          ||      Y. Rekhter         ||       
  RFC1042          ||       J. Postel, J.K. Reynolds         ||         
  RFC1043          ||       A. Yasuda, T. Thompson         ||         
  RFC1044          ||      K. Hardwick, J. Lekashman         ||       
  RFC1045          ||       D.R. Cheriton         ||         
  RFC1046          ||       W. Prue, J. Postel         ||         
  RFC1047          ||       C. Partridge         ||         
  RFC1048          ||       P.A. Prindeville         ||         
  RFC1049          ||       M.A. Sirbu         ||         
  RFC1050          ||      Sun Microsystems         ||       
  RFC1051          ||       P.A. Prindeville         ||         
  RFC1052          ||      V.G. Cerf         ||       
  RFC1053          ||      S. Levy, T. Jacobson         ||       
  RFC1054          ||       S.E. Deering         ||         
  RFC1055          ||       J.L. Romkey         ||         
  RFC1056          ||       M.L. Lambert         ||         
  RFC1057          ||       Sun Microsystems         ||         
  RFC1058          ||       C.L. Hedrick         ||         
  RFC1059          ||       D.L. Mills         ||         
  RFC1060          ||       J.K. Reynolds, J. Postel         ||         
  RFC1061          ||               ||       
  RFC1062          ||       S. Romano, M.K. Stahl, M. Recker         ||         
  RFC1063          ||       J.C. Mogul, C.A. Kent, C. Partridge, K. McCloghrie         ||         
  RFC1064          ||       M.R. Crispin         ||         
  RFC1065          ||       K. McCloghrie, M.T. Rose         ||         
  RFC1066          ||       K. McCloghrie, M.T. Rose         ||         
  RFC1067          ||       J.D. Case, M. Fedor, M.L. Schoffstall, J. Davin         ||         
  RFC1068          ||       A.L. DeSchon, R.T. Braden         ||         
  RFC1069          ||       R.W. Callon, H.W. Braun         ||         
  RFC1070          ||       R.A. Hagens, N.E. Hall, M.T. Rose         ||        hagens@cs.wisc.edu, nhall@cs.wisc.edu 
  RFC1071          ||      R.T. Braden, D.A. Borman, C. Partridge         ||       
  RFC1072          ||      V. Jacobson, R.T. Braden         ||       
  RFC1073          ||       D. Waitzman         ||         
  RFC1074          ||       J. Rekhter         ||         
  RFC1075          ||       D. Waitzman, C. Partridge, S.E. Deering         ||         
  RFC1076          ||       G. Trewitt, C. Partridge         ||         
  RFC1077          ||       B.M. Leiner         ||         
  RFC1078          ||      M. Lottor         ||       
  RFC1079          ||       C.L. Hedrick         ||         
  RFC1080          ||       C.L. Hedrick         ||         
  RFC1081          ||       M.T. Rose         ||         
  RFC1082          ||       M.T. Rose         ||         
  RFC1083          ||       Defense Advanced Research Projects Agency, Internet Activities Board         ||         
  RFC1084          ||       J.K. Reynolds         ||        JKREYNOLDS@ISI.EDU 
  RFC1085          ||       M.T. Rose         ||       mrose17@gmail.com
  RFC1086          ||       J.P. Onions, M.T. Rose         ||        JPO@CS.NOTT.AC.UK, mrose17@gmail.com
  RFC1087          ||       Defense Advanced Research Projects Agency, Internet Activities Board         ||         
  RFC1088          ||       L.J. McLaughlin         ||        ljm@TWG.COM 
  RFC1089          ||       M. Schoffstall, C. Davin, M. Fedor, J. Case         ||        schoff@stonewall.nyser.net, jrd@ptt.lcs.mit.edu, fedor@patton.NYSER.NET, case@UTKUX1.UTK.EDU 
  RFC1090          ||       R. Ullmann         ||         
  RFC1091          ||       J. VanBokkelen         ||         
  RFC1092          ||       J. Rekhter         ||         
  RFC1093          ||       H.W. Braun         ||         
  RFC1094          ||      B. Nowicki         ||       
  RFC1095          ||      U.S. Warrier, L. Besaw         ||       
  RFC1096          ||       G.A. Marcy         ||         
  RFC1097          ||       B. Miller         ||         
  RFC1098          ||       J.D. Case, M. Fedor, M.L. Schoffstall, J. Davin         ||        jrd@ptt.lcs.mit.edu 
  RFC1099          ||       J. Reynolds         ||        JKREY@ISI.EDU 
  RFC1100          ||      Defense Advanced Research Projects Agency, Internet Activities Board         ||       
  RFC1101          ||      P.V. Mockapetris         ||       
  RFC1102          ||       D.D. Clark         ||         
  RFC1103          ||       D. Katz         ||         
  RFC1104          ||       H.W. Braun         ||        hwb@merit.edu 
  RFC1105          ||       K. Lougheed, Y. Rekhter         ||         
  RFC1106          ||      R. Fox         ||       rfox@tandem.com
  RFC1107          ||       K.R. Sollins         ||        SOLLINS@XX.LCS.MIT.EDU 
  RFC1108          ||       S. Kent         ||         
  RFC1109          ||       V.G. Cerf         ||        CERF@A.ISI.EDU 
  RFC1110          ||      A.M. McKenzie         ||       MCKENZIE@BBN.COM
  RFC1111          ||       J. Postel         ||        POSTEL@ISI.EDU 
  RFC1112          ||       S.E. Deering         ||        deering@PESCADERO.STANFORD.EDU 
  RFC1113          ||      J. Linn         ||       Linn@ultra.enet.dec.com
  RFC1114          ||       S.T. Kent, J. Linn         ||        kent@BBN.COM, Linn@ultra.enet.dec.com 
  RFC1115          ||       J. Linn         ||        Linn@ultra.enet.dec.com 
  RFC1116          ||       D.A. Borman         ||        dab@CRAY.COM 
  RFC1117          ||       S. Romano, M.K. Stahl, M. Recker         ||         
  RFC1118          ||       E. Krol         ||        Krol@UXC.CSO.UIUC.EDU 
  RFC1119          ||      D.L. Mills         ||       
  RFC1120          ||       V. Cerf         ||        VCERF@NRI.RESTON.VA.US 
  RFC1121          ||       J. Postel, L. Kleinrock, V.G. Cerf, B. Boehm         ||        Postel@ISI.EDU, lk@CS.UCLA.EDU, VCerf@NRI.RESTON.VA.US, boehm@CS.UCLA.EDU 
  RFC1122          ||      R. Braden, Ed.         ||       Braden@ISI.EDU
  RFC1123          ||      R. Braden, Ed.         ||       Braden@ISI.EDU
  RFC1124          ||       B.M. Leiner         ||         
  RFC1125          ||       D. Estrin         ||         
  RFC1126          ||       M. Little         ||        little@SAIC.COM 
  RFC1127          ||       R.T. Braden         ||        Braden@ISI.EDU 
  RFC1128          ||       D.L. Mills         ||         
  RFC1129          ||       D.L. Mills         ||         
  RFC1130          ||       Defense Advanced Research Projects Agency, Internet Activities Board         ||         
  RFC1131          ||      J. Moy         ||       
  RFC1132          ||      L.J. McLaughlin         ||       ljm@TWG.COM
  RFC1133          ||       J.Y. Yu, H.W. Braun         ||        jyy@merit.edu, hwb@merit.edu 
  RFC1134          ||       D. Perkins         ||        rdhobby@ucdavis.edu 
  RFC1135          ||       J.K. Reynolds         ||        JKREY@ISI.EDU 
  RFC1136          ||       S. Hares, D. Katz         ||         
  RFC1137          ||       S. Kille         ||        S.Kille@Cs.Ucl.AC.UK 
  RFC1138          ||       S.E. Kille         ||        S.Kille@Cs.Ucl.AC.UK 
  RFC1139          ||       R.A. Hagens         ||        hagens@CS.WISC.EDU 
  RFC1140          ||       Defense Advanced Research Projects Agency, Internet Activities Board         ||         
  RFC1141          ||      T. Mallory, A. Kullberg         ||       tmallory@CCV.BBN.COM, akullberg@BBN.COM
  RFC1142          ||      D. Oran, Ed.         ||       
  RFC1143          ||       D.J. Bernstein         ||         
  RFC1144          ||       V. Jacobson         ||         
  RFC1145          ||      J. Zweig, C. Partridge         ||       zweig@CS.UIUC.EDU, craig@BBN.COM
  RFC1146          ||      J. Zweig, C. Partridge         ||       zweig@CS.UIUC.EDU, craig@BBN.COM
  RFC1147          ||      R.H. Stine         ||       STINE@SPARTA.COM
  RFC1148          ||       S.E. Kille         ||       S.Kille@Cs.Ucl.AC.UK 
  RFC1149          ||      D. Waitzman         ||       dwaitzman@BBN.COM
  RFC1150          ||      G.S. Malkin, J.K. Reynolds         ||       gmalkin@proteon.com, jkrey@isi.edu
  RFC1151          ||      C. Partridge, R.M. Hinden         ||       craig@BBN.COM, bob.hinden@gmail.com
  RFC1152          ||      C. Partridge         ||       craig@BBN.COM
  RFC1153          ||      F.J. Wancho         ||       
  RFC1154          ||      D. Robinson, R. Ullmann         ||       
  RFC1155          ||       M.T. Rose, K. McCloghrie         ||       mrose17@gmail.com
  RFC1156          ||       K. McCloghrie, M.T. Rose         ||       mrose17@gmail.com
  RFC1157          ||      J.D. Case, M. Fedor, M.L. Schoffstall, J. Davin         ||       jrd@ptt.lcs.mit.edu
  RFC1158          ||       M.T. Rose         ||         
  RFC1159          ||       R. Nelson         ||        nelson@sun.soe.clarkson.edu 
  RFC1160          ||       V. Cerf         ||        VCERF@NRI.RESTON.VA.US 
  RFC1161          ||       M.T. Rose         ||         
  RFC1162          ||       G. Satz         ||         
  RFC1163          ||       K. Lougheed, Y. Rekhter         ||         
  RFC1164          ||       J.C. Honig, D. Katz, M. Mathis, Y. Rekhter, J.Y. Yu         ||         
  RFC1165          ||       J. Crowcroft, J.P. Onions         ||        JON@CS.UCL.AC.UK, JPO@CS.NOTT.AC.UK 
  RFC1166          ||      S. Kirkpatrick, M.K. Stahl, M. Recker         ||       
  RFC1167          ||       V.G. Cerf         ||        vcerf@NRI.Reston.VA.US 
  RFC1168          ||       A. Westine, A.L. DeSchon, J. Postel, C.E. Ward         ||         
  RFC1169          ||       V.G. Cerf, K.L. Mills         ||        vcerf@nri.reston.va.us, MILLS@ECF.NCSL.NIST.GOV 
  RFC1170          ||       R.B. Fougner         ||         
  RFC1171          ||       D. Perkins         ||        ddp@andrew.cmu.edu 
  RFC1172          ||       D. Perkins, R. Hobby         ||        rdhobby@ucdavis.edu, ddp@andrew.cmu.edu 
  RFC1173          ||       J. VanBokkelen         ||        jbvb@ftp.com 
  RFC1174          ||       V.G. Cerf         ||        vcerf@nri.reston.va.us 
  RFC1175          ||       K.L. Bowers, T.L. LaQuey, J.K. Reynolds, K. Roubicek, M.K. Stahl, A. Yuan         ||         
  RFC1176          ||       M.R. Crispin         ||        mrc@Tomobiki-Cho.CAC.Washington.EDU 
  RFC1177          ||       G.S. Malkin, A.N. Marine, J.K. Reynolds         ||        gmalkin@ftp.com, APRIL@NIC.DDN.MIL, jkrey@isi.edu 
  RFC1178          ||       D. Libes         ||        libes@cme.nist.gov 
  RFC1179          ||       L. McLaughlin         ||        ljm@twg.com 
  RFC1180          ||       T.J. Socolofsky, C.J. Kale         ||        TEDS@SPIDER.CO.UK, CLAUDIAK@SPIDER.CO.UK 
  RFC1181          ||       R. Blokzijl         ||        k13@nikhef.nl 
  RFC1182          ||               ||       
  RFC1183          ||      C.F. Everhart, L.A. Mamakos, R. Ullmann, P.V. Mockapetris         ||       Craig_Everhart@transarc.com, pvm@isi.edu
  RFC1184          ||       D.A. Borman         ||        dab@CRAY.COM 
  RFC1185          ||       V. Jacobson, R.T. Braden, L. Zhang         ||        van@CSAM.LBL.GOV, Braden@ISI.EDU, lixia@PARC.XEROX.COM 
  RFC1186          ||       R.L. Rivest         ||        rivest@theory.lcs.mit.edu 
  RFC1187          ||       M.T. Rose, K. McCloghrie, J.R. Davin         ||       mrose17@gmail.com,  KZM@HLS.COM,  jrd@ptt.lcs.mit.edu 
  RFC1188          ||       D. Katz         ||        dkatz@merit.edu 
  RFC1189          ||       U.S. Warrier, L. Besaw, L. LaBarre, B.D. Handspicker         ||         
  RFC1190          ||      C. Topolcic         ||       Casner@ISI.Edu, CLynn@BBN.Com, ppark@BBN.COM, Schroder@BBN.Com, Topolcic@BBN.Com
  RFC1191          ||       J.C. Mogul, S.E. Deering         ||        mogul@decwrl.dec.com, deering@xerox.com 
  RFC1192          ||       B. Kahin         ||        kahin@hulaw.harvard.edu 
  RFC1193          ||       D. Ferrari         ||        ferrari@UCBVAX.BERKELEY.EDU 
  RFC1194          ||       D.P. Zimmerman         ||        dpz@dimacs.rutgers.edu 
  RFC1195          ||      R.W. Callon         ||       
  RFC1196          ||       D.P. Zimmerman         ||        dpz@dimacs.rutgers.edu 
  RFC1197          ||       M. Sherman         ||         
  RFC1198          ||       R.W. Scheifler         ||        rws@expo.lcs.mit.edu 
  RFC1199          ||       J. Reynolds         ||        JKREY@ISI.EDU 
  RFC1200          ||      Defense Advanced Research Projects Agency, Internet Activities Board         ||       
  RFC1201          ||       D. Provan         ||        donp@Novell.Com 
  RFC1202          ||       M.T. Rose         ||       mrose17@gmail.com
  RFC1203          ||       J. Rice         ||        RICE@SUMEX-AIM.STANFORD.EDU 
  RFC1204          ||       S. Yeh, D. Lee         ||        dlee@netix.com 
  RFC1205          ||       P. Chmielewski         ||        paulc@rchland.iinus1.ibm.com 
  RFC1206          ||       G.S. Malkin, A.N. Marine         ||        gmalkin@ftp.com, APRIL@nic.ddn.mil 
  RFC1207          ||       G.S. Malkin, A.N. Marine, J.K. Reynolds         ||        gmalkin@ftp.com, APRIL@nic.ddn.mil, jkrey@isi.edu 
  RFC1208          ||      O.J. Jacobsen, D.C. Lynch         ||       OLE@CSLI.STANFORD.EDU, Lynch@ISI.EDU
  RFC1209          ||      D. Piscitello, J. Lawrence         ||       dave@sabre.bellcore.com, jcl@sabre.bellcore.com
  RFC1210          ||       V.G. Cerf, P.T. Kirstein, B. Randell         ||         
  RFC1211          ||       A. Westine, J. Postel         ||        Westine@ISI.EDU, Postel@ISI.EDU 
  RFC1212          ||       M.T. Rose, K. McCloghrie         ||       mrose17@gmail.com,  kzm@hls.com 
  RFC1213          ||      K. McCloghrie, M. Rose         ||       kzm@hls.com, mrose17@gmail.com
  RFC1214          ||      L. LaBarre         ||       cel@mbunix.mitre.org
  RFC1215          ||       M.T. Rose         ||       mrose17@gmail.com
  RFC1216          ||       P. Richard, P. Kynikos         ||         
  RFC1217          ||       V.G. Cerf         ||        CERF@NRI.RESTON.VA.US 
  RFC1218          ||      North American Directory Forum         ||       
  RFC1219          ||      P.F. Tsuchiya         ||       tsuchiya@thumper.bellcore.com
  RFC1220          ||      F. Baker         ||       fbaker@ACC.COM
  RFC1221          ||      W. Edmond         ||       wbe@bbn.com
  RFC1222          ||       H.W. Braun, Y. Rekhter         ||        HWB@SDSC.EDU, Yakov@Watson.IBM.COM 
  RFC1223          ||       J.M. Halpern         ||         
  RFC1224          ||       L. Steinberg         ||        LOUISS@IBM.COM 
  RFC1225          ||       M.T. Rose         ||       mrose17@gmail.com
  RFC1226          ||       B. Kantor         ||        brian@UCSD.EDU 
  RFC1227          ||       M.T. Rose         ||       mrose17@gmail.com
  RFC1228          ||       G. Carpenter, B. Wijnen         ||         
  RFC1229          ||       K. McCloghrie         ||        kzm@hls.com 
  RFC1230          ||       K. McCloghrie, R. Fox         ||        kzm@hls.com, rfox@synoptics.com 
  RFC1231          ||       K. McCloghrie, R. Fox, E. Decker         ||        kzm@hls.com, rfox@synoptics.com, cire@cisco.com 
  RFC1232          ||       F. Baker, C.P. Kolb         ||        fbaker@acc.com, kolb@psi.com 
  RFC1233          ||       T.A. Cox, K. Tesink         ||        tacox@sabre.bellcore.com, kaj@nvuxr.cc.bellcore.com 
  RFC1234          ||       D. Provan         ||        donp@Novell.Com 
  RFC1235          ||       J. Ioannidis, G. Maguire         ||        ji@cs.columbia.edu, maguire@cs.columbia.edu 
  RFC1236          ||       L. Morales, P. Hasse         ||        lmorales@huachuca-emh8.army.mil, phasse@huachuca-emh8.army.mil 
  RFC1237          ||       R. Colella, E. Gardner, R. Callon         ||        colella@osi3.ncsl.nist.gov, epg@gateway.mitre.org 
  RFC1238          ||       G. Satz         ||         
  RFC1239          ||       J.K. Reynolds         ||        jkrey@isi.edu 
  RFC1240          ||       C. Shue, W. Haggerty, K. Dobbins         ||        chi@osf.org, bill@comm.wang.com 
  RFC1241          ||       R.A. Woodburn, D.L. Mills         ||        woody@cseic.saic.com, mills@udel.edu 
  RFC1242          ||      S. Bradner         ||       SOB@HARVARD.HARVARD.EDU
  RFC1243          ||       S. Waldbusser         ||        waldbusser@andrew.cmu.edu 
  RFC1244          ||       J.P. Holbrook, J.K. Reynolds         ||        holbrook@cic.net, JKREY@ISI.EDU 
  RFC1245          ||       J. Moy         ||         
  RFC1246          ||       J. Moy         ||         
  RFC1247          ||       J. Moy         ||        jmoy@proteon.com 
  RFC1248          ||       F. Baker, R. Coltun         ||        fbaker@acc.com, rcoltun@ni.umd.edu 
  RFC1249          ||       T. Howes, M. Smith, B. Beecher         ||        tim@umich.edu, mcs@umich.edu, bryan@umich.edu 
  RFC1250          ||       J. Postel         ||         
  RFC1251          ||       G. Malkin         ||        gmalkin@ftp.com 
  RFC1252          ||       F. Baker, R. Coltun         ||        fbaker@acc.com, rcoltun@ni.umd.edu 
  RFC1253          ||       F. Baker, R. Coltun         ||        fbaker@acc.com, rcoltun@ni.umd.edu 
  RFC1254          ||       A. Mankin, K. Ramakrishnan         ||         
  RFC1255          ||       The North American Directory Forum         ||         
  RFC1256          ||      S. Deering, Ed.         ||       deering@xerox.com
  RFC1257          ||       C. Partridge         ||        craig@SICS.SE 
  RFC1258          ||      B. Kantor         ||       brian@UCSD.EDU
  RFC1259          ||       M. Kapor         ||        mkapor@eff.org 
  RFC1260          ||               ||       
  RFC1261          ||       S. Williamson, L. Nobile         ||        scottw@DIIS.DDN.MIL 
  RFC1262          ||       V.G. Cerf         ||         
  RFC1263          ||       S. O'Malley, L.L. Peterson         ||        llp@cs.arizona.edu, sean@cs.arizona.edu 
  RFC1264          ||      R.M. Hinden         ||       bob.hinden@gmail.com
  RFC1265          ||       Y. Rekhter         ||        yakov@watson.ibm.com 
  RFC1266          ||       Y. Rekhter         ||        yakov@watson.ibm.com 
  RFC1267          ||       K. Lougheed, Y. Rekhter         ||         
  RFC1268          ||       Y. Rekhter, P. Gross         ||        yakov@watson.ibm.com 
  RFC1269          ||       S. Willis, J.W. Burruss         ||         
  RFC1270          ||       F. Kastenholz         ||         
  RFC1271          ||       S. Waldbusser         ||        waldbusser@andrew.cmu.edu 
  RFC1272          ||       C. Mills, D. Hirsh, G.R. Ruth         ||         
  RFC1273          ||       M.F. Schwartz         ||        schwartz@cs.colorado.edu 
  RFC1274          ||       P. Barker, S. Kille         ||        P.Barker@cs.ucl.ac.uk, S.Kille@cs.ucl.ac.uk 
  RFC1275          ||      S.E. Hardcastle-Kille         ||       S.Kille@CS.UCL.AC.UK
  RFC1276          ||       S.E. Hardcastle-Kille         ||        S.Kille@CS.UCL.AC.UK 
  RFC1277          ||       S.E. Hardcastle-Kille         ||        S.Kille@CS.UCL.AC.UK 
  RFC1278          ||       S.E. Hardcastle-Kille         ||        S.Kille@CS.UCL.AC.UK 
  RFC1279          ||      S.E. Hardcastle-Kille         ||       S.Kille@CS.UCL.AC.UK
  RFC1280          ||       J. Postel         ||         
  RFC1281          ||       R. Pethia, S. Crocker, B. Fraser         ||        rdp@cert.sei.cmu.edu, crocker@tis.com, byf@cert.sei.cmu.edu 
  RFC1282          ||      B. Kantor         ||       brian@UCSD.EDU
  RFC1283          ||       M. Rose         ||         
  RFC1284          ||       J. Cook, Ed.         ||        kasten@europa.clearpoint.com 
  RFC1285          ||       J. Case         ||        case@CS.UTK.EDU 
  RFC1286          ||       E. Decker, P. Langille, A. Rijsinghani, K. McCloghrie         ||        langille@edwin.enet.dec.com, anil@levers.enet.dec.com, kzm@hls.com 
  RFC1287          ||       D. Clark, L. Chapin, V. Cerf, R. Braden, R. Hobby         ||        ddc@LCS.MIT.EDU, vcerf@nri.reston.va.us, lyman@BBN.COM, braden@isi.edu, rdhobby@ucdavis.edu 
  RFC1288          ||       D. Zimmerman         ||        dpz@dimacs.rutgers.edu 
  RFC1289          ||       J. Saperia         ||        saperia@enet.dec.com 
  RFC1290          ||       J. Martin         ||        jmartin@magnus.acs.ohio-state.edu 
  RFC1291          ||       V. Aggarwal         ||         
  RFC1292          ||       R. Lang, R. Wright         ||         
  RFC1293          ||       T. Bradley, C. Brown         ||         
  RFC1294          ||       T. Bradley, C. Brown, A. Malis         ||         
  RFC1295          ||       The North American Directory Forum         ||        0004454742@mcimail.com 
  RFC1296          ||       M. Lottor         ||        mkl@nisc.sri.com 
  RFC1297          ||       D. Johnson         ||         
  RFC1298          ||       R. Wormley, S. Bostock         ||        bwormley@novell.com, steveb@novell.com 
  RFC1299          ||       M. Kennedy         ||        MKENNEDY@ISI.EDU 
  RFC1300          ||       S. Greenfield         ||        0004689513@mcimail.com 
  RFC1301          ||       S. Armstrong, A. Freier, K. Marzullo         ||        armstrong@wrc.xerox.com, freier@apple.com, marzullo@cs.cornell.edu 
  RFC1302          ||       D. Sitzler, P. Smith, A. Marine         ||         
  RFC1303          ||       K. McCloghrie, M. Rose         ||        kzm@hls.com, mrose17@gmail.com
  RFC1304          ||      T. Cox, Ed., K. Tesink, Ed.         ||       tacox@sabre.bellcore.com, kaj@nvuxr.cc.bellcore.com
  RFC1305          ||      D. Mills         ||       
  RFC1306          ||       A. Nicholson, J. Young         ||        droid@cray.com, jsy@cray.com 
  RFC1307          ||       J. Young, A. Nicholson         ||        jsy@cray.com, droid@cray.com 
  RFC1308          ||       C. Weider, J. Reynolds         ||         
  RFC1309          ||       C. Weider, J. Reynolds, S. Heker         ||        jkrey@isi.edu 
  RFC1310          ||       L. Chapin         ||         
  RFC1311          ||       J. Postel         ||         
  RFC1312          ||       R. Nelson, G. Arnold         ||        nelson@crynwr.com, geoff@east.sun.com 
  RFC1313          ||       C. Partridge         ||        craig@aland.bbn.com 
  RFC1314          ||       A. Katz, D. Cohen         ||        Katz@ISI.Edu, Cohen@ISI.Edu 
  RFC1315          ||       C. Brown, F. Baker, C. Carvalho         ||        cbrown@wellfleet.com, fbaker@acc.com, charles@acc.com 
  RFC1316          ||       B. Stewart         ||        rlstewart@eng.xyplex.com 
  RFC1317          ||       B. Stewart         ||        rlstewart@eng.xyplex.com 
  RFC1318          ||       B. Stewart         ||        rlstewart@eng.xyplex.com 
  RFC1319          ||      B. Kaliski         ||       burt@rsa.com
  RFC1320          ||      R. Rivest         ||       rivest@theory.lcs.mit.edu
  RFC1321          ||      R. Rivest         ||       rivest@theory.lcs.mit.edu
  RFC1322          ||       D. Estrin, Y. Rekhter, S. Hotz         ||        estrin@usc.edu, yakov@ibm.com, hotz@usc.edu 
  RFC1323          ||      V. Jacobson, R. Braden, D. Borman         ||       van@CSAM.LBL.GOV, Braden@ISI.EDU
  RFC1324          ||       D. Reed         ||         
  RFC1325          ||       G. Malkin, A. Marine         ||        gmalkin@Xylogics.COM, april@nisc.sri.com 
  RFC1326          ||       P. Tsuchiya         ||        tsuchiya@thumper.bellcore.com 
  RFC1327          ||       S. Hardcastle-Kille         ||         
  RFC1328          ||       S. Hardcastle-Kille         ||        S.Kille@CS.UCL.AC.UK 
  RFC1329          ||      P. Kuehn         ||       thimmela@sniabg.wa.sni.de
  RFC1330          ||       ESCC X.500/X.400 Task Force, ESnet Site Coordinating Comittee (ESCC), Energy Sciences Network (ESnet)         ||         
  RFC1331          ||       W. Simpson         ||        bsimpson@ray.lloyd.com 
  RFC1332          ||       G. McGregor         ||        Glenn.McGregor@Merit.edu 
  RFC1333          ||       W. Simpson         ||        bsimpson@ray.lloyd.com 
  RFC1334          ||       B. Lloyd, W. Simpson         ||        Bill.Simpson@um.cc.umich.edu 
  RFC1335          ||       Z. Wang, J. Crowcroft         ||        z.wang@cs.ucl.ac.uk, j.crowcroft@cs.ucl.ac.uk 
  RFC1336          ||       G. Malkin         ||        gmalkin@Xylogics.COM 
  RFC1337          ||       R. Braden         ||        Braden@ISI.EDU 
  RFC1338          ||       V. Fuller, T. Li, J. Yu, K. Varadhan         ||         
  RFC1339          ||      S. Dorner, P. Resnick         ||       s-dorner@uiuc.edu, presnick@qti.qualcomm.com
  RFC1340          ||       J. Reynolds, J. Postel         ||         
  RFC1341          ||       N. Borenstein, N. Freed         ||         
  RFC1342          ||       K. Moore         ||        moore@cs.utk.edu 
  RFC1343          ||       N. Borenstein         ||         
  RFC1344          ||       N. Borenstein         ||         
  RFC1345          ||       K. Simonsen         ||         
  RFC1346          ||       P. Jones         ||         
  RFC1347          ||       R. Callon         ||         
  RFC1348          ||       B. Manning         ||        bmanning@rice.edu 
  RFC1349          ||       P. Almquist         ||         
  RFC1350          ||       K. Sollins         ||        SOLLINS@LCS.MIT.EDU 
  RFC1351          ||       J. Davin, J. Galvin, K. McCloghrie         ||        jrd@ptt.lcs.mit.edu, galvin@tis.com, kzm@hls.com 
  RFC1352          ||       J. Galvin, K. McCloghrie, J. Davin         ||        galvin@tis.com, kzm@hls.com, jrd@ptt.lcs.mit.edu 
  RFC1353          ||       K. McCloghrie, J. Davin, J. Galvin         ||        kzm@hls.com, jrd@ptt.lcs.mit.edu, galvin@tis.com 
  RFC1354          ||       F. Baker         ||        fbaker@acc.com 
  RFC1355          ||       J. Curran, A. Marine         ||        jcurran@nnsc.nsf.net, april@nisc.sri.com 
  RFC1356          ||       A. Malis, D. Robinson, R. Ullmann         ||         
  RFC1357          ||       D. Cohen         ||        Cohen@ISI.EDU 
  RFC1358          ||       L. Chapin         ||        lyman@BBN.COM 
  RFC1359          ||       ACM SIGUCCS         ||        martyne@nr-tech.cit.cornell.edu 
  RFC1360          ||       J. Postel         ||         
  RFC1361          ||       D. Mills         ||        mills@udel.edu 
  RFC1362          ||       M. Allen         ||        MALLEN@NOVELL.COM, brian@ray.lloyd.com 
  RFC1363          ||       C. Partridge         ||        craig@aland.bbn.com 
  RFC1364          ||       K. Varadhan         ||        kannan@oar.net 
  RFC1365          ||       K. Siyan         ||        72550.1634@compuserve.com 
  RFC1366          ||       E. Gerich         ||        epg@MERIT.EDU 
  RFC1367          ||       C. Topolcic         ||        topolcic@NRI.Reston.VA.US 
  RFC1368          ||       D. McMaster, K. McCloghrie         ||        mcmaster@synoptics.com, kzm@hls.com 
  RFC1369          ||       F. Kastenholz         ||        kasten@ftp.com 
  RFC1370          ||       Internet Architecture Board, L. Chapin         ||         
  RFC1371          ||       P. Gross         ||        pgross@ans.net 
  RFC1372          ||       C. Hedrick, D. Borman         ||         
  RFC1373          ||       T. Tignor         ||        tpt2@isi.edu 
  RFC1374          ||       J. Renwick, A. Nicholson         ||        jkr@CRAY.COM, droid@CRAY.COM 
  RFC1375          ||       P. Robinson         ||         
  RFC1376          ||       S. Senum         ||        sjs@network.com 
  RFC1377          ||       D. Katz         ||        dkatz@cisco.com 
  RFC1378          ||       B. Parker         ||        brad@cayman.com 
  RFC1379          ||      R. Braden         ||       Braden@ISI.EDU
  RFC1380          ||       P. Gross, P. Almquist         ||        pgross@ans.net, Almquist@JESSICA.STANFORD.EDU 
  RFC1381          ||       D. Throop, F. Baker         ||        throop@dg-rtp.dg.com, fbaker@acc.com 
  RFC1382          ||       D. Throop, Ed.         ||        throop@dg-rtp.dg.com 
  RFC1383          ||       C. Huitema         ||        Christian.Huitema@MIRSA.INRIA.FR 
  RFC1384          ||       P. Barker, S.E. Hardcastle-Kille         ||        P.Barker@CS.UCL.AC.UK, S.Kille@ISODE.COM 
  RFC1385          ||      Z. Wang         ||       z.wang@cs.ucl.ac.uk
  RFC1386          ||       A. Cooper, J. Postel         ||         
  RFC1387          ||       G. Malkin         ||        gmalkin@Xylogics.COM 
  RFC1388          ||       G. Malkin         ||        gmalkin@Xylogics.COM 
  RFC1389          ||       G. Malkin, F. Baker         ||        gmalkin@Xylogics.COM, fbaker@acc.com 
  RFC1390          ||       D. Katz         ||        dkatz@cisco.com 
  RFC1391          ||       G. Malkin         ||        gmalkin@Xylogics.COM 
  RFC1392          ||       G. Malkin, T. LaQuey Parker         ||        gmalkin@Xylogics.COM, tracy@utexas.edu 
  RFC1393          ||      G. Malkin         ||       gmalkin@Xylogics.COM
  RFC1394          ||       P. Robinson         ||         
  RFC1395          ||       J. Reynolds         ||        jkrey@isi.edu 
  RFC1396          ||       S. Crocker         ||         
  RFC1397          ||       D. Haskin         ||         
  RFC1398          ||       F. Kastenholz         ||        kasten@ftp.com 
  RFC1399          ||       J. Elliott         ||        elliott@isi.edu 
  RFC1400          ||       S. Williamson         ||        scottw@internic.net 
  RFC1401          ||       Internet Architecture Board         ||         
  RFC1402          ||       J. Martin         ||        nic@osu.edu 
  RFC1403          ||       K. Varadhan         ||         
  RFC1404          ||       B. Stockman         ||         
  RFC1405          ||       C. Allocchio         ||        Claudio.Allocchio@elettra.Trieste.it 
  RFC1406          ||      F. Baker, Ed., J. Watt, Ed.         ||       fbaker@acc.com, james@newbridge.com
  RFC1407          ||       T. Cox, K. Tesink         ||        tacox@mail.bellcore.com, kaj@cc.bellcore.com 
  RFC1408          ||       D. Borman, Ed.         ||        dab@CRAY.COM, stevea@isc.com 
  RFC1409          ||       D. Borman, Ed.         ||        dab@CRAY.COM, stevea@isc.com 
  RFC1410          ||       J. Postel, Ed.         ||         
  RFC1411          ||       D. Borman, Ed.         ||        dab@CRAY.COM, stevea@isc.com 
  RFC1412          ||       K. Alagappan         ||        kannan@sejour.lkg.dec.com, stevea@isc.com 
  RFC1413          ||       M. St. Johns         ||        stjohns@DARPA.MIL 
  RFC1414          ||       M. St. Johns, M. Rose         ||        stjohns@DARPA.MIL, mrose17@gmail.com
  RFC1415          ||       J. Mindel, R. Slaski         ||         
  RFC1416          ||       D. Borman, Ed.         ||        dab@CRAY.COM, stevea@isc.com 
  RFC1417          ||       The North American Directory Forum         ||        0004454742@mcimail.com 
  RFC1418          ||       M. Rose         ||       mrose17@gmail.com
  RFC1419          ||       G. Minshall, M. Ritter         ||        minshall@wc.novell.com, MWRITTER@applelink.apple.com 
  RFC1420          ||       S. Bostock         ||         
  RFC1421          ||      J. Linn         ||       104-8456@mcimail.com
  RFC1422          ||       S. Kent         ||        kent@BBN.COM 
  RFC1423          ||      D. Balenson         ||       balenson@tis.com
  RFC1424          ||       B. Kaliski         ||        burt@rsa.com 
  RFC1425          ||       J. Klensin, WG Chair, N. Freed, Ed., M. Rose, E. Stefferud, D. Crocker         ||         
  RFC1426          ||       J. Klensin, WG Chair, N. Freed, Ed., M. Rose, E. Stefferud, D. Crocker         ||         
  RFC1427          ||       J. Klensin, WG Chair, N. Freed, Ed., K. Moore         ||         
  RFC1428          ||       G. Vaudreuil         ||        GVaudre@CNRI.Reston.VA.US 
  RFC1429          ||       E. Thomas         ||         
  RFC1430          ||       S. Hardcastle-Kille, E. Huizer, V. Cerf, R. Hobby, S. Kent         ||        S.Kille@isode.com, vcerf@cnri.reston.va.us, rdhobby@ucdavis.edu, skent@bbn.com 
  RFC1431          ||       P. Barker         ||         
  RFC1432          ||       J. Quarterman         ||        jsq@tic.com, mids@tic.com 
  RFC1433          ||       J. Garrett, J. Hagan, J. Wong         ||        jwg@garage.att.com, Hagan@UPENN.EDU, jwong@garage.att.com 
  RFC1434          ||       R. Dixon, D. Kushi         ||        rcdixon@ralvmg.vnet.ibm.com, kushi@watson.ibm.com 
  RFC1435          ||       S. Knowles         ||        stev@ftp.com 
  RFC1436          ||       F. Anklesaria, M. McCahill, P. Lindner, D. Johnson, D. Torrey, B. Albert         ||        fxa@boombox.micro.umn.edu, mpm@boombox.micro.umn.edu, lindner@boombox.micro.umn.edu, dmj@boombox.micro.umn.edu, daniel@boombox.micro.umn.edu, alberti@boombox.micro.umn.edu 
  RFC1437          ||       N. Borenstein, M. Linimon         ||        nsb@bellcore.com, linimon@LONESOME.COM 
  RFC1438          ||       A. Lyman Chapin, C. Huitema         ||        Lyman@BBN.COM, Christian.Huitema@MIRSA.INRIA.FR 
  RFC1439          ||       C. Finseth         ||        Craig.A.Finseth-1@umn.edu 
  RFC1440          ||       R. Troth         ||        troth@rice.edu 
  RFC1441          ||       J. Case, K. McCloghrie, M. Rose, S. Waldbusser         ||         
  RFC1442          ||       J. Case, K. McCloghrie, M. Rose, S. Waldbusser         ||         
  RFC1443          ||       J. Case, K. McCloghrie, M. Rose, S. Waldbusser         ||         
  RFC1444          ||       J. Case, K. McCloghrie, M. Rose, S. Waldbusser         ||         
  RFC1445          ||       J. Galvin, K. McCloghrie         ||        galvin@tis.com 
  RFC1446          ||       J. Galvin, K. McCloghrie         ||        galvin@tis.com 
  RFC1447          ||       K. McCloghrie, J. Galvin         ||        galvin@tis.com 
  RFC1448          ||       J. Case, K. McCloghrie, M. Rose, S. Waldbusser         ||         
  RFC1449          ||       J. Case, K. McCloghrie, M. Rose, S. Waldbusser         ||         
  RFC1450          ||       J. Case, K. McCloghrie, M. Rose, S. Waldbusser         ||         
  RFC1451          ||       J. Case, K. McCloghrie, M. Rose, S. Waldbusser         ||         
  RFC1452          ||       J. Case, K. McCloghrie, M. Rose, S. Waldbusser         ||         
  RFC1453          ||       W. Chimiak         ||        chim@relito.medeng.wfu.edu 
  RFC1454          ||       T. Dixon         ||        dixon@rare.nl 
  RFC1455          ||       D. Eastlake 3rd         ||         
  RFC1456          ||       Vietnamese Standardization Working Group         ||         
  RFC1457          ||       R. Housley         ||        Housley.McLean_CSD@Xerox.COM 
  RFC1458          ||       R. Braudes, S. Zabele         ||        rebraudes@tasc.com, gszabele@tasc.com 
  RFC1459          ||      J. Oikarinen, D. Reed         ||       
  RFC1460          ||       M. Rose         ||       mrose17@gmail.com
  RFC1461          ||       D. Throop         ||        throop@dg-rtp.dg.com 
  RFC1462          ||       E. Krol, E. Hoffman         ||        e-krol@uiuc.edu, ellen@merit.edu 
  RFC1463          ||       E. Hoffman, L. Jackson         ||         
  RFC1464          ||       R. Rosenbaum         ||         
  RFC1465          ||       D. Eppenberger         ||        Eppenberger@switch.ch 
  RFC1466          ||       E. Gerich         ||        epg@MERIT.EDU 
  RFC1467          ||       C. Topolcic         ||        topolcic@CNRI.Reston.VA.US 
  RFC1468          ||       J. Murai, M. Crispin, E. van der Poel         ||        jun@wide.ad.jp, MRC@PANDA.COM, erik@poel.juice.or.jp 
  RFC1469          ||       T. Pusateri         ||        pusateri@cs.duke.edu 
  RFC1470          ||       R. Enger, J. Reynolds         ||        enger@reston.ans.net 
  RFC1471          ||       F. Kastenholz         ||        kasten@ftp.com 
  RFC1472          ||       F. Kastenholz         ||        kasten@ftp.com 
  RFC1473          ||       F. Kastenholz         ||        kasten@ftp.com 
  RFC1474          ||       F. Kastenholz         ||        kasten@ftp.com 
  RFC1475          ||      R. Ullmann         ||       
  RFC1476          ||       R. Ullmann         ||         
  RFC1477          ||      M. Steenstrup         ||       
  RFC1478          ||       M. Steenstrup         ||         
  RFC1479          ||       M. Steenstrup         ||         
  RFC1480          ||       A. Cooper, J. Postel         ||         
  RFC1481          ||       C. Huitema         ||        Christian.Huitema@MIRSA.INRIA.FR 
  RFC1482          ||       M. Knopper, S. Richardson         ||         
  RFC1483          ||       Juha Heinanen         ||         
  RFC1484          ||       S. Hardcastle-Kille         ||        S.Kille@ISODE.COM 
  RFC1485          ||       S. Hardcastle-Kille         ||        S.Kille@ISODE.COM 
  RFC1486          ||       M. Rose, C. Malamud         ||       mrose17@gmail.com,  carl@malamud.com 
  RFC1487          ||       W. Yeong, T. Howes, S. Kille         ||        yeongw@psilink.com, tim@umich.edu, S.Kille@isode.com 
  RFC1488          ||       T. Howes, S. Kille, W. Yeong, C. Robbins         ||        tim@umich.edu, S.Kille@isode.com, yeongw@psilink.com 
  RFC1489          ||       A. Chernov         ||        ache@astral.msk.su 
  RFC1490          ||       T. Bradley, C. Brown, A. Malis         ||         
  RFC1491          ||       C. Weider, R. Wright         ||        clw@merit.edu, wright@lbl.gov 
  RFC1492          ||       C. Finseth         ||        Craig.A.Finseth-1@umn.edu 
  RFC1493          ||       E. Decker, P. Langille, A. Rijsinghani, K. McCloghrie         ||        langille@edwin.enet.dec.com, anil@levers.enet.dec.com, kzm@hls.com 
  RFC1494          ||       H. Alvestrand, S. Thompson         ||        Harald.Alvestrand@delab.sintef.no, sjt@gateway.ssw.com 
  RFC1495          ||       H. Alvestrand, S. Kille, R. Miles, M. Rose, S. Thompson         ||        Harald.Alvestrand@delab.sintef.no,  S.Kille@ISODE.COM,  rsm@spyder.ssw.com, mrose17@gmail.com,  sjt@gateway.ssw.com 
  RFC1496          ||       H. Alvestrand, J. Romaguera, K. Jordan         ||        Harald.T.Alvestrand@delab.sintef.no, Kevin.E.Jordan@mercury.oss.arh.cpg.cdc.com, Romaguera@netconsult.ch 
  RFC1497          ||       J. Reynolds         ||        jkrey@isi.edu 
  RFC1498          ||       J. Saltzer         ||        Saltzer@MIT.EDU 
  RFC1499          ||       J. Elliott         ||        elliott@isi.edu 
  RFC1500          ||       J. Postel         ||         
  RFC1501          ||       E. Brunsen         ||        BRUNSENE@EMAIL.ENMU.EDU 
  RFC1502          ||       H. Alvestrand         ||        Harald.Alvestrand@delab.sintef.no 
  RFC1503          ||       K. McCloghrie, M. Rose         ||        kzm@hls.com, mrose17@gmail.com
  RFC1504          ||       A. Oppenheimer         ||        Oppenheime1@applelink.apple.com 
  RFC1505          ||       A. Costanzo, D. Robinson, R. Ullmann         ||         
  RFC1506          ||       J. Houttuin         ||         
  RFC1507          ||       C. Kaufman         ||         
  RFC1508          ||       J. Linn         ||         
  RFC1509          ||       J. Wray         ||        Wray@tuxedo.enet.dec.com 
  RFC1510          ||      J. Kohl, C. Neuman         ||       jtkohl@zk3.dec.com, bcn@isi.edu
  RFC1511          ||       J. Linn         ||         
  RFC1512          ||       J. Case, A. Rijsinghani         ||        case@CS.UTK.EDU, anil@levers.enet.dec.com 
  RFC1513          ||       S. Waldbusser         ||        waldbusser@cmu.edu 
  RFC1514          ||       P. Grillo, S. Waldbusser         ||        pl0143@mail.psi.net, waldbusser@cmu.edu 
  RFC1515          ||       D. McMaster, K. McCloghrie, S. Roberts         ||        mcmaster@synoptics.com, kzm@hls.com, sroberts@farallon.com 
  RFC1516          ||       D. McMaster, K. McCloghrie         ||        mcmaster@synoptics.com, kzm@hls.com 
  RFC1517          ||      Internet Engineering Steering Group, R. Hinden         ||       bob.hinden@gmail.com
  RFC1518          ||       Y. Rekhter, T. Li         ||        yakov@watson.ibm.com, tli@cisco.com 
  RFC1519          ||       V. Fuller, T. Li, J. Yu, K. Varadhan         ||        vaf@Stanford.EDU, tli@cisco.com, jyy@merit.edu, kannan@oar.net 
  RFC1520          ||       Y. Rekhter, C. Topolcic         ||        yakov@watson.ibm.com, topolcic@CNRI.Reston.VA.US 
  RFC1521          ||       N. Borenstein, N. Freed         ||        gvaudre@cnri.reston.va.us 
  RFC1522          ||       K. Moore         ||        moore@cs.utk.edu 
  RFC1523          ||       N. Borenstein         ||        nsb@bellcore.com 
  RFC1524          ||       N. Borenstein         ||        nsb@bellcore.com 
  RFC1525          ||       E. Decker, K. McCloghrie, P. Langille, A. Rijsinghani         ||        kzm@hls.com, langille@edwin.enet.dec.com, anil@levers.enet.dec.com 
  RFC1526          ||       D. Piscitello         ||        dave@mail.bellcore.com 
  RFC1527          ||       G. Cook         ||        cook@path.net 
  RFC1528          ||       C. Malamud, M. Rose         ||         
  RFC1529          ||       C. Malamud, M. Rose         ||         
  RFC1530          ||       C. Malamud, M. Rose         ||         
  RFC1531          ||       R. Droms         ||        droms@bucknell.edu 
  RFC1532          ||       W. Wimer         ||        Walter.Wimer@CMU.EDU 
  RFC1533          ||       S. Alexander, R. Droms         ||        stevea@lachman.com, droms@bucknell.edu 
  RFC1534          ||       R. Droms         ||        droms@bucknell.edu 
  RFC1535          ||       E. Gavron         ||        gavron@aces.com 
  RFC1536          ||       A. Kumar, J. Postel, C. Neuman, P. Danzig, S. Miller         ||        anant@isi.edu, postel@isi.edu, bcn@isi.edu, danzig@caldera.usc.edu, smiller@caldera.usc.edu 
  RFC1537          ||       P. Beertema         ||        Piet.Beertema@cwi.nl, anant@isi.edu 
  RFC1538          ||       W. Behl, B. Sterling, W. Teskey         ||         
  RFC1539          ||       G. Malkin         ||        gmalkin@Xylogics.COM 
  RFC1540          ||       J. Postel         ||         
  RFC1541          ||       R. Droms         ||        droms@bucknell.edu 
  RFC1542          ||      W. Wimer         ||       Walter.Wimer@CMU.EDU
  RFC1543          ||      J. Postel         ||       Postel@ISI.EDU, dwaitzman@BBN.COM
  RFC1544          ||       M. Rose         ||       mrose17@gmail.com
  RFC1545          ||       D. Piscitello         ||        dave@mail.bellcore.com 
  RFC1546          ||      C. Partridge, T. Mendez, W. Milliken         ||       craig@bbn.com, tmendez@bbn.com, milliken@bbn.com
  RFC1547          ||       D. Perkins         ||        Bill.Simpson@um.cc.umich.edu 
  RFC1548          ||       W. Simpson         ||         
  RFC1549          ||       W. Simpson, Ed.         ||         
  RFC1550          ||       S. Bradner, A. Mankin         ||        sob@harvard.edu, mankin@cmf.nrl.navy.mil 
  RFC1551          ||       M. Allen         ||        mallen@novell.com, fbaker@acc.com 
  RFC1552          ||       W. Simpson         ||        Bill.Simpson@um.cc.umich.edu 
  RFC1553          ||       S. Mathur, M. Lewis         ||        mathur@telebit.com, Mark.S.Lewis@telebit.com 
  RFC1554          ||       M. Ohta, K. Handa         ||        mohta@cc.titech.ac.jp, handa@etl.go.jp 
  RFC1555          ||       H. Nussbacher, Y. Bourvine         ||        hank@vm.tau.ac.il, yehavi@vms.huji.ac.il 
  RFC1556          ||       H. Nussbacher         ||        hank@vm.tau.ac.il 
  RFC1557          ||       U. Choi, K. Chon, H. Park         ||        uhhyung@kaist.ac.kr, chon@cosmos.kaist.ac.kr, hjpark@dino.media.co.kr 
  RFC1558          ||       T. Howes         ||        tim@umich.edu 
  RFC1559          ||       J. Saperia         ||        saperia@tay.dec.com 
  RFC1560          ||       B. Leiner, Y. Rekhter         ||        leiner@nsipo.nasa.gov, yakov@watson.ibm.com 
  RFC1561          ||       D. Piscitello         ||        wk04464@worldlink.com 
  RFC1562          ||       G. Michaelson, M. Prior         ||        G.Michaelson@cc.uq.oz.au, mrp@itd.adelaide.edu.au 
  RFC1563          ||       N. Borenstein         ||        nsb@bellcore.com 
  RFC1564          ||       P. Barker, R. Hedberg         ||        P.Barker@cs.ucl.ac.uk, Roland.Hedberg@rc.tudelft.nl, Roland.Hedberg@umdac.umu.se 
  RFC1565          ||       S. Kille, N. Freed         ||        S.Kille@isode.com, ned@innosoft.com 
  RFC1566          ||       S. Kille, N. Freed         ||        S.Kille@isode.com, ned@innosoft.com 
  RFC1567          ||       G. Mansfield, S. Kille         ||        glenn@aic.co.jp, S.Kille@isode.com 
  RFC1568          ||       A. Gwinn         ||        allen@mail.cox.smu.edu 
  RFC1569          ||       M. Rose         ||       mrose17@gmail.com
  RFC1570          ||       W. Simpson, Ed.         ||         
  RFC1571          ||       D. Borman         ||        dab@CRAY.COM 
  RFC1572          ||       S. Alexander, Ed.         ||         
  RFC1573          ||       K. McCloghrie, F. Kastenholz         ||        kzm@hls.com, kasten@ftp.com 
  RFC1574          ||       S. Hares, C. Wittbrodt         ||        skh@merit.edu, cjw@magnolia.Stanford.EDU 
  RFC1575          ||       S. Hares, C. Wittbrodt         ||        skh@merit.edu, cjw@magnolia.Stanford.EDU 
  RFC1576          ||       J. Penner         ||        jjp@bscs.com 
  RFC1577          ||       M. Laubach         ||        laubach@hpl.hp.com 
  RFC1578          ||       J. Sellers         ||        sellers@quest.arc.nasa.gov 
  RFC1579          ||       S. Bellovin         ||        smb@research.att.com 
  RFC1580          ||       EARN Staff         ||        earndoc@earncc.earn.net 
  RFC1581          ||       G. Meyer         ||        gerry@spider.co.uk 
  RFC1582          ||       G. Meyer         ||        gerry@spider.co.uk 
  RFC1583          ||       J. Moy         ||         
  RFC1584          ||      J. Moy         ||       
  RFC1585          ||       J. Moy         ||        jmoy@proteon.com 
  RFC1586          ||       O. deSouza, M. Rodrigues         ||        osmund.desouza@att.com, manoel.rodrigues@att.com 
  RFC1587          ||       R. Coltun, V. Fuller         ||        rcoltun@rainbow-bridge.com, vaf@Valinor.Stanford.EDU 
  RFC1588          ||       J. Postel, C. Anderson         ||         
  RFC1589          ||       D. Mills         ||        mills@udel.edu 
  RFC1590          ||       J. Postel         ||        Postel@ISI.EDU 
  RFC1591          ||       J. Postel         ||        Postel@ISI.EDU 
  RFC1592          ||       B. Wijnen, G. Carpenter, K. Curran, A. Sehgal, G. Waters         ||         
  RFC1593          ||       W. McKenzie, J. Cheng         ||        mckenzie@ralvma.vnet.ibm.com, cheng@ralvm6.vnet.ibm.com 
  RFC1594          ||       A. Marine, J. Reynolds, G. Malkin         ||        amarine@atlas.arc.nasa.gov, jkrey@isi.edu, gmalkin@Xylogics.COM 
  RFC1595          ||       T. Brown, K. Tesink         ||        tacox@mail.bellcore.com, kaj@cc.bellcore.com 
  RFC1596          ||       T. Brown, Ed.         ||        tacox@mail.bellcore.com 
  RFC1597          ||       Y. Rekhter, B. Moskowitz, D. Karrenberg, G. de Groot         ||        yakov@watson.ibm.com, 3858921@mcimail.com, Daniel.Karrenberg@ripe.net, GeertJan.deGroot@ripe.net 
  RFC1598          ||       W. Simpson         ||        Bill.Simpson@um.cc.umich.edu 
  RFC1599          ||       M. Kennedy         ||        MKENNEDY@ISI.EDU 
  RFC1600          ||       J. Postel         ||         
  RFC1601          ||       C. Huitema         ||        Christian.Huitema@sophia.inria.fr 
  RFC1602          ||      Internet Architecture Board, Internet Engineering Steering Group         ||       Christian.Huitema@MIRSA.INRIA.FR, 0006423401@mcimail.com
  RFC1603          ||       E. Huizer, D. Crocker         ||         
  RFC1604          ||       T. Brown, Ed.         ||        tacox@mail.bellcore.com 
  RFC1605          ||       W. Shakespeare         ||         
  RFC1606          ||       J. Onions         ||        j.onions@nexor.co.uk 
  RFC1607          ||       V. Cerf         ||        vcerf@isoc.org, vinton_cerf@mcimail.com 
  RFC1608          ||       T. Johannsen, G. Mansfield, M. Kosters, S. Sataluri         ||        Thomas.Johannsen@ifn.et.tu-dresden.de, glenn@aic.co.jp, markk@internic.net, sri@qsun.att.com 
  RFC1609          ||       G. Mansfield, T. Johannsen, M. Knopper         ||        glenn@aic.co.jp, Thomas.Johannsen@ifn.et.tu-dresden.de, mak@merit.edu 
  RFC1610          ||       J. Postel         ||         
  RFC1611          ||       R. Austein, J. Saperia         ||        sra@epilogue.com, saperia@zko.dec.com 
  RFC1612          ||       R. Austein, J. Saperia         ||        sra@epilogue.com, saperia@zko.dec.com 
  RFC1613          ||       J. Forster, G. Satz, G. Glick, R. Day         ||        forster@cisco.com, satz@cisco.com, gglick@cisco.com, R.Day@jnt.ac.uk 
  RFC1614          ||       C. Adie         ||        C.J.Adie@edinburgh.ac.uk 
  RFC1615          ||       J. Houttuin, J. Craigie         ||         
  RFC1616          ||      RARE WG-MSG Task Force 88, E. Huizer, Ed., J. Romaguera, Ed.         ||       
  RFC1617          ||       P. Barker, S. Kille, T. Lenggenhager         ||        p.barker@cs.ucl.ac.uk, s.kille@isode.com, lenggenhager@switch.ch 
  RFC1618          ||       W. Simpson         ||        Bill.Simpson@um.cc.umich.edu 
  RFC1619          ||       W. Simpson         ||        Bill.Simpson@um.cc.umich.edu 
  RFC1620          ||       B. Braden, J. Postel, Y. Rekhter         ||        Braden@ISI.EDU, Postel@ISI.EDU, Yakov@WATSON.IBM.COM 
  RFC1621          ||       P. Francis         ||        francis@cactus.ntt.jp 
  RFC1622          ||       P. Francis         ||        francis@cactus.ntt.jp 
  RFC1623          ||       F. Kastenholz         ||        kasten@ftp.com 
  RFC1624          ||       A. Rijsinghani, Ed.         ||        anil@levers.enet.dec.com 
  RFC1625          ||       M. St. Pierre, J. Fullton, K. Gamiel, J. Goldman, B. Kahle, J. Kunze, H. Morris, F. Schiettecatte         ||        saint@wais.com, jim.fullton@cnidr.org, kevin.gamiel@cnidr.org, jonathan@think.com, brewster@wais.com, jak@violet.berkeley.edu, morris@wais.com, francois@wais.com 
  RFC1626          ||       R. Atkinson         ||        atkinson@itd.nrl.navy.mil 
  RFC1627          ||       E. Lear, E. Fair, D. Crocker, T. Kessler         ||         
  RFC1628          ||       J. Case, Ed.         ||        case@SNMP.COM 
  RFC1629          ||       R. Colella, R. Callon, E. Gardner, Y. Rekhter         ||        colella@nist.gov, callon@wellfleet.com, epg@gateway.mitre.org, yakov@watson.ibm.com 
  RFC1630          ||       T. Berners-Lee         ||        timbl@info.cern.ch 
  RFC1631          ||       K. Egevang, P. Francis         ||        kbe@craycom.dk, francis@cactus.ntt.jp 
  RFC1632          ||      A. Getchell, Ed., S. Sataluri, Ed.         ||       
  RFC1633          ||       R. Braden, D. Clark, S. Shenker         ||        Braden@ISI.EDU, ddc@LCS.MIT.EDU, Shenker@PARC.XEROX.COM 
  RFC1634          ||       M. Allen         ||        mallen@novell.com, fbaker@acc.com 
  RFC1635          ||       P. Deutsch, A. Emtage, A. Marine         ||        peterd@bunyip.com, bajan@bunyip.com, amarine@atlas.arc.nasa.gov 
  RFC1636          ||       R. Braden, D. Clark, S. Crocker, C. Huitema         ||        Braden@ISI.EDU, ddc@lcs.mit.edu, crocker@tis.com, Christian.Huitema@MIRSA.INRIA.FR 
  RFC1637          ||       B. Manning, R. Colella         ||        bmanning@rice.edu, colella@nist.gov 
  RFC1638          ||       F. Baker, R. Bowen         ||        Rich_Bowen@vnet.ibm.com 
  RFC1639          ||       D. Piscitello         ||        dave@corecom.com 
  RFC1640          ||       S. Crocker         ||        crocker@TIS.COM 
  RFC1641          ||       D. Goldsmith, M. Davis         ||        david_goldsmith@taligent.com, mark_davis@taligent.com 
  RFC1642          ||       D. Goldsmith, M. Davis         ||        david_goldsmith@taligent.com, mark_davis@taligent.com 
  RFC1643          ||      F. Kastenholz         ||       kasten@ftp.com
  RFC1644          ||      R. Braden         ||       Braden@ISI.EDU
  RFC1645          ||       A. Gwinn         ||        allen@mail.cox.smu.edu 
  RFC1646          ||       C. Graves, T. Butts, M. Angel         ||        cvg@oc.com, tom@oc.com, angel@oc.com 
  RFC1647          ||       B. Kelly         ||        kellywh@mail.auburn.edu 
  RFC1648          ||       A. Cargille         ||         
  RFC1649          ||       R. Hagens, A. Hansen         ||        hagens@ans.net, Alf.Hansen@uninett.no 
  RFC1650          ||       F. Kastenholz         ||        kasten@ftp.com 
  RFC1651          ||       J. Klensin, N. Freed, M. Rose, E. Stefferud, D. Crocker         ||        klensin@mci.net,  ned@innosoft.com, mrose17@gmail.com,  stef@nma.com,  dcrocker@sgi.com 
  RFC1652          ||      J. Klensin, N. Freed, M. Rose, E. Stefferud, D. Crocker         ||       klensin@mci.net, ned@innosoft.com, mrose17@gmail.com, stef@nma.com, dcrocker@sgi.com
  RFC1653          ||       J. Klensin, N. Freed, K. Moore         ||        klensin@mci.net, ned@innosoft.com, moore@cs.utk.edu 
  RFC1654          ||      Y. Rekhter, Ed., T. Li, Ed.         ||       
  RFC1655          ||      Y. Rekhter, Ed., P. Gross, Ed.         ||       yakov@watson.ibm.com, 0006423401@mcimail.com
  RFC1656          ||      P. Traina         ||       pst@cisco.com
  RFC1657          ||       S. Willis, J. Burruss, J. Chu, Ed.         ||        swillis@wellfleet.com, jburruss@wellfleet.com, jychu@watson.ibm.com 
  RFC1658          ||       B. Stewart         ||        rlstewart@eng.xyplex.com 
  RFC1659          ||       B. Stewart         ||        rlstewart@eng.xyplex.com 
  RFC1660          ||       B. Stewart         ||        rlstewart@eng.xyplex.com 
  RFC1661          ||       W. Simpson, Ed.         ||         
  RFC1662          ||       W. Simpson, Ed.         ||         
  RFC1663          ||       D. Rand         ||        dave_rand@novell.com 
  RFC1664          ||       C. Allocchio, A. Bonito, B. Cole, S. Giordano, R. Hagens         ||         
  RFC1665          ||      Z. Kielczewski, Ed., D. Kostick, Ed., K. Shih, Ed.         ||       zbig@eicon.qc.ca, dck2@mail.bellcore.com, kmshih@novell.com
  RFC1666          ||      Z. Kielczewski, Ed., D. Kostick, Ed., K. Shih, Ed.         ||       zbig@eicon.qc.ca, dck2@mail.bellcore.com, kmshih@novell.com
  RFC1667          ||       S. Symington, D. Wood, M. Pullen         ||        susan@gateway.mitre.org, wood@mitre.org, mpullen@cs.gmu.edu 
  RFC1668          ||       D. Estrin, T. Li, Y. Rekhter         ||        estrin@usc.edu, tli@cisco.com, yakov@watson.ibm.com 
  RFC1669          ||       J. Curran         ||        jcurran@near.net 
  RFC1670          ||       D. Heagerty         ||        denise@dxcoms.cern.ch 
  RFC1671          ||       B. Carpenter         ||        brian@dxcoms.cern.ch 
  RFC1672          ||       N. Brownlee         ||        n.brownlee@auckland.ac.nz 
  RFC1673          ||       R. Skelton         ||        RSKELTON@msm.epri.com 
  RFC1674          ||       M. Taylor         ||        mark.s.taylor@airdata.com 
  RFC1675          ||       S. Bellovin         ||        smb@research.att.com 
  RFC1676          ||       A. Ghiselli, D. Salomoni, C. Vistoli         ||        Salomoni@infn.it, Vistoli@infn.it, Ghiselli@infn.it 
  RFC1677          ||       B. Adamson         ||        adamson@itd.nrl.navy.mil 
  RFC1678          ||       E. Britton, J. Tavs         ||        brittone@vnet.ibm.com, tavs@vnet.ibm.com 
  RFC1679          ||       D. Green, P. Irey, D. Marlow, K. O'Donoghue         ||        dtgreen@relay.nswc.navy.mil, pirey@relay.nswc.navy.mil, dmarlow@relay.nswc.navy.mil, kodonog@relay.nswc.navy.mil 
  RFC1680          ||       C. Brazdziunas         ||        crb@faline.bellcore.com 
  RFC1681          ||       S. Bellovin         ||        smb@research.att.com 
  RFC1682          ||       J. Bound         ||        bound@zk3.dec.com 
  RFC1683          ||       R. Clark, M. Ammar, K. Calvert         ||        rjc@cc.gatech.edu, ammar@cc.gatech.edu, calvert@cc.gatech.edu 
  RFC1684          ||       P. Jurg         ||         
  RFC1685          ||       H. Alvestrand         ||         
  RFC1686          ||       M. Vecchi         ||        mpvecchi@twcable.com 
  RFC1687          ||       E. Fleischman         ||        ericf@atc.boeing.com 
  RFC1688          ||       W. Simpson         ||        Bill.Simpson@um.cc.umich.edu 
  RFC1689          ||       J. Foster, Ed.         ||         
  RFC1690          ||       G. Huston         ||        Geoff.Huston@aarnet.edu.au 
  RFC1691          ||       W. Turner         ||        wrt1@cornell.edu 
  RFC1692          ||       P. Cameron, D. Crocker, D. Cohen, J. Postel         ||        cameron@xylint.co.uk, dcrocker@sgi.com, Cohen@myricom.com, Postel@ISI.EDU 
  RFC1693          ||      T.  Connolly, P. Amer, P. Conrad         ||       connolly@udel.edu, amer@udel.edu, pconrad@udel.edu
  RFC1694          ||      T. Brown, Ed., K. Tesink, Ed.         ||       tacox@mail.bellcore.com, kaj@cc.bellcore.com
  RFC1695          ||      M. Ahmed, Ed., K. Tesink, Ed.         ||       mxa@mail.bellcore.com, kaj@cc.bellcore.com
  RFC1696          ||       J. Barnes, L. Brown, R. Royston, S. Waldbusser         ||        barnes@xylogics.com, brown_l@msm.cdx.mot.com, rroyston@usr.com, swol@andrew.cmu.edu 
  RFC1697          ||       D. Brower, Ed., B. Purvy, A. Daniel, M. Sinykin, J. Smith         ||        daveb@ingres.com, bpurvy@us.oracle.com, anthony@informix.com, msinykin@us.oracle.com, jaysmith@us.oracle.com 
  RFC1698          ||       P. Furniss         ||        P.Furniss@ulcc.ac.uk 
  RFC1699          ||       J. Elliott         ||        elliott@isi.edu 
  RFC1700          ||      J. Reynolds, J. Postel         ||       jkrey@isi.edu, postel@isi.edu
  RFC1701          ||       S. Hanks, T. Li, D. Farinacci, P. Traina         ||        stan@netsmiths.com, tli@cisco.com, dino@cisco.com, pst@cisco.com 
  RFC1702          ||       S. Hanks, T. Li, D. Farinacci, P. Traina         ||        stan@netsmiths.com, tli@cisco.com, dino@cisco.com, pst@cisco.com 
  RFC1703          ||       M. Rose         ||       mrose17@gmail.com
  RFC1704          ||       N. Haller, R. Atkinson         ||         
  RFC1705          ||       R. Carlson, D. Ficarella         ||        RACarlson@anl.gov, ficarell@cpdmfg.cig.mot.com 
  RFC1706          ||       B. Manning, R. Colella         ||        bmanning@isi.edu, colella@nist.gov 
  RFC1707          ||       M. McGovern, R. Ullmann         ||        scrivner@world.std.com, rullmann@crd.lotus.com 
  RFC1708          ||       D. Gowin         ||        drg508@crane-ns.nwscc.sea06.navy.MIL 
  RFC1709          ||       J. Gargano, D. Wasley         ||        jcgargano@ucdavis.edu, dlw@berkeley.edu 
  RFC1710          ||      R. Hinden         ||       bob.hinden@gmail.com
  RFC1711          ||       J. Houttuin         ||        houttuin@rare.nl 
  RFC1712          ||       C. Farrell, M. Schulze, S. Pleitner, D. Baldoni         ||        craig@cs.curtin.edu.au, mike@cs.curtin.edu.au, pleitner@cs.curtin.edu.au, flint@cs.curtin.edu.au 
  RFC1713          ||       A. Romao         ||        artur@fct.unl.pt 
  RFC1714          ||       S. Williamson, M. Kosters         ||        scottw@internic.net, markk@internic.net 
  RFC1715          ||       C. Huitema         ||        Christian.Huitema@MIRSA.INRIA.FR 
  RFC1716          ||       P. Almquist, F. Kastenholz         ||         
  RFC1717          ||       K. Sklower, B. Lloyd, G. McGregor, D. Carr         ||        sklower@CS.Berkeley.EDU, brian@lloyd.com, glenn@lloyd.com, dcarr@Newbridge.COM 
  RFC1718          ||       IETF Secretariat, G. Malkin         ||        ietf-info@cnri.reston.va.us, gmalkin@Xylogics.COM 
  RFC1719          ||       P. Gross         ||        phill_gross@mcimail.com 
  RFC1720          ||       J. Postel         ||         
  RFC1721          ||       G. Malkin         ||        gmalkin@Xylogics.COM 
  RFC1722          ||       G. Malkin         ||        gmalkin@Xylogics.COM 
  RFC1723          ||      G. Malkin         ||       gmalkin@Xylogics.COM
  RFC1724          ||       G. Malkin, F. Baker         ||        gmalkin@Xylogics.COM, fred@cisco.com 
  RFC1725          ||      J. Myers, M. Rose         ||       mrose17@gmail.com
  RFC1726          ||       C. Partridge, F. Kastenholz         ||        craig@aland.bbn.com, kasten@ftp.com 
  RFC1727          ||       C. Weider, P. Deutsch         ||        clw@bunyip.com, peterd@bunyip.com 
  RFC1728          ||       C. Weider         ||        clw@bunyip.com 
  RFC1729          ||       C. Lynch         ||        clifford.lynch@ucop.edu 
  RFC1730          ||       M. Crispin         ||        MRC@CAC.Washington.EDU 
  RFC1731          ||       J. Myers         ||         
  RFC1732          ||       M. Crispin         ||        MRC@CAC.Washington.EDU 
  RFC1733          ||       M. Crispin         ||        MRC@CAC.Washington.EDU 
  RFC1734          ||      J. Myers         ||       
  RFC1735          ||       J. Heinanen, R. Govindan         ||        Juha.Heinanen@datanet.tele.fi, govindan@isi.edu 
  RFC1736          ||      J. Kunze         ||       jak@violet.berkeley.edu
  RFC1737          ||       K. Sollins, L. Masinter         ||        masinter@parc.xerox.com, sollins@lcs.mit.edu 
  RFC1738          ||      T. Berners-Lee, L. Masinter, M. McCahill         ||       
  RFC1739          ||       G. Kessler, S. Shepard         ||        kumquat@hill.com, sds@hill.com 
  RFC1740          ||       P. Faltstrom, D. Crocker, E. Fair         ||        paf@nada.kth.se, dcrocker@mordor.stanford.edu, fair@apple.com 
  RFC1741          ||       P. Faltstrom, D. Crocker, E. Fair         ||        paf@nada.kth.se, dcrocker@mordor.stanford.edu, fair@apple.com 
  RFC1742          ||       S. Waldbusser, K. Frisa         ||        waldbusser@cmu.edu, kfrisa@fore.com 
  RFC1743          ||       K. McCloghrie, E. Decker         ||        kzm@cisco.com, cire@cisco.com 
  RFC1744          ||       G. Huston         ||        Geoff.Huston@aarnet.edu.au 
  RFC1745          ||       K. Varadhan, S. Hares, Y. Rekhter         ||        kannan@isi.edu, skh@merit.edu, yakov@watson.ibm.com 
  RFC1746          ||       B. Manning, D. Perkins         ||        bmanning@isi.edu, dperkins@tenet.edu 
  RFC1747          ||       J. Hilgeman, Chair, S. Nix, A. Bartky, W. Clark, Ed.         ||        jeffh@apertus.com, snix@metaplex.com, alan@sync.com, wclark@cisco.com 
  RFC1748          ||       K. McCloghrie, E. Decker         ||        kzm@cisco.com, cire@cisco.com 
  RFC1749          ||       K. McCloghrie, F. Baker, E. Decker         ||        kzm@cisco.com, fred@cisco.com, cire@cisco.com 
  RFC1750          ||       D. Eastlake 3rd, S. Crocker, J. Schiller         ||        dee@lkg.dec.com, crocker@cybercash.com, jis@mit.edu 
  RFC1751          ||       D. McDonald         ||        danmcd@itd.nrl.navy.mil 
  RFC1752          ||       S. Bradner, A. Mankin         ||        sob@harvard.edu, mankin@isi.edu 
  RFC1753          ||       N. Chiappa         ||        jnc@lcs.mit.edu 
  RFC1754          ||       M. Laubach         ||        laubach@com21.com 
  RFC1755          ||       M. Perez, F. Liaw, A. Mankin, E. Hoffman, D. Grossman, A. Malis         ||        perez@isi.edu, fong@fore.com, mankin@isi.edu, hoffman@isi.edu, dan@merlin.dev.cdx.mot.com, malis@maelstrom.timeplex.com 
  RFC1756          ||       T. Rinne         ||        Timo.Rinne@hut.fi 
  RFC1757          ||       S. Waldbusser         ||        waldbusser@cmu.edu 
  RFC1758          ||       The North American Directory Forum         ||        0004454742@mcimail.com 
  RFC1759          ||      R. Smith, F. Wright, T. Hastings, S. Zilles, J. Gyllenskog         ||       rlsmith@nb.ppd.ti.com, don@lexmark.com, tom.hastings@alum.mit.edu, szilles@mv.us.adobe.com, jgyllens@hpdmd48.boi.hp.com
  RFC1760          ||       N. Haller         ||        nmh@bellcore.com 
  RFC1761          ||       B. Callaghan, R. Gilligan         ||        brent.callaghan@eng.sun.com, bob.gilligan@eng.sun.com 
  RFC1762          ||       S. Senum         ||        sjs@digibd.com 
  RFC1763          ||       S. Senum         ||        sjs@digibd.com 
  RFC1764          ||       S. Senum         ||        sjs@digibd.com 
  RFC1765          ||       J. Moy         ||        jmoy@casc.com 
  RFC1766          ||       H. Alvestrand         ||        Harald.T.Alvestrand@uninett.no 
  RFC1767          ||       D. Crocker         ||         
  RFC1768          ||       D. Marlow         ||        dmarlow@relay.nswc.navy.mil 
  RFC1769          ||       D. Mills         ||        mills@udel.edu 
  RFC1770          ||      C. Graff         ||       bud@fotlan5.fotlan.army.mil
  RFC1771          ||       Y. Rekhter, T. Li         ||         
  RFC1772          ||       Y. Rekhter, P. Gross         ||        yakov@watson.ibm.com, 0006423401@mcimail.com 
  RFC1773          ||       P. Traina         ||        pst@cisco.com 
  RFC1774          ||       P. Traina, Ed.         ||         
  RFC1775          ||       D. Crocker         ||        dcrocker@mordor.stanford.edu 
  RFC1776          ||       S. Crocker         ||        crocker@cybercash.com 
  RFC1777          ||       W. Yeong, T. Howes, S. Kille         ||        yeongw@psilink.com, tim@umich.edu, S.Kille@isode.com 
  RFC1778          ||       T. Howes, S. Kille, W. Yeong, C. Robbins         ||        tim@umich.edu, S.Kille@isode.com, yeongw@psilink.com 
  RFC1779          ||       S. Kille         ||        S.Kille@ISODE.COM 
  RFC1780          ||       J. Postel, Ed.         ||         
  RFC1781          ||       S. Kille         ||        S.Kille@ISODE.COM 
  RFC1782          ||       G. Malkin, A. Harkin         ||        gmalkin@xylogics.com, ash@cup.hp.com 
  RFC1783          ||       G. Malkin, A. Harkin         ||        gmalkin@xylogics.com, ash@cup.hp.com 
  RFC1784          ||       G. Malkin, A. Harkin         ||        gmalkin@xylogics.com, ash@cup.hp.com 
  RFC1785          ||       G. Malkin, A. Harkin         ||        gmalkin@xylogics.com, ash@cup.hp.com 
  RFC1786          ||       T. Bates, E. Gerich, L. Joncheray, J-M. Jouanigot, D. Karrenberg, M. Terpstra, J. Yu         ||         
  RFC1787          ||       Y. Rekhter         ||         
  RFC1788          ||      W. Simpson         ||       
  RFC1789          ||       C. Yang         ||        cqyang@cs.unt.edu 
  RFC1790          ||       V. Cerf         ||        vcerf@isoc.org 
  RFC1791          ||       T. Sung         ||        tae@novell.Com 
  RFC1792          ||       T. Sung         ||        tae@novell.Com 
  RFC1793          ||       J. Moy         ||        jmoy@casc.com 
  RFC1794          ||       T. Brisco         ||        brisco@rutgers.edu 
  RFC1795          ||       L. Wells, Chair, A. Bartky, Ed.         ||         
  RFC1796          ||       C. Huitema, J. Postel, S. Crocker         ||        Christian.Huitema@MIRSA.INRIA.FR, Postel@ISI.EDU, crocker@cybercash.com 
  RFC1797          ||       Internet Assigned Numbers Authority (IANA)         ||        iana@isi.edu 
  RFC1798          ||       A. Young         ||        A.Young@isode.com 
  RFC1799          ||       M. Kennedy         ||        MKENNEDY@ISI.EDU 
  RFC1800          ||       J. Postel, Ed.         ||         
  RFC1801          ||       S. Kille         ||        S.Kille@ISODE.COM 
  RFC1802          ||       H. Alvestrand, K. Jordan, S. Langlois, J. Romaguera         ||        Harald.T.Alvestrand@uninett.no, Kevin.E.Jordan@cdc.com, Sylvain.Langlois@der.edf.fr, Romaguera@NetConsult.ch 
  RFC1803          ||       R. Wright, A. Getchell, T. Howes, S. Sataluri, P. Yee, W. Yeong         ||         
  RFC1804          ||       G. Mansfield, P. Rajeev, S. Raghavan, T. Howes         ||        glenn@aic.co.jp, rajeev%hss@lando.hns.com, svr@iitm.ernet.in, tim@umich.edu 
  RFC1805          ||       A. Rubin         ||        rubin@bellcore.com 
  RFC1806          ||      R. Troost, S. Dorner         ||       rens@century.com, sdorner@qualcomm.com
  RFC1807          ||       R. Lasher, D. Cohen         ||        rlasher@forsythe.stanford.edu, Cohen@myri.com 
  RFC1808          ||       R. Fielding         ||        fielding@ics.uci.edu 
  RFC1809          ||       C. Partridge         ||        craig@aland.bbn.com 
  RFC1810          ||       J. Touch         ||        touch@isi.edu 
  RFC1811          ||       Federal Networking Council         ||        execdir@fnc.gov 
  RFC1812          ||      F. Baker, Ed.         ||       
  RFC1813          ||       B. Callaghan, B. Pawlowski, P. Staubach         ||        brent.callaghan@eng.sun.com, beepy@netapp.com, peter.staubach@eng.sun.com 
  RFC1814          ||       E. Gerich         ||        epg@merit.edu 
  RFC1815          ||       M. Ohta         ||        mohta@cc.titech.ac.jp 
  RFC1816          ||       Federal Networking Council         ||        execdir@fnc.gov 
  RFC1817          ||       Y. Rekhter         ||        yakov@cisco.com 
  RFC1818          ||       J. Postel, T. Li, Y. Rekhter         ||        postel@isi.edu, yakov@cisco.com, tli@cisco.com 
  RFC1819          ||      L. Delgrossi, Ed., L. Berger, Ed.         ||       lberger@bbn.com, luca@andersen.fr, dat@bbn.com, stevej@syzygycomm.com, schaller@heidelbg.ibm.com
  RFC1820          ||       E. Huizer         ||        Erik.Huizer@SURFnet.nl 
  RFC1821          ||       M. Borden, E. Crawley, B. Davie, S. Batsell         ||         
  RFC1822          ||       J. Lowe         ||         
  RFC1823          ||       T. Howes, M. Smith         ||        tim@umich.edu, mcs@umich.edu 
  RFC1824          ||       H. Danisch         ||        danisch@ira.uka.de 
  RFC1825          ||       R. Atkinson         ||         
  RFC1826          ||       R. Atkinson         ||         
  RFC1827          ||       R. Atkinson         ||         
  RFC1828          ||      P. Metzger, W. Simpson         ||       
  RFC1829          ||       P. Karn, P. Metzger, W. Simpson         ||         
  RFC1830          ||       G. Vaudreuil         ||        Greg.Vaudreuil@Octel.com 
  RFC1831          ||      R. Srinivasan         ||       raj@eng.sun.com
  RFC1832          ||       R. Srinivasan         ||        raj@eng.sun.com 
  RFC1833          ||      R. Srinivasan         ||       raj@eng.sun.com
  RFC1834          ||       J. Gargano, K. Weiss         ||        jcgargano@ucdavis.edu, krweiss@ucdavis.edu 
  RFC1835          ||       P. Deutsch, R. Schoultz, P. Faltstrom, C. Weider         ||        peterd@bunyip.com, schoultz@sunet.se, paf@bunyip.com, clw@bunyip.com 
  RFC1836          ||       S. Kille         ||        S.Kille@ISODE.COM 
  RFC1837          ||       S. Kille         ||        S.Kille@ISODE.COM 
  RFC1838          ||       S. Kille         ||        S.Kille@ISODE.COM 
  RFC1839          ||               ||         
  RFC1840          ||               ||         
  RFC1841          ||       J. Chapman, D. Coli, A. Harvey, B. Jensen, K. Rowett         ||        joelle@cisco.com, dcoli@cisco.com, agh@cisco.com, bent@cisco.com, krowett@cisco.com 
  RFC1842          ||       Y. Wei, Y. Zhang, J. Li, J. Ding, Y. Jiang         ||        HZRFC@usai.asiainfo.com, zhang@orion.harvard.edu, jian@is.rice.edu, ding@Beijing.AsiaInfo.com, yjj@eng.umd.edu 
  RFC1843          ||       F. Lee         ||        lee@csl.stanford.edu 
  RFC1844          ||       E. Huizer         ||        Erik.Huizer@SURFnet.nl 
  RFC1845          ||       D. Crocker, N. Freed, A. Cargille         ||        dcrocker@mordor.stanford.edu, ned@innosoft.com 
  RFC1846          ||      A. Durand, F. Dupont         ||       Alain.Durand@imag.fr, Francis.Dupont@inria.fr
  RFC1847          ||       J. Galvin, S. Murphy, S. Crocker, N. Freed         ||        galvin@tis.com, sandy@tis.com, crocker@cybercash.com, ned@innosoft.com 
  RFC1848          ||       S. Crocker, N. Freed, J. Galvin, S. Murphy         ||        crocker@cybercash.com, galvin@tis.com, murphy@tis.com, ned@innosoft.com 
  RFC1849          ||      H. Spencer         ||       henry@zoo.utoronto.ca
  RFC1850          ||       F. Baker, R. Coltun         ||        fred@cisco.com, rcoltun@rainbow-bridge.com 
  RFC1851          ||       P. Karn, P. Metzger, W. Simpson         ||         
  RFC1852          ||       P. Metzger, W. Simpson         ||         
  RFC1853          ||       W. Simpson         ||         
  RFC1854          ||       N. Freed         ||        ned@innosoft.com 
  RFC1855          ||       S. Hambridge         ||        sallyh@ludwig.sc.intel.com 
  RFC1856          ||       H. Clark         ||        henryc@bbnplanet.com 
  RFC1857          ||       M. Lambert         ||        lambert@psc.edu 
  RFC1858          ||       G. Ziemba, D. Reed, P. Traina         ||        paul@alantec.com, darrenr@cyber.com.au, pst@cisco.com 
  RFC1859          ||       Y. Pouffary         ||        pouffary@taec.enet.dec.com 
  RFC1860          ||       T. Pummill, B. Manning         ||        trop@alantec.com, bmanning@isi.edu 
  RFC1861          ||       A. Gwinn         ||        allen@mail.cox.smu.edu 
  RFC1862          ||       M. McCahill, J. Romkey, M. Schwartz, K. Sollins, T. Verschuren, C. Weider         ||        mpm@boombox.micro.umn.edu, romkey@apocalypse.org, schwartz@cs.colorado.edu, sollins@lcs.mit.edu, Ton.Verschuren@surfnet.nl, clw@bunyip.com 
  RFC1863          ||       D. Haskin         ||        dhaskin@baynetworks.com 
  RFC1864          ||       J. Myers, M. Rose         ||       mrose17@gmail.com
  RFC1865          ||       W. Houser, J. Griffin, C. Hage         ||        houser.walt@forum.va.gov, agriffin@cpcug.org, carl@chage.com 
  RFC1866          ||       T. Berners-Lee, D. Connolly         ||        timbl@w3.org, connolly@w3.org 
  RFC1867          ||       E. Nebel, L. Masinter         ||        masinter@parc.xerox.com, nebel@xsoft.sd.xerox.com 
  RFC1868          ||       G. Malkin         ||        gmalkin@xylogics.com 
  RFC1869          ||       J. Klensin, N. Freed, M. Rose, E. Stefferud, D. Crocker         ||        klensin@mci.net,  ned@innosoft.com, mrose17@gmail.com,  stef@nma.com,  dcrocker@mordor.stanford.edu 
  RFC1870          ||       J. Klensin, N. Freed, K. Moore         ||        klensin@mci.net, ned@innosoft.com, moore@cs.utk.edu 
  RFC1871          ||       J. Postel         ||        postel@isi.edu 
  RFC1872          ||       E. Levinson         ||        ELevinson@Accurate.com 
  RFC1873          ||       E. Levinson         ||         
  RFC1874          ||       E. Levinson         ||        ELevinson@Accurate.com 
  RFC1875          ||       N. Berge         ||        Nils.Harald.Berge@nr.no 
  RFC1876          ||       C. Davis, P. Vixie, T. Goodwin, I. Dickinson         ||        ckd@kei.com, paul@vix.com, tim@pipex.net, idickins@fore.co.uk 
  RFC1877          ||       S. Cobb         ||        stevec@microsoft.com 
  RFC1878          ||       T. Pummill, B. Manning         ||        trop@alantec.com, bmanning@isi.edu 
  RFC1879          ||       B. Manning, Ed.         ||         
  RFC1880          ||       J. Postel, Ed.         ||         
  RFC1881          ||       IAB, IESG         ||         
  RFC1882          ||       B. Hancock         ||        hancock@network-1.com 
  RFC1883          ||      S. Deering, R. Hinden         ||       bob.hinden@gmail.com
  RFC1884          ||      R. Hinden, Ed., S. Deering, Ed.         ||       bob.hinden@gmail.com
  RFC1885          ||       A. Conta, S. Deering         ||        deering@parc.xerox.com 
  RFC1886          ||       S. Thomson, C. Huitema         ||        set@thumper.bellcore.com, Christian.Huitema@MIRSA.INRIA.FR 
  RFC1887          ||      Y. Rekhter, Ed., T. Li, Ed.         ||       
  RFC1888          ||       J. Bound, B. Carpenter, D. Harrington, J. Houldsworth, A. Lloyd         ||         
  RFC1889          ||       Audio-Video Transport Working Group, H. Schulzrinne, S. Casner, R. Frederick, V. Jacobson         ||        schulzrinne@fokus.gmd.de, casner@precept.com, frederic@parc.xerox.com, van@ee.lbl.gov 
  RFC1890          ||       Audio-Video Transport Working Group, H. Schulzrinne         ||        schulzrinne@fokus.gmd.de 
  RFC1891          ||       K. Moore         ||        moore@cs.utk.edu 
  RFC1892          ||       G. Vaudreuil         ||        Greg.Vaudreuil@Octel.com 
  RFC1893          ||       G. Vaudreuil         ||        Greg.Vaudreuil@Octel.com 
  RFC1894          ||       K. Moore, G. Vaudreuil         ||        moore@cs.utk.edu, Greg.Vaudreuil@Octel.Com 
  RFC1895          ||       E. Levinson         ||        ELevinson@Accurate.com 
  RFC1896          ||      P. Resnick, A. Walker         ||       presnick@qti.qualcomm.com, amanda@intercon.com
  RFC1897          ||      R. Hinden, J. Postel         ||       bob.hinden@gmail.com, postel@isi.edu
  RFC1898          ||       D. Eastlake 3rd, B. Boesch, S. Crocker, M. Yesil         ||        dee@cybercash.com, boesch@cybercash.com, crocker@cybercash.com, magdalen@cybercash.com 
  RFC1899          ||       J. Elliott         ||        elliott@isi.edu 
  RFC1900          ||       B. Carpenter, Y. Rekhter         ||        brian@dxcoms.cern.ch, yakov@cisco.com 
  RFC1901          ||       J. Case, K. McCloghrie, M. Rose, S. Waldbusser         ||         
  RFC1902          ||       J. Case, K. McCloghrie, M. Rose, S. Waldbusser         ||         
  RFC1903          ||       J. Case, K. McCloghrie, M. Rose, S. Waldbusser         ||         
  RFC1904          ||       J. Case, K. McCloghrie, M. Rose, S. Waldbusser         ||         
  RFC1905          ||       J. Case, K. McCloghrie, M. Rose, S. Waldbusser         ||         
  RFC1906          ||       J. Case, K. McCloghrie, M. Rose, S. Waldbusser         ||         
  RFC1907          ||       J. Case, K. McCloghrie, M. Rose, S. Waldbusser         ||         
  RFC1908          ||       J. Case, K. McCloghrie, M. Rose, S. Waldbusser         ||         
  RFC1909          ||       K. McCloghrie, Ed.         ||         
  RFC1910          ||       G. Waters, Ed.         ||         
  RFC1911          ||       G. Vaudreuil         ||        Greg.Vaudreuil@Octel.Com 
  RFC1912          ||       D. Barr         ||        barr@math.psu.edu 
  RFC1913          ||       C. Weider, J. Fullton, S. Spero         ||        clw@bunyip.com, fullton@cnidr.org, ses@eit.com 
  RFC1914          ||       P. Faltstrom, R. Schoultz, C. Weider         ||        paf@bunyip.com, schoultz@sunet.se, clw@bunyip.com 
  RFC1915          ||       F. Kastenholz         ||        kasten@ftp.com 
  RFC1916          ||       H. Berkowitz, P. Ferguson, W. Leland, P. Nesser         ||        hcb@clark.net, pferguso@cisco.com, wel@bellcore.com, pjnesser@rocket.com 
  RFC1917          ||       P. Nesser II         ||        pjnesser@martigny.ai.mit.edu 
  RFC1918          ||      Y. Rekhter, B. Moskowitz, D. Karrenberg, G. J. de Groot, E. Lear         ||       yakov@cisco.com, rgm3@is.chrysler.com, Daniel.Karrenberg@ripe.net, GeertJan.deGroot@ripe.net, lear@sgi.com
  RFC1919          ||       M. Chatel         ||        mchatel@pax.eunet.ch 
  RFC1920          ||       J. Postel         ||         
  RFC1921          ||       J. Dujonc         ||        J.Y.Dujonc@frcl.bull.fr 
  RFC1922          ||       HF. Zhu, DY. Hu, ZG. Wang, TC. Kao, WCH. Chang, M. Crispin         ||        zhf@net.tsinghua.edu.cn, hdy@tsinghua.edu.cn, tckao@iiidns.iii.org.tw, chung@iiidns.iii.org.tw, MRC@CAC.Washington.EDU 
  RFC1923          ||       J. Halpern, S. Bradner         ||        jhalpern@newbridge.com, sob@harvard.edu 
  RFC1924          ||       R. Elz         ||        kre@munnari.OZ.AU 
  RFC1925          ||       R. Callon         ||        rcallon@baynetworks.com 
  RFC1926          ||       J. Eriksson         ||        bygg@sunet.se 
  RFC1927          ||       C. Rogers         ||        rogers@isi.edu 
  RFC1928          ||       M. Leech, M. Ganis, Y. Lee, R. Kuris, D. Koblas, L. Jones         ||        mleech@bnr.ca 
  RFC1929          ||       M. Leech         ||        mleech@bnr.ca 
  RFC1930          ||      J. Hawkinson, T. Bates         ||       jhawk@bbnplanet.com, Tony.Bates@mci.net
  RFC1931          ||       D. Brownell         ||        dbrownell@sun.com 
  RFC1932          ||       R. Cole, D. Shur, C. Villamizar         ||        rgc@qsun.att.com, d.shur@att.com, curtis@ans.net 
  RFC1933          ||       R. Gilligan, E. Nordmark         ||        Bob.Gilligan@Eng.Sun.COM, Erik.Nordmark@Eng.Sun.COM 
  RFC1934          ||       K. Smith         ||        ksmith@ascend.com 
  RFC1935          ||       J. Quarterman, S. Carl-Mitchell         ||        tic@tic.com 
  RFC1936          ||       J. Touch, B. Parham         ||        touch@isi.edu, bparham@isi.edu 
  RFC1937          ||       Y. Rekhter, D. Kandlur         ||        yakov@cisco.com, kandlur@watson.ibm.com 
  RFC1938          ||       N. Haller, C. Metz         ||         
  RFC1939          ||      J. Myers, M. Rose         ||       mrose17@gmail.com
  RFC1940          ||       D. Estrin, T. Li, Y. Rekhter, K. Varadhan, D. Zappala         ||        estrin@isi.edu, tli@cisco.com, yakov@cisco.com, kannan@isi.edu, daniel@isi.edu 
  RFC1941          ||       J. Sellers, J. Robichaux         ||        julier@internic.net, sellers@quest.arc.nasa.gov 
  RFC1942          ||       D. Raggett         ||        dsr@w3.org 
  RFC1943          ||       B. Jennings         ||        jennings@sandia.gov 
  RFC1944          ||       S. Bradner, J. McQuaid         ||         
  RFC1945          ||       T. Berners-Lee, R. Fielding, H. Frystyk         ||        timbl@w3.org, fielding@ics.uci.edu, frystyk@w3.org 
  RFC1946          ||       S. Jackowski         ||        Stevej@NetManage.com 
  RFC1947          ||       D. Spinellis         ||        D.Spinellis@senanet.com 
  RFC1948          ||      S. Bellovin         ||       smb@research.att.com
  RFC1949          ||       A. Ballardie         ||        A.Ballardie@cs.ucl.ac.uk 
  RFC1950          ||       P. Deutsch, J-L. Gailly         ||         
  RFC1951          ||       P. Deutsch         ||         
  RFC1952          ||       P. Deutsch         ||         
  RFC1953          ||      P. Newman, W. Edwards, R. Hinden, E. Hoffman, F. Ching Liaw, T. Lyon, G. Minshall         ||       bob.hinden@gmail.com
  RFC1954          ||      P. Newman, W. Edwards, R. Hinden, E. Hoffman, F. Ching Liaw, T. Lyon, G. Minshall         ||       bob.hinden@gmail.com
  RFC1955          ||      R. Hinden         ||       bob.hinden@gmail.com
  RFC1956          ||       D. Engebretson, R. Plzak         ||        engebred@ncr.disa.mil, plzak@nic.ddn.mil 
  RFC1957          ||       R. Nelson         ||        nelson@crynwr.com 
  RFC1958          ||       B. Carpenter, Ed.         ||         
  RFC1959          ||       T. Howes, M. Smith         ||        tim@umich.edu, mcs@umich.edu 
  RFC1960          ||       T. Howes         ||        tim@umich.edu 
  RFC1961          ||       P. McMahon         ||        p.v.mcmahon@rea0803.wins.icl.co.uk 
  RFC1962          ||       D. Rand         ||        dlr@daver.bungi.com 
  RFC1963          ||       K. Schneider, S. Venters         ||        kevin@adtran.com, sventers@adtran.com 
  RFC1964          ||      J. Linn         ||       
  RFC1965          ||       P. Traina         ||        pst@cisco.com 
  RFC1966          ||       T. Bates, R. Chandra         ||        tbates@cisco.com, rchandra@cisco.com 
  RFC1967          ||       K. Schneider, R. Friend         ||        kschneider@adtran.com, rfriend@stac.com 
  RFC1968          ||       G. Meyer         ||        gerry@spider.co.uk 
  RFC1969          ||       K. Sklower, G. Meyer         ||        sklower@CS.Berkeley.EDU, gerry@spider.co.uk 
  RFC1970          ||       T. Narten, E. Nordmark, W. Simpson         ||         
  RFC1971          ||       S. Thomson, T. Narten         ||         
  RFC1972          ||       M. Crawford         ||        crawdad@fnal.gov 
  RFC1973          ||       W. Simpson         ||         
  RFC1974          ||       R. Friend, W. Simpson         ||        rfriend@stac.com 
  RFC1975          ||       D. Schremp, J. Black, J. Weiss         ||        dhs@magna.telco.com, jtb@magna.telco.com, jaw@magna.telco.com 
  RFC1976          ||       K. Schneider, S. Venters         ||        kevin@adtran.com, sventers@adtran.com 
  RFC1977          ||       V. Schryver         ||        vjs@rhyolite.com 
  RFC1978          ||       D. Rand         ||        dave_rand@novell.com 
  RFC1979          ||       J. Woods         ||        jfw@funhouse.com 
  RFC1980          ||      J. Seidman         ||       jim@spyglass.com
  RFC1981          ||       J. McCann, S. Deering, J. Mogul         ||        deering@parc.xerox.com, mogul@pa.dec.com 
  RFC1982          ||       R. Elz, R. Bush         ||        randy@psg.com 
  RFC1983          ||       G. Malkin, Ed.         ||         
  RFC1984          ||      IAB, IESG         ||       brian@dxcoms.cern.ch, fred@cisco.com
  RFC1985          ||       J. De Winter         ||        jack@wildbear.on.ca 
  RFC1986          ||       W. Polites, W. Wollman, D. Woo, R. Langan         ||         
  RFC1987          ||      P. Newman, W. Edwards, R. Hinden, E. Hoffman, F. Ching Liaw, T. Lyon, G. Minshall         ||       bob.hinden@gmail.com
  RFC1988          ||       G. McAnally, D. Gilbert, J. Flick         ||        johnf@hprnd.rose.hp.com 
  RFC1989          ||       W. Simpson         ||         
  RFC1990          ||       K. Sklower, B. Lloyd, G. McGregor, D. Carr, T. Coradetti         ||        sklower@CS.Berkeley.EDU, brian@lloyd.com, glenn@lloyd.com, dcarr@Newbridge.COM, 70761.1664@compuserve.com 
  RFC1991          ||      D. Atkins, W. Stallings, P. Zimmermann         ||       warlord@MIT.EDU, stallings@ACM.org, prz@acm.org
  RFC1992          ||       I. Castineyra, N. Chiappa, M. Steenstrup         ||        isidro@bbn.com, gnc@ginger.lcs.mit.edu, msteenst@bbn.com 
  RFC1993          ||       A. Barbir, D. Carr, W. Simpson         ||         
  RFC1994          ||       W. Simpson         ||         
  RFC1995          ||       M. Ohta         ||        mohta@necom830.hpcl.titech.ac.jp 
  RFC1996          ||       P. Vixie         ||        paul@vix.com 
  RFC1997          ||      R. Chandra, P. Traina, T. Li         ||       pst@cisco.com, rchandra@cisco.com, tli@skat.usc.edu
  RFC1998          ||       E. Chen, T. Bates         ||        enke@mci.net, tbates@cisco.com 
  RFC1999          ||       J. Elliott         ||        elliott@isi.edu 
  RFC2000          ||       J. Postel, Ed.         ||         
  RFC2001          ||       W. Stevens         ||        rstevens@noao.edu 
  RFC2002          ||       C. Perkins, Ed.         ||         
  RFC2003          ||      C. Perkins         ||       perk@watson.ibm.com, solomon@comm.mot.com
  RFC2004          ||       C. Perkins         ||        perk@watson.ibm.com, solomon@comm.mot.com 
  RFC2005          ||       J. Solomon         ||        solomon@comm.mot.com 
  RFC2006          ||       D. Cong, M. Hamlen, C. Perkins         ||         
  RFC2007          ||       J. Foster, M. Isaacs, M. Prior         ||        Jill.Foster@newcastle.ac.uk, mmi@dcs.gla.ac.uk, mrp@connect.com.au 
  RFC2008          ||       Y. Rekhter, T. Li         ||        yakov@cisco.com, tli@cisco.com 
  RFC2009          ||       T. Imielinski, J. Navas         ||         
  RFC2010          ||       B. Manning, P. Vixie         ||        bmanning@isi.edu, paul@vix.com 
  RFC2011          ||       K. McCloghrie, Ed.         ||         
  RFC2012          ||       K. McCloghrie, Ed.         ||         
  RFC2013          ||       K. McCloghrie, Ed.         ||         
  RFC2014          ||      A. Weinrib, J. Postel         ||       
  RFC2015          ||       M. Elkins         ||         
  RFC2016          ||       L. Daigle, P. Deutsch, B. Heelan, C. Alpaugh, M. Maclachlan         ||        ura-bunyip@bunyip.com 
  RFC2017          ||       N. Freed, K. Moore, A. Cargille         ||        ned@innosoft.com, moore@cs.utk.edu 
  RFC2018          ||       M. Mathis, J. Mahdavi, S. Floyd, A. Romanow         ||         
  RFC2019          ||       M. Crawford         ||        crawdad@fnal.gov 
  RFC2020          ||       J. Flick         ||         
  RFC2021          ||       S. Waldbusser         ||        waldbusser@ins.com 
  RFC2022          ||       G. Armitage         ||        gja@thumper.bellcore.com 
  RFC2023          ||       D. Haskin, E. Allen         ||         
  RFC2024          ||       D. Chen, Ed., P. Gayek, S. Nix         ||        dchen@vnet.ibm.com, gayek@vnet.ibm.com, snix@metaplex.com 
  RFC2025          ||       C. Adams         ||        cadams@bnr.ca 
  RFC2026          ||      S. Bradner         ||       
  RFC2027          ||       J. Galvin         ||         
  RFC2028          ||       R. Hovey, S. Bradner         ||        hovey@wnpv01.enet.dec.com, sob@harvard.edu 
  RFC2029          ||       M. Speer, D. Hoffman         ||        michael.speer@eng.sun.com, don.hoffman@eng.sun.com 
  RFC2030          ||       D. Mills         ||         
  RFC2031          ||       E. Huizer         ||         
  RFC2032          ||       T. Turletti, C. Huitema         ||        turletti@sophia.inria.fr, huitema@bellcore.com 
  RFC2033          ||       J. Myers         ||         
  RFC2034          ||       N. Freed         ||         
  RFC2035          ||       L. Berc, W. Fenner, R. Frederick, S. McCanne         ||        berc@pa.dec.com, fenner@cmf.nrl.navy.mil, frederick@parc.xerox.com, mccanne@ee.lbl.gov 
  RFC2036          ||       G. Huston         ||         
  RFC2037          ||       K. McCloghrie, A. Bierman         ||        kzm@cisco.com, andy@yumaworks.com
  RFC2038          ||       D. Hoffman, G. Fernando, V. Goyal         ||        gerard.fernando@eng.sun.com, goyal@precept.com, don.hoffman@eng.sun.com 
  RFC2039          ||       C. Kalbfleisch         ||         
  RFC2040          ||       R. Baldwin, R. Rivest         ||        baldwin@rsa.com, rivest@theory.lcs.mit.edu 
  RFC2041          ||      B. Noble, G. Nguyen, M. Satyanarayanan, R. Katz         ||       bnoble@cs.cmu.edu, gnguyen@cs.berkeley.edu, satya@cs.cmu.edu, randy@cs.berkeley.edu
  RFC2042          ||       B. Manning         ||        bmanning@isi.edu 
  RFC2043          ||       A. Fuqua         ||        fuqua@vnet.ibm.com 
  RFC2044          ||       F. Yergeau         ||        fyergeau@alis.com 
  RFC2045          ||      N. Freed, N. Borenstein         ||       ned@innosoft.com, nsb@nsb.fv.com, Greg.Vaudreuil@Octel.Com
  RFC2046          ||      N. Freed, N. Borenstein         ||       ned@innosoft.com, nsb@nsb.fv.com, Greg.Vaudreuil@Octel.Com
  RFC2047          ||       K. Moore         ||        moore@cs.utk.edu 
  RFC2048          ||       N. Freed, J. Klensin, J. Postel         ||        ned@innosoft.com, klensin@mci.net, Postel@ISI.EDU 
  RFC2049          ||       N. Freed, N. Borenstein         ||        ned@innosoft.com, nsb@nsb.fv.com, Greg.Vaudreuil@Octel.Com 
  RFC2050          ||      K. Hubbard, M. Kosters, D. Conrad, D. Karrenberg, J. Postel         ||       kimh@internic.net, markk@internic.net, davidc@APNIC.NET, dfk@RIPE.NET, Postel@ISI.EDU
  RFC2051          ||       M. Allen, B. Clouston, Z. Kielczewski, W. Kwan, B. Moore         ||        mallen@hq.walldata.com, clouston@cisco.com, zbig@cisco.com, billk@jti.com, remoore@ralvm6.vnet.ibm.com 
  RFC2052          ||       A. Gulbrandsen, P. Vixie         ||        agulbra@troll.no, paul@vix.com 
  RFC2053          ||       E. Der-Danieliantz         ||        edd@acm.org 
  RFC2054          ||       B. Callaghan         ||        brent.callaghan@eng.sun.com 
  RFC2055          ||       B. Callaghan         ||        brent.callaghan@eng.sun.com 
  RFC2056          ||       R. Denenberg, J. Kunze, D. Lynch         ||         
  RFC2057          ||       S. Bradner         ||        sob@harvard.edu 
  RFC2058          ||       C. Rigney, A. Rubens, W. Simpson, S. Willens         ||        cdr@livingston.com, acr@merit.edu, wsimpson@greendragon.com, steve@livingston.com 
  RFC2059          ||       C. Rigney         ||        cdr@livingston.com 
  RFC2060          ||       M. Crispin         ||        MRC@CAC.Washington.EDU 
  RFC2061          ||       M. Crispin         ||        MRC@CAC.Washington.EDU 
  RFC2062          ||       M. Crispin         ||        MRC@CAC.Washington.EDU 
  RFC2063          ||       N. Brownlee, C. Mills, G. Ruth         ||        cmills@bbn.com, gruth@gte.com 
  RFC2064          ||       N. Brownlee         ||         
  RFC2065          ||       D. Eastlake 3rd, C. Kaufman         ||        dee@cybercash.com, charlie_kaufman@iris.com 
  RFC2066          ||       R. Gellens         ||        Randy@MV.Unisys.Com 
  RFC2067          ||       J. Renwick         ||        jkr@NetStar.com 
  RFC2068          ||       R. Fielding, J. Gettys, J. Mogul, H. Frystyk, T. Berners-Lee         ||        fielding@ics.uci.edu, jg@w3.org, mogul@wrl.dec.com, frystyk@w3.org, timbl@w3.org 
  RFC2069          ||       J. Franks, P. Hallam-Baker, J. Hostetler, P. Leach, A. Luotonen, E. Sink, L. Stewart         ||        john@math.nwu.edu, hallam@w3.org, jeff@spyglass.com, paulle@microsoft.com, luotonen@netscape.com, eric@spyglass.com, stewart@OpenMarket.com 
  RFC2070          ||       F. Yergeau, G. Nicol, G. Adams, M. Duerst         ||        fyergeau@alis.com, gtn@ebt.com, glenn@spyglass.com, mduerst@ifi.unizh.ch 
  RFC2071          ||       P. Ferguson, H. Berkowitz         ||        pferguso@cisco.com, hcb@clark.net 
  RFC2072          ||       H. Berkowitz         ||        hcb@clark.net 
  RFC2073          ||      Y. Rekhter, P. Lothberg, R. Hinden, S. Deering, J. Postel         ||       bob.hinden@gmail.com
  RFC2074          ||       A. Bierman, R. Iddon         ||       andy@yumaworks.com, robin_iddon@3mail.3com.com 
  RFC2075          ||       C. Partridge         ||        craig@bbn.com 
  RFC2076          ||       J. Palme         ||         
  RFC2077          ||       S. Nelson, C. Parks, Mitra         ||         
  RFC2078          ||       J. Linn         ||        John.Linn@ov.com 
  RFC2079          ||       M. Smith         ||        mcs@netscape.com 
  RFC2080          ||       G. Malkin, R. Minnear         ||        gmalkin@Xylogics.COM, minnear@ipsilon.com 
  RFC2081          ||       G. Malkin         ||        gmalkin@xylogics.com 
  RFC2082          ||       F. Baker, R. Atkinson         ||        rja@cisco.com 
  RFC2083          ||       T. Boutell         ||        boutell@boutell.com 
  RFC2084          ||       G. Bossert, S. Cooper, W. Drummond         ||        bossert@corp.sgi.com, sc@corp.sgi.com, drummond@ieee.org 
  RFC2085          ||       M. Oehler, R. Glenn         ||        mjo@tycho.ncsc.mil, rob.glenn@nist.gov 
  RFC2086          ||       J. Myers         ||         
  RFC2087          ||       J. Myers         ||         
  RFC2088          ||      J. Myers         ||       
  RFC2089          ||       B. Wijnen, D. Levi         ||         
  RFC2090          ||       A. Emberson         ||        tom@lanworks.com 
  RFC2091          ||       G. Meyer, S. Sherry         ||         
  RFC2092          ||       S. Sherry, G. Meyer         ||         
  RFC2093          ||       H. Harney, C. Muckenhirn         ||         
  RFC2094          ||       H. Harney, C. Muckenhirn         ||         
  RFC2095          ||       J. Klensin, R. Catoe, P. Krumviede         ||        klensin@mci.net, randy@mci.net, paul@mci.net 
  RFC2096          ||       F. Baker         ||        fred@cisco.com 
  RFC2097          ||       G. Pall         ||        gurdeep@microsoft.com 
  RFC2098          ||       Y. Katsube, K. Nagami, H. Esaki         ||         
  RFC2099          ||       J. Elliott         ||        elliott@isi.edu 
  RFC2100          ||       J. Ashworth         ||        jra@scfn.thpl.lib.fl.us 
  RFC2101          ||       B. Carpenter, J. Crowcroft, Y. Rekhter         ||        brian@dxcoms.cern.ch, j.crowcroft@cs.ucl.ac.uk, yakov@cisco.com 
  RFC2102          ||       R. Ramanathan         ||        ramanath@bbn.com 
  RFC2103          ||       R. Ramanathan         ||         
  RFC2104          ||      H. Krawczyk, M. Bellare, R. Canetti         ||       hugo@watson.ibm.com, mihir@cs.ucsd.edu, canetti@watson.ibm.com
  RFC2105          ||       Y. Rekhter, B. Davie, D. Katz, E. Rosen, G. Swallow         ||        yakov@cisco.com, bsd@cisco.com, dkatz@cisco.com, erosen@cisco.com, swallow@cisco.com 
  RFC2106          ||       S. Chiang, J. Lee, H. Yasuda         ||        schiang@cisco.com, jolee@cisco.com, yasuda@eme068.cow.melco.co.jp 
  RFC2107          ||       K. Hamzeh         ||        kory@ascend.com 
  RFC2108          ||       K. de Graaf, D. Romascanu, D. McMaster, K. McCloghrie         ||        kdegraaf@isd.3com.com, dromasca@gmail.com , mcmaster@cisco.com, kzm@cisco.com 
  RFC2109          ||      D. Kristol, L. Montulli         ||       
  RFC2110          ||       J. Palme, A. Hopmann         ||         
  RFC2111          ||       E. Levinson         ||         
  RFC2112          ||       E. Levinson         ||         
  RFC2113          ||      D. Katz         ||       
  RFC2114          ||       S. Chiang, J. Lee, H. Yasuda         ||        schiang@cisco.com, jolee@cisco.com, yasuda@eme068.cow.melco.co.jp 
  RFC2115          ||       C. Brown, F. Baker         ||         
  RFC2116          ||       C. Apple, K. Rossen         ||         
  RFC2117          ||       D. Estrin, D. Farinacci, A. Helmy, D. Thaler, S. Deering, M. Handley, V. Jacobson, C. Liu, P. Sharma, L. Wei         ||         
  RFC2118          ||       G. Pall         ||         
  RFC2119          ||      S. Bradner         ||       
  RFC2120          ||       D. Chadwick         ||         
  RFC2121          ||       G. Armitage         ||        gja@thumper.bellcore.com 
  RFC2122          ||       D. Mavrakis, H. Layec, K. Kartmann         ||         
  RFC2123          ||       N. Brownlee         ||         
  RFC2124          ||       P. Amsden, J. Amweg, P. Calato, S. Bensley, G. Lyons         ||        amsden@ctron.com, amsden@ctron.com, amsden@ctron.com, amsden@ctron.com, amsden@ctron.com 
  RFC2125          ||       C. Richards, K. Smith         ||         
  RFC2126          ||       Y. Pouffary, A. Young         ||        pouffary@taec.enet.dec.com, A.Young@isode.com 
  RFC2127          ||       G. Roeck, Ed.         ||        groeck@cisco.com 
  RFC2128          ||       G. Roeck, Ed.         ||        groeck@cisco.com 
  RFC2129          ||      K. Nagami, Y. Katsube, Y. Shobatake, A. Mogi, S. Matsuzawa, T. Jinmei, H. Esaki         ||       
  RFC2130          ||      C. Weider, C. Preston, K. Simonsen, H. Alvestrand, R. Atkinson, M. Crispin, P. Svanberg         ||       cweider@microsoft.com, cecilia@well.com, Keld@dkuug.dk, Harald.T.Alvestrand@uninett.no, rja@cisco.com, mrc@cac.washington.edu, psv@nada.kth.se
  RFC2131          ||      R. Droms         ||       droms@bucknell.edu
  RFC2132          ||      S. Alexander, R. Droms         ||       sca@engr.sgi.com, droms@bucknell.edu
  RFC2133          ||       R. Gilligan, S. Thomson, J. Bound, W. Stevens         ||        gilligan@freegate.net, set@thumper.bellcore.com, rstevens@kohala.com 
  RFC2134          ||       ISOC Board of Trustees         ||         
  RFC2135          ||       ISOC Board of Trustees         ||         
  RFC2136          ||      P. Vixie, Ed., S. Thomson, Y. Rekhter, J. Bound         ||       yakov@cisco.com, set@thumper.bellcore.com, bound@zk3.dec.com, paul@vix.com 
  RFC2137          ||       D. Eastlake 3rd         ||        dee@cybercash.com 
  RFC2138          ||       C. Rigney, A. Rubens, W. Simpson, S. Willens         ||        cdr@livingston.com, acr@merit.edu, wsimpson@greendragon.com, steve@livingston.com 
  RFC2139          ||       C. Rigney         ||        cdr@livingston.com 
  RFC2140          ||       J. Touch         ||         
  RFC2141          ||       R. Moats         ||         
  RFC2142          ||       D. Crocker         ||         
  RFC2143          ||       B. Elliston         ||         
  RFC2144          ||       C. Adams         ||         
  RFC2145          ||      J. C. Mogul, R. Fielding, J. Gettys, H. Frystyk         ||       
  RFC2146          ||       Federal Networking Council         ||        execdir@fnc.gov 
  RFC2147          ||       D. Borman         ||         
  RFC2148          ||       H. Alvestrand, P. Jurg         ||         
  RFC2149          ||       R. Talpade, M. Ammar         ||         
  RFC2150          ||       J. Max, W. Stickle         ||        jlm@rainfarm.com, wls@rainfarm.com 
  RFC2151          ||       G. Kessler, S. Shepard         ||         
  RFC2152          ||       D. Goldsmith, M. Davis         ||        goldsmith@apple.com, mark_davis@taligent.com 
  RFC2153          ||      W. Simpson         ||       
  RFC2154          ||       S. Murphy, M. Badger, B. Wellington         ||         
  RFC2155          ||       B. Clouston, B. Moore         ||         
  RFC2156          ||       S. Kille         ||         
  RFC2157          ||       H. Alvestrand         ||        Harald.T.Alvestrand@uninett.no 
  RFC2158          ||       H. Alvestrand         ||        Harald.T.Alvestrand@uninett.no 
  RFC2159          ||       H. Alvestrand         ||        Harald.T.Alvestrand@uninett.no 
  RFC2160          ||       H. Alvestrand         ||        Harald.T.Alvestrand@uninett.no 
  RFC2161          ||       H. Alvestrand         ||        Harald.T.Alvestrand@uninett.no 
  RFC2162          ||       C. Allocchio         ||        Claudio.Allocchio@elettra.Trieste.it 
  RFC2163          ||       C. Allocchio         ||         
  RFC2164          ||       S. Kille         ||        S.Kille@ISODE.COM 
  RFC2165          ||       J. Veizades, E. Guttman, C. Perkins, S. Kaplan         ||        cperkins@Corp.sun.com 
  RFC2166          ||       D. Bryant, P. Brittain         ||         
  RFC2167          ||       S. Williamson, M. Kosters, D. Blacka, J. Singh, K. Zeilstra         ||         
  RFC2168          ||       R. Daniel, M. Mealling         ||         
  RFC2169          ||       R. Daniel         ||         
  RFC2170          ||       W. Almesberger, J. Le Boudec, P. Oechslin         ||         
  RFC2171          ||       K. Murakami, M. Maruyama         ||         
  RFC2172          ||       M. Maruyama, K. Murakami         ||         
  RFC2173          ||       K. Murakami, M. Maruyama         ||         
  RFC2174          ||       K. Murakami, M. Maruyama         ||         
  RFC2175          ||       K. Murakami, M. Maruyama         ||         
  RFC2176          ||      K. Murakami, M. Maruyama         ||       
  RFC2177          ||       B. Leiba         ||         
  RFC2178          ||      J. Moy         ||       jmoy@casc.com
  RFC2179          ||       A. Gwinn         ||        allen@mail.cox.smu.edu, ssh@wwsi.com 
  RFC2180          ||       M. Gahrns         ||        mikega@microsoft.com 
  RFC2181          ||      R. Elz, R. Bush         ||       kre@munnari.OZ.AU, randy@psg.com
  RFC2182          ||       R. Elz, R. Bush, S. Bradner, M. Patton         ||        kre@munnari.OZ.AU, randy@psg.com, sob@harvard.edu, MAP@POBOX.COM 
  RFC2183          ||      R. Troost, S. Dorner, K. Moore, Ed.         ||       rens@century.com, sdorner@qualcomm.com
  RFC2184          ||       N. Freed, K. Moore         ||         
  RFC2185          ||       R. Callon, D. Haskin         ||         
  RFC2186          ||       D. Wessels, K. Claffy         ||        wessels@nlanr.net, kc@nlanr.net 
  RFC2187          ||       D. Wessels, K. Claffy         ||        wessels@nlanr.net, kc@nlanr.net 
  RFC2188          ||       M. Banan, M. Taylor, J. Cheng         ||         
  RFC2189          ||      A. Ballardie         ||       
  RFC2190          ||       C. Zhu         ||        czhu@ibeam.intel.com 
  RFC2191          ||       G. Armitage         ||        gja@dnrc.bell-labs.com 
  RFC2192          ||      C. Newman         ||       chris.newman@innosoft.com
  RFC2193          ||       M. Gahrns         ||        mikega@microsoft.com 
  RFC2194          ||       B. Aboba, J. Lu, J. Alsop, J. Ding, W. Wang         ||        bernarda@microsoft.com, juanlu@aimnet.net, jalsop@ipass.com, ding@bjai.asiainfo.com, weiwang@merit.edu 
  RFC2195          ||       J. Klensin, R. Catoe, P. Krumviede         ||        klensin@mci.net, randy@mci.net, paul@mci.net 
  RFC2196          ||       B. Fraser         ||         
  RFC2197          ||       N. Freed         ||        ned.freed@innosoft.com 
  RFC2198          ||      C. Perkins, I. Kouvelas, O. Hodson, V. Hardman, M. Handley, J.C. Bolot, A. Vega-Garcia, S. Fosse-Parisis         ||       mjh@isi.edu
  RFC2199          ||       A. Ramos         ||        ramos@isi.edu 
  RFC2200          ||       J. Postel         ||         
  RFC2201          ||      A. Ballardie         ||       
  RFC2202          ||       P. Cheng, R. Glenn         ||        pau@watson.ibm.com, rob.glenn@nist.gov 
  RFC2203          ||      M. Eisler, A. Chiu, L. Ling         ||       mre@eng.sun.com, hacker@eng.sun.com, lling@eng.sun.com
  RFC2204          ||      D. Nash         ||       dnash@ford.com
  RFC2205          ||      R. Braden, Ed., L. Zhang, S. Berson, S. Herzog, S. Jamin         ||       Braden@ISI.EDU, lixia@cs.ucla.edu, Berson@ISI.EDU, Herzog@WATSON.IBM.COM, jamin@EECS.UMICH.EDU
  RFC2206          ||       F. Baker, J. Krawczyk, A. Sastry         ||        fred@cisco.com, jjk@tiac.net, arun@cisco.com 
  RFC2207          ||       L. Berger, T. O'Malley         ||        timo@bbn.com 
  RFC2208          ||      A. Mankin, Ed., F. Baker, B. Braden, S. Bradner, M. O'Dell, A. Romanow, A. Weinrib, L. Zhang         ||       aweinrib@ibeam.intel.com, braden@isi.edu, lixia@cs.ucla.edu, allyn@eng.sun.com, mo@uu.net
  RFC2209          ||       R. Braden, L. Zhang         ||        Braden@ISI.EDU, lixia@cs.ucla.edu 
  RFC2210          ||       J. Wroclawski         ||        jtw@lcs.mit.edu 
  RFC2211          ||       J. Wroclawski         ||        jtw@lcs.mit.edu 
  RFC2212          ||       S. Shenker, C. Partridge, R. Guerin         ||        shenker@parc.xerox.com, craig@bbn.com, guerin@watson.ibm.com 
  RFC2213          ||       F. Baker, J. Krawczyk, A. Sastry         ||        fred@cisco.com, jjk@tiac.net, arun@cisco.com 
  RFC2214          ||       F. Baker, J. Krawczyk, A. Sastry         ||        fred@cisco.com, jjk@tiac.net, arun@cisco.com 
  RFC2215          ||       S. Shenker, J. Wroclawski         ||        shenker@parc.xerox.com, jtw@lcs.mit.edu 
  RFC2216          ||       S. Shenker, J. Wroclawski         ||        shenker@parc.xerox.com, jtw@lcs.mit.edu 
  RFC2217          ||       G. Clark         ||        glenc@cisco.com 
  RFC2218          ||       T. Genovese, B. Jennings         ||        TonyG@Microsoft.com, jennings@sandia.gov 
  RFC2219          ||       M. Hamilton, R. Wright         ||        m.t.hamilton@lut.ac.uk, wright@lbl.gov 
  RFC2220          ||       R. Guenther         ||        rgue@loc.gov 
  RFC2221          ||       M. Gahrns         ||        mikega@microsoft.com 
  RFC2222          ||       J. Myers         ||        jgmyers@netscape.com 
  RFC2223          ||      J. Postel, J. Reynolds         ||       Postel@ISI.EDU, jkrey@isi.edu, dwaitzman@BBN.COM
  RFC2224          ||       B. Callaghan         ||        brent.callaghan@eng.sun.com 
  RFC2225          ||      M. Laubach, J. Halpern         ||       
  RFC2226          ||       T. Smith, G. Armitage         ||        tjsmith@vnet.ibm.com, gja@lucent.com 
  RFC2227          ||       J. Mogul, P. Leach         ||        mogul@wrl.dec.com, paulle@microsoft.com 
  RFC2228          ||       M. Horowitz, S. Lunt         ||        marc@cygnus.com 
  RFC2229          ||       R. Faith, B. Martin         ||        faith@cs.unc.edu, bamartin@miranda.org 
  RFC2230          ||       R. Atkinson         ||         
  RFC2231          ||      N. Freed, K. Moore         ||       ned.freed@innosoft.com, moore@cs.utk.edu
  RFC2232          ||       B. Clouston, Ed., B. Moore, Ed.         ||        clouston@cisco.com, remoore@ralvm6.vnet.ibm.com 
  RFC2233          ||       K. McCloghrie, F. Kastenholz         ||        kzm@cisco.com, kasten@ftp.com 
  RFC2234          ||      D. Crocker, Ed., P. Overell         ||       dcrocker@bbiw.net, paul@bayleaf.org.uk
  RFC2235          ||       R. Zakon         ||        zakon@info.isoc.org 
  RFC2236          ||      W. Fenner         ||       fenner@parc.xerox.com
  RFC2237          ||       K. Tamaru         ||        kenzat@microsoft.com 
  RFC2238          ||       B. Clouston, Ed., B. Moore, Ed.         ||        clouston@cisco.com, remoore@ralvm6.vnet.ibm.com 
  RFC2239          ||       K. de Graaf, D. Romascanu, D. McMaster, K. McCloghrie, S. Roberts         ||        kdegraaf@isd.3com.com, dromasca@gmail.com , mcmaster@cisco.com, kzm@cisco.com, sroberts@farallon.com 
  RFC2240          ||       O. Vaughan         ||        owain@vaughan.com 
  RFC2241          ||       D. Provan         ||        donp@Novell.Com 
  RFC2242          ||       R. Droms, K. Fong         ||         
  RFC2243          ||       C. Metz         ||         
  RFC2244          ||      C. Newman, J. G. Myers         ||       
  RFC2245          ||       C. Newman         ||         
  RFC2246          ||      T. Dierks, C. Allen         ||       tdierks@certicom.com, pck@netcom.com, relyea@netscape.com, jar@netscape.com, msabin@netcom.com, dansimon@microsoft.com, tomw@netscape.com, hugo@watson.ibm.com
  RFC2247          ||       S. Kille, M. Wahl, A. Grimstad, R. Huber, S. Sataluri         ||        S.Kille@ISODE.COM, M.Wahl@critical-angle.com, alg@att.com, rvh@att.com, sri@att.com 
  RFC2248          ||       N. Freed, S. Kille         ||        ned.freed@innosoft.com, S.Kille@isode.com 
  RFC2249          ||       N. Freed, S. Kille         ||        ned.freed@innosoft.com, S.Kille@isode.com 
  RFC2250          ||       D. Hoffman, G. Fernando, V. Goyal, M. Civanlar         ||        gerard.fernando@eng.sun.com, goyal@precept.com, don.hoffman@eng.sun.com, civanlar@research.att.com 
  RFC2251          ||       M. Wahl, T. Howes, S. Kille         ||        M.Wahl@critical-angle.com, howes@netscape.com, S.Kille@isode.com 
  RFC2252          ||       M. Wahl, A. Coulbeck, T. Howes, S. Kille         ||        M.Wahl@critical-angle.com, A.Coulbeck@isode.com, howes@netscape.com, S.Kille@isode.com 
  RFC2253          ||       M. Wahl, S. Kille, T. Howes         ||        M.Wahl@critical-angle.com, S.Kille@ISODE.COM, howes@netscape.com 
  RFC2254          ||       T. Howes         ||        howes@netscape.com 
  RFC2255          ||       T. Howes, M. Smith         ||        howes@netscape.com, mcs@netscape.com 
  RFC2256          ||       M. Wahl         ||        M.Wahl@critical-angle.com 
  RFC2257          ||       M. Daniele, B. Wijnen, D. Francisco         ||        daniele@zk3.dec.com, wijnen@vnet.ibm.com, dfrancis@cisco.com 
  RFC2258          ||       J. Ordille         ||        joann@bell-labs.com 
  RFC2259          ||       J. Elliott, J. Ordille         ||        jim@apocalypse.org, joann@bell-labs.com 
  RFC2260          ||       T. Bates, Y. Rekhter         ||        tbates@cisco.com, yakov@cisco.com 
  RFC2261          ||       D. Harrington, R. Presuhn, B. Wijnen         ||         
  RFC2262          ||       J. Case, D. Harrington, R. Presuhn, B. Wijnen         ||         
  RFC2263          ||       D. Levi, P. Meyer, B. Stewart         ||         
  RFC2264          ||       U. Blumenthal, B. Wijnen         ||         
  RFC2265          ||       B. Wijnen, R. Presuhn, K. McCloghrie         ||         
  RFC2266          ||       J. Flick         ||         
  RFC2267          ||       P. Ferguson, D. Senie         ||        ferguson@cisco.com, dts@senie.com 
  RFC2268          ||       R. Rivest         ||        rsa-labs@rsa.com 
  RFC2269          ||       G. Armitage         ||        gja@lucent.com 
  RFC2270          ||       J. Stewart, T. Bates, R. Chandra, E. Chen         ||        jstewart@isi.edu, tbates@cisco.com, rchandra@cisco.com, enkechen@cisco.com 
  RFC2271          ||       D. Harrington, R. Presuhn, B. Wijnen         ||         
  RFC2272          ||       J. Case, D. Harrington, R. Presuhn, B. Wijnen         ||         
  RFC2273          ||       D. Levi, P. Meyer, B. Stewart         ||         
  RFC2274          ||       U. Blumenthal, B. Wijnen         ||         
  RFC2275          ||       B. Wijnen, R. Presuhn, K. McCloghrie         ||         
  RFC2276          ||       K. Sollins         ||        sollins@lcs.mit.edu 
  RFC2277          ||       H. Alvestrand         ||        Harald.T.Alvestrand@uninett.no 
  RFC2278          ||       N. Freed, J. Postel         ||        ned.freed@innosoft.com, Postel@ISI.EDU 
  RFC2279          ||       F. Yergeau         ||        fyergeau@alis.com 
  RFC2280          ||       C. Alaettinoglu, T. Bates, E. Gerich, D. Karrenberg, D. Meyer, M. Terpstra, C. Villamizar         ||        cengiz@isi.edu, tbates@cisco.com, epg@home.net, dfk@ripe.net, meyer@antc.uoregon.edu, marten@BayNetworks.com, curtis@ans.net 
  RFC2281          ||       T. Li, B. Cole, P. Morton, D. Li         ||        tli@juniper.net, cole@juniper.net, pmorton@cisco.com, dawnli@cisco.com 
  RFC2282          ||       J. Galvin         ||         
  RFC2283          ||       T. Bates, R. Chandra, D. Katz, Y. Rekhter         ||         
  RFC2284          ||       L. Blunk, J. Vollbrecht         ||        ljb@merit.edu, jrv@merit.edu 
  RFC2285          ||       R. Mandeville         ||        bob.mandeville@eunet.fr 
  RFC2286          ||       J. Kapp         ||        skapp@reapertech.com 
  RFC2287          ||       C. Krupczak, J. Saperia         ||        cheryl@empiretech.com 
  RFC2288          ||       C. Lynch, C. Preston, R. Daniel         ||        cliff@cni.org, cecilia@well.com, rdaniel@acl.lanl.gov 
  RFC2289          ||       N. Haller, C. Metz, P. Nesser, M. Straw         ||         
  RFC2290          ||       J. Solomon, S. Glass         ||        solomon@comm.mot.com, glass@ftp.com 
  RFC2291          ||       J. Slein, F. Vitali, E. Whitehead, D. Durand         ||        slein@wrc.xerox.com, fabio@cs.unibo.it, ejw@ics.uci.edu, dgd@cs.bu.edu 
  RFC2292          ||       W. Stevens, M. Thomas         ||        rstevens@kohala.com, matt.thomas@altavista-software.com 
  RFC2293          ||       S. Kille         ||        S.Kille@ISODE.COM 
  RFC2294          ||       S. Kille         ||        S.Kille@ISODE.COM 
  RFC2295          ||       K. Holtman, A. Mutz         ||        koen@win.tue.nl, mutz@hpl.hp.com 
  RFC2296          ||       K. Holtman, A. Mutz         ||        koen@win.tue.nl, mutz@hpl.hp.com 
  RFC2297          ||      P. Newman, W. Edwards, R. Hinden, E. Hoffman, F. Ching Liaw, T. Lyon, G. Minshall         ||       bob.hinden@gmail.com
  RFC2298          ||       R. Fajman         ||        raf@cu.nih.gov 
  RFC2299          ||       A. Ramos         ||        ramos@isi.edu 
  RFC2300          ||       J. Postel         ||        Postel@ISI.EDU 
  RFC2301          ||       L. McIntyre, S. Zilles, R. Buckley, D. Venable, G. Parsons, J. Rafferty         ||         
  RFC2302          ||       G. Parsons, J. Rafferty, S. Zilles         ||         
  RFC2303          ||       C. Allocchio         ||         
  RFC2304          ||       C. Allocchio         ||         
  RFC2305          ||       K. Toyoda, H. Ohno, J. Murai, D. Wing         ||         
  RFC2306          ||       G. Parsons, J. Rafferty         ||         
  RFC2307          ||       L. Howard         ||        lukeh@xedoc.com 
  RFC2308          ||      M. Andrews         ||       Mark.Andrews@cmis.csiro.au
  RFC2309          ||      B. Braden, D. Clark, J. Crowcroft, B. Davie, S. Deering, D. Estrin, S. Floyd, V. Jacobson, G. Minshall, C. Partridge, L. Peterson, K. Ramakrishnan, S. Shenker, J. Wroclawski, L. Zhang         ||       Braden@ISI.EDU, DDC@lcs.mit.edu, Jon.Crowcroft@cs.ucl.ac.uk, bdavie@cisco.com, deering@cisco.com, Estrin@usc.edu, Floyd@ee.lbl.gov, Van@ee.lbl.gov, Minshall@fiberlane.com, craig@bbn.com, LLP@cs.arizona.edu, KKRama@research.att.com, Shenker@parc.xerox.com, JTW@lcs.mit.edu, Lixia@cs.ucla.edu
  RFC2310          ||       K. Holtman         ||        koen@win.tue.nl 
  RFC2311          ||      S. Dusse, P. Hoffman, B. Ramsdell, L. Lundblade, L. Repka         ||       spock@rsa.com, phoffman@imc.org, blaker@deming.com, lgl@qualcomm.com, repka@netscape.com
  RFC2312          ||      S. Dusse, P. Hoffman, B. Ramsdell, J. Weinstein         ||       spock@rsa.com, phoffman@imc.org, blaker@deming.com, jsw@netscape.com
  RFC2313          ||       B. Kaliski         ||        burt@rsa.com 
  RFC2314          ||       B. Kaliski         ||        burt@rsa.com 
  RFC2315          ||       B. Kaliski         ||        burt@rsa.com 
  RFC2316          ||       S. Bellovin         ||         
  RFC2317          ||       H. Eidnes, G. de Groot, P. Vixie         ||        Havard.Eidnes@runit.sintef.no, GeertJan.deGroot@bsdi.com, paul@vix.com 
  RFC2318          ||       H. Lie, B. Bos, C. Lilley         ||        howcome@w3.org, bert@w3.org, chris@w3.org 
  RFC2319          ||      KOI8-U Working Group         ||       
  RFC2320          ||       M. Greene, J. Luciani, K. White, T. Kuo         ||        maria@xedia.com, luciani@baynetworks.com, kennethw@vnet.ibm.com, ted_kuo@Baynetworks.com 
  RFC2321          ||       A. Bressen         ||        bressen@leftbank.com 
  RFC2322          ||       K. van den Hout, A. Koopal, R. van Mook         ||        koos@cetis.hvu.nl, andre@NL.net, remco@sateh.com 
  RFC2323          ||       A. Ramos         ||        ramos@isi.edu 
  RFC2324          ||      L. Masinter         ||       masinter@parc.xerox.com
  RFC2325          ||       M. Slavitch         ||        slavitch@loran.com 
  RFC2326          ||      H. Schulzrinne, A. Rao, R. Lanphier         ||       schulzrinne@cs.columbia.edu, anup@netscape.com, robla@real.com
  RFC2327          ||       M. Handley, V. Jacobson         ||         
  RFC2328          ||      J. Moy         ||       jmoy@casc.com
  RFC2329          ||       J. Moy         ||        jmoy@casc.com 
  RFC2330          ||      V. Paxson, G. Almes, J. Mahdavi, M. Mathis         ||       vern@ee.lbl.gov, almes@advanced.org, mahdavi@psc.edu, mathis@psc.edu
  RFC2331          ||       M. Maher         ||        maher@isi.edu 
  RFC2332          ||       J. Luciani, D. Katz, D. Piscitello, B. Cole, N. Doraswamy         ||        dkatz@cisco.com, luciani@baynetworks.com, bcole@jnx.com, naganand@baynetworks.com 
  RFC2333          ||       D. Cansever         ||        dcansever@gte.com 
  RFC2334          ||       J. Luciani, G. Armitage, J. Halpern, N. Doraswamy         ||        luciani@baynetworks.com, gja@lucent.com, jhalpern@Newbridge.COM, naganand@baynetworks.com 
  RFC2335          ||       J. Luciani         ||        luciani@baynetworks.com 
  RFC2336          ||      J. Luciani         ||       
  RFC2337          ||       D. Farinacci, D. Meyer, Y. Rekhter         ||         
  RFC2338          ||      S. Knight, D. Weaver, D. Whipple, R. Hinden, D. Mitzel, P. Hunt, P. Higginson, M. Shand, A. Lindem         ||       Steven.Knight@ascend.com, Doug.Weaver@ascend.com, dwhipple@microsoft.com, bob.hinden@gmail.com, mitzel@iprg.nokia.com, hunt@iprg.nokia.com, higginson@mail.dec.com, shand@mail.dec.com
  RFC2339          ||       The Internet Society, Sun Microsystems         ||         
  RFC2340          ||       B. Jamoussi, D. Jamieson, D. Williston, S. Gabe         ||        jamoussi@Nortel.ca, djamies@Nortel.ca, danwil@Nortel.ca, spgabe@Nortel.ca 
  RFC2341          ||       A. Valencia, M. Littlewood, T. Kolar         ||        tkolar@cisco.com, littlewo@cisco.com, valencia@cisco.com 
  RFC2342          ||       M. Gahrns, C. Newman         ||        mikega@microsoft.com, chris.newman@innosoft.com 
  RFC2343          ||       M. Civanlar, G. Cash, B. Haskell         ||        civanlar@research.att.com, glenn@research.att.com, bgh@research.att.com 
  RFC2344          ||       G. Montenegro, Ed.         ||         
  RFC2345          ||       J. Klensin, T. Wolf, G. Oglesby         ||        klensin@mci.net, ted@usa.net, gary@mci.net 
  RFC2346          ||       J. Palme         ||        jpalme@dsv.su.se 
  RFC2347          ||       G. Malkin, A. Harkin         ||        gmalkin@baynetworks.com, ash@cup.hp.com 
  RFC2348          ||       G. Malkin, A. Harkin         ||        gmalkin@baynetworks.com, ash@cup.hp.com 
  RFC2349          ||       G. Malkin, A. Harkin         ||        gmalkin@baynetworks.com, ash@cup.hp.com 
  RFC2350          ||       N. Brownlee, E. Guttman         ||        n.brownlee@auckland.ac.nz, Erik.Guttman@sun.com 
  RFC2351          ||       A. Robert         ||        arobert@par1.par.sita.int 
  RFC2352          ||       O. Vaughan         ||        owain@vaughan.com 
  RFC2353          ||       G. Dudley         ||        dudleyg@us.ibm.com 
  RFC2354          ||       C. Perkins, O. Hodson         ||        c.perkins@cs.ucl.ac.uk, o.hodson@cs.ucl.ac.uk 
  RFC2355          ||      B. Kelly         ||       kellywh@mail.auburn.edu
  RFC2356          ||       G. Montenegro, V. Gupta         ||        gabriel.montenegro@Eng.Sun.COM, vipul.gupta@Eng.Sun.COM 
  RFC2357          ||       A. Mankin, A. Romanow, S. Bradner, V. Paxson         ||        mankin@east.isi.edu, allyn@mci.net, sob@harvard.edu, vern@ee.lbl.gov 
  RFC2358          ||       J. Flick, J. Johnson         ||        johnf@hprnd.rose.hp.com, jeff@redbacknetworks.com 
  RFC2359          ||       J. Myers         ||        jgmyers@netscape.com 
  RFC2360          ||       G. Scott         ||         
  RFC2361          ||       E. Fleischman         ||        ericfl@microsoft.com, Eric.Fleischman@PSS.Boeing.com 
  RFC2362          ||      D. Estrin, D. Farinacci, A. Helmy, D. Thaler, S. Deering, M. Handley, V. Jacobson, C. Liu, P. Sharma, L. Wei         ||       estrin@usc.edu, dino@cisco.com, ahelmy@catarina.usc.edu, thalerd@eecs.umich.edu, deering@parc.xerox.com, m.handley@cs.ucl.ac.uk, van@ee.lbl.gov, charley@catarina.usc.edu, puneet@catarina.usc.edu, lwei@cisco.com
  RFC2363          ||       G. Gross, M. Kaycee, A. Li, A. Malis, J. Stephens         ||        gmgross@lucent.com, mjk@nj.paradyne.com, alin@shastanets.com, malis@ascend.com, john@cayman.com 
  RFC2364          ||       G. Gross, M. Kaycee, A. Li, A. Malis, J. Stephens         ||        gmgross@lucent.com, mjk@nj.paradyne.com, alin@shastanets.com, malis@ascend.com, john@cayman.com 
  RFC2365          ||       D. Meyer         ||        dmm@cisco.com 
  RFC2366          ||       C. Chung, M. Greene         ||        cchung@tieo.saic.com 
  RFC2367          ||       D. McDonald, C. Metz, B. Phan         ||        danmcd@eng.sun.com, cmetz@inner.net, phan@itd.nrl.navy.mil 
  RFC2368          ||      P. Hoffman, L. Masinter, J. Zawinski         ||       
  RFC2369          ||       G. Neufeld, J. Baer         ||         
  RFC2370          ||      R. Coltun         ||       
  RFC2371          ||       J. Lyon, K. Evans, J. Klein         ||        JimLyon@Microsoft.Com, Keith.Evans@Tandem.Com, Johannes.Klein@Tandem.Com 
  RFC2372          ||       K. Evans, J. Klein, J. Lyon         ||        Keith.Evans@Tandem.Com, Johannes.Klein@Tandem.Com, JimLyon@Microsoft.Com 
  RFC2373          ||      R. Hinden, S. Deering         ||       bob.hinden@gmail.com
  RFC2374          ||      R. Hinden, M. O'Dell, S. Deering         ||       bob.hinden@gmail.com, mo@uunet.uu.net, deering@cisco.com
  RFC2375          ||      R. Hinden, S. Deering         ||       bob.hinden@gmail.com, deering@cisco.com
  RFC2376          ||       E. Whitehead, M. Murata         ||         
  RFC2377          ||       A. Grimstad, R. Huber, S. Sataluri, M. Wahl         ||        alg@att.com, rvh@att.com, srs@lucent.com, M.Wahl@critical-angle.com 
  RFC2378          ||       R. Hedberg, P. Pomes         ||        Roland.Hedberg@umdac.umu.se, ppomes@qualcomm.com 
  RFC2379          ||       L. Berger         ||        lberger@fore.com 
  RFC2380          ||       L. Berger         ||        lberger@fore.com 
  RFC2381          ||       M. Garrett, M. Borden         ||        mwg@bellcore.com, mborden@baynetworks.com 
  RFC2382          ||       E. Crawley, Ed., L. Berger, S. Berson, F. Baker, M. Borden, J. Krawczyk         ||        esc@argon.com, lberger@fore.com, berson@isi.edu, fred@cisco.com, mborden@baynetworks.com, jj@arrowpoint.com 
  RFC2383          ||       M. Suzuki         ||        suzuki@nal.ecl.net 
  RFC2384          ||       R. Gellens         ||        Randy@Qualcomm.Com 
  RFC2385          ||      A. Heffernan         ||       ahh@cisco.com
  RFC2386          ||       E. Crawley, R. Nair, B. Rajagopalan, H. Sandick         ||         
  RFC2387          ||       E. Levinson         ||        XIson@cnj.digex.com 
  RFC2388          ||      L. Masinter         ||       masinter@parc.xerox.com
  RFC2389          ||       P. Hethmon, R. Elz         ||         
  RFC2390          ||       T. Bradley, C. Brown, A. Malis         ||        tbradley@avici.com, cbrown@juno.com, malis@ascend.com 
  RFC2391          ||       P. Srisuresh, D. Gan         ||        suresh@ra.lucent.com, dhg@juniper.net 
  RFC2392          ||       E. Levinson         ||        XIson@cnj.digex.net 
  RFC2393          ||       A. Shacham, R. Monsour, R. Pereira, M. Thomas         ||        shacham@cisco.com, rmonsour@hifn.com, rpereira@timestep.com, matt.thomas@altavista-software.com, naganand@baynetworks.com 
  RFC2394          ||       R. Pereira         ||         
  RFC2395          ||       R. Friend, R. Monsour         ||        rfriend@hifn.com, rmonsour@hifn.com 
  RFC2396          ||       T. Berners-Lee, R. Fielding, L. Masinter         ||        timbl@w3.org, fielding@ics.uci.edu, masinter@parc.xerox.com 
  RFC2397          ||      L. Masinter         ||       
  RFC2398          ||       S. Parker, C. Schmechel         ||        sparker@eng.sun.com, cschmec@eng.sun.com 
  RFC2399          ||       A. Ramos         ||        ramos@isi.edu 
  RFC2400          ||       J. Postel, J. Reynolds         ||        Postel@ISI.EDU, JKRey@ISI.EDU 
  RFC2401          ||       S. Kent, R. Atkinson         ||         
  RFC2402          ||       S. Kent, R. Atkinson         ||         
  RFC2403          ||       C. Madson, R. Glenn         ||         
  RFC2404          ||       C. Madson, R. Glenn         ||         
  RFC2405          ||       C. Madson, N. Doraswamy         ||         
  RFC2406          ||       S. Kent, R. Atkinson         ||         
  RFC2407          ||       D. Piper         ||        ddp@network-alchemy.com 
  RFC2408          ||       D. Maughan, M. Schertler, M. Schneider, J. Turner         ||        wdm@tycho.ncsc.mil, mss@tycho.ncsc.mil, mjs@securify.com, jeff.turner@raba.com 
  RFC2409          ||       D. Harkins, D. Carrel         ||        dharkins@cisco.com, carrel@ipsec.org 
  RFC2410          ||       R. Glenn, S. Kent         ||         
  RFC2411          ||      R. Thayer, N. Doraswamy, R. Glenn         ||       naganand@baynetworks.com, rob.glenn@nist.gov
  RFC2412          ||       H. Orman         ||        ho@darpa.mil 
  RFC2413          ||      S. Weibel, J. Kunze, C. Lagoze, M. Wolf         ||       weibel@oclc.org, jak@ckm.ucsf.edu, lagoze@cs.cornell.edu, misha.wolf@reuters.com
  RFC2414          ||       M. Allman, S. Floyd, C. Partridge         ||        mallman@lerc.nasa.gov, floyd@ee.lbl.gov, craig@bbn.com 
  RFC2415          ||       K. Poduri, K. Nichols         ||        kpoduri@Baynetworks.com, knichols@baynetworks.com 
  RFC2416          ||       T. Shepard, C. Partridge         ||        shep@alum.mit.edu, craig@bbn.com 
  RFC2417          ||       C. Chung, M. Greene         ||        chihschung@aol.com, maria@xedia.com 
  RFC2418          ||      S. Bradner         ||       
  RFC2419          ||       K. Sklower, G. Meyer         ||        sklower@CS.Berkeley.EDU 
  RFC2420          ||       H. Kummert         ||        kummert@nentec.de 
  RFC2421          ||       G. Vaudreuil, G. Parsons         ||        Glenn.Parsons@Nortel.ca, GregV@Lucent.Com 
  RFC2422          ||       G. Vaudreuil, G. Parsons         ||        Glenn.Parsons@Nortel.ca, GregV@Lucent.Com 
  RFC2423          ||       G. Vaudreuil, G. Parsons         ||        Glenn.Parsons@Nortel.ca, GregV@Lucent.Com 
  RFC2424          ||       G. Vaudreuil, G. Parsons         ||        Glenn.Parsons@Nortel.ca, GregV@Lucent.Com 
  RFC2425          ||      T. Howes, M. Smith, F. Dawson         ||       howes@netscape.com, mcs@netscape.com, frank_dawson@lotus.com
  RFC2426          ||      F. Dawson, T. Howes         ||       
  RFC2427          ||       C. Brown, A. Malis         ||        cbrown@juno.com, malis@ascend.com 
  RFC2428          ||       M. Allman, S. Ostermann, C. Metz         ||        mallman@lerc.nasa.gov, ostermann@cs.ohiou.edu, cmetz@inner.net 
  RFC2429          ||       C. Bormann, L. Cline, G. Deisher, T. Gardos, C. Maciocco, D. Newell, J. Ott, G. Sullivan, S. Wenger, C. Zhu         ||         
  RFC2430          ||       T. Li, Y. Rekhter         ||        tli@juniper.net, yakov@cisco.com 
  RFC2431          ||       D. Tynan         ||        dtynan@claddagh.ie 
  RFC2432          ||       K. Dubray         ||        kdubray@ironbridgenetworks.com 
  RFC2433          ||       G. Zorn, S. Cobb         ||        glennz@microsoft.com, stevec@microsoft.com 
  RFC2434          ||      T. Narten, H. Alvestrand         ||       narten@raleigh.ibm.com, Harald@Alvestrand.no
  RFC2435          ||       L. Berc, W. Fenner, R. Frederick, S. McCanne, P. Stewart         ||        berc@pa.dec.com, fenner@parc.xerox.com, frederick@parc.xerox.com, mccanne@cs.berkeley.edu, stewart@parc.xerox.com 
  RFC2436          ||       R. Brett, S. Bradner, G. Parsons         ||        rfbrett@nortel.ca, sob@harvard.edu, Glenn.Parsons@Nortel.ca 
  RFC2437          ||       B. Kaliski, J. Staddon         ||        burt@rsa.com, jstaddon@rsa.com 
  RFC2438          ||       M. O'Dell, H. Alvestrand, B. Wijnen, S. Bradner         ||        mo@uu.net, Harald.Alvestrand@maxware.no, wijnen@vnet.ibm.com, sob@harvard.edu 
  RFC2439          ||       C. Villamizar, R. Chandra, R. Govindan         ||        curtis@ans.net, rchandra@cisco.com, govindan@isi.edu 
  RFC2440          ||      J. Callas, L. Donnerhacke, H. Finney, R. Thayer         ||       
  RFC2441          ||       D. Cohen         ||        cohen@myri.com 
  RFC2442          ||       N. Freed, D. Newman, J. Belissent, M. Hoy         ||        ned.freed@innosoft.com, dan.newman@innosoft.com, jacques.belissent@eng.sun.com 
  RFC2443          ||       J. Luciani, A. Gallo         ||        luciani@baynetworks.com, gallo@raleigh.ibm.com 
  RFC2444          ||       C. Newman         ||        chris.newman@innosoft.com 
  RFC2445          ||      F. Dawson, D. Stenerson         ||       
  RFC2446          ||      S. Silverberg, S. Mansour, F. Dawson, R. Hopson         ||       
  RFC2447          ||      F. Dawson, S. Mansour, S. Silverberg         ||       
  RFC2448          ||       M. Civanlar, G. Cash, B. Haskell         ||        civanlar@research.att.com, glenn@research.att.com, bgh@research.att.com 
  RFC2449          ||      R. Gellens, C. Newman, L. Lundblade         ||       randy@qualcomm.com, chris.newman@innosoft.com, lgl@qualcomm.com
  RFC2450          ||      R. Hinden         ||       bob.hinden@gmail.com
  RFC2451          ||       R. Pereira, R. Adams         ||         
  RFC2452          ||      M. Daniele         ||       daniele@zk3.dec.com
  RFC2453          ||       G. Malkin         ||        gmalkin@baynetworks.com 
  RFC2454          ||      M. Daniele         ||       daniele@zk3.dec.com
  RFC2455          ||       B. Clouston, B. Moore         ||        clouston@cisco.com, remoore@us.ibm.com 
  RFC2456          ||       B. Clouston, B. Moore         ||        clouston@cisco.com, remoore@us.ibm.com 
  RFC2457          ||       B. Clouston, B. Moore         ||        clouston@cisco.com, remoore@us.ibm.com 
  RFC2458          ||       H. Lu, M. Krishnaswamy, L. Conroy, S. Bellovin, F. Burg, A. DeSimone, K. Tewani, P. Davidson, H. Schulzrinne, K. Vishwanathan         ||        smb@research.att.com, fburg@hogpb.att.com, lwc@roke.co.uk, pauldav@nortel.ca, murali@bell-labs.com, hui-lan.lu@bell-labs.com, schulzrinne@cs.columbia.edu, tewani@att.com, kumar@isochrone.com 
  RFC2459          ||       R. Housley, W. Ford, W. Polk, D. Solo         ||        housley@spyrus.com, wford@verisign.com, wpolk@nist.gov, david.solo@citicorp.com 
  RFC2460          ||      S. Deering, R. Hinden         ||       deering@cisco.com, bob.hinden@gmail.com
  RFC2461          ||      T. Narten, E. Nordmark, W. Simpson         ||       narten@raleigh.ibm.com, nordmark@sun.com, Bill.Simpson@um.cc.umich.edu
  RFC2462          ||      S. Thomson, T. Narten         ||       
  RFC2463          ||       A. Conta, S. Deering         ||        aconta@lucent.com, deering@cisco.com 
  RFC2464          ||      M. Crawford         ||       crawdad@fnal.gov
  RFC2465          ||      D. Haskin, S. Onishi         ||       dhaskin@baynetworks.com, sonishi@baynetworks.com
  RFC2466          ||      D. Haskin, S. Onishi         ||       dhaskin@baynetworks.com, sonishi@baynetworks.com
  RFC2467          ||      M. Crawford         ||       crawdad@fnal.gov
  RFC2468          ||       V. Cerf         ||        vcerf@mci.net 
  RFC2469          ||       T. Narten, C. Burton         ||        narten@raleigh.ibm.com, burton@rtp.vnet.ibm.com 
  RFC2470          ||      M. Crawford, T. Narten, S. Thomas         ||       crawdad@fnal.gov, narten@raleigh.ibm.com, stephen.thomas@transnexus.com
  RFC2471          ||      R. Hinden, R. Fink, J. Postel         ||       bob.hinden@gmail.com, rlfink@lbl.gov
  RFC2472          ||      D. Haskin, E. Allen         ||       dhaskin@baynetworks.com, eallen@baynetworks.com
  RFC2473          ||       A. Conta, S. Deering         ||        aconta@lucent.com, deering@cisco.com 
  RFC2474          ||      K. Nichols, S. Blake, F. Baker, D. Black         ||       kmn@cisco.com, slblake@torrentnet.com, fred@cisco.com, black_david@emc.com
  RFC2475          ||      S. Blake, D. Black, M. Carlson, E. Davies, Z. Wang, W. Weiss         ||       slblake@torrentnet.com, black_david@emc.com, mark.carlson@sun.com, elwynd@nortel.co.uk, zhwang@bell-labs.com, wweiss@lucent.com
  RFC2476          ||       R. Gellens, J. Klensin         ||        Randy@Qualcomm.Com, klensin@mci.net 
  RFC2477          ||       B. Aboba, G. Zorn         ||        bernarda@microsoft.com, glennz@microsoft.com 
  RFC2478          ||       E. Baize, D. Pinkas         ||         
  RFC2479          ||       C. Adams         ||        cadams@entrust.com 
  RFC2480          ||       N. Freed         ||        ned.freed@innosoft.com 
  RFC2481          ||       K. Ramakrishnan, S. Floyd         ||         
  RFC2482          ||      K. Whistler, G. Adams         ||       kenw@sybase.com, glenn@spyglass.com
  RFC2483          ||       M. Mealling, R. Daniel         ||        michaelm@rwhois.net, rdaniel@lanl.gov 
  RFC2484          ||       G. Zorn         ||        glennz@microsoft.com 
  RFC2485          ||       S. Drach         ||        drach@sun.com 
  RFC2486          ||       B. Aboba, M. Beadles         ||        bernarda@microsoft.com, mbeadles@wcom.net 
  RFC2487          ||       P. Hoffman         ||        phoffman@imc.org 
  RFC2488          ||       M. Allman, D. Glover, L. Sanchez         ||        mallman@lerc.nasa.gov, Daniel.R.Glover@lerc.nasa.gov, lsanchez@ir.bbn.com 
  RFC2489          ||       R. Droms         ||        droms@bucknell.edu 
  RFC2490          ||       M. Pullen, R. Malghan, L. Lavu, G. Duan, J. Ma, H. Nah         ||        mpullen@gmu.edu, rmalghan@bacon.gmu.edu, llavu@bacon.gmu.edu, gduan@us.oracle.com, jma@newbridge.com, hnah@bacon.gmu.edu 
  RFC2491          ||      G. Armitage, P. Schulter, M. Jork, G. Harter         ||       gja@lucent.com, paschulter@acm.org, jork@kar.dec.com, harter@zk3.dec.com
  RFC2492          ||      G. Armitage, P. Schulter, M. Jork         ||       gja@lucent.com, paschulter@acm.org, jork@kar.dec.com
  RFC2493          ||       K. Tesink, Ed.         ||        kaj@bellcore.com 
  RFC2494          ||       D. Fowler, Ed.         ||        davef@newbridge.com 
  RFC2495          ||       D. Fowler, Ed.         ||        davef@newbridge.com 
  RFC2496          ||       D. Fowler, Ed.         ||        davef@newbridge.com 
  RFC2497          ||      I. Souvatzis         ||       is@netbsd.org
  RFC2498          ||       J. Mahdavi, V. Paxson         ||        mahdavi@psc.edu, vern@ee.lbl.gov 
  RFC2499          ||       A. Ramos         ||        ramos@isi.edu 
  RFC2500          ||       J. Reynolds, R. Braden         ||         
  RFC2501          ||       S. Corson, J. Macker         ||        corson@isr.umd.edu, macker@itd.nrl.navy.mil 
  RFC2502          ||       M. Pullen, M. Myjak, C. Bouwens         ||        mpullen@gmu.edu, mmyjak@virtualworkshop.com, christina.bouwens@cpmx.mail.saic.com 
  RFC2503          ||       R. Moulton, M. Needleman         ||        ruth@muswell.demon.co.uk 
  RFC2504          ||       E. Guttman, L. Leong, G. Malkin         ||        erik.guttman@sun.com, lorna@colt.net, gmalkin@baynetworks.com 
  RFC2505          ||       G. Lindberg         ||         
  RFC2506          ||       K. Holtman, A. Mutz, T. Hardie         ||        koen@win.tue.nl, andy_mutz@hp.com, hardie@equinix.com 
  RFC2507          ||       M. Degermark, B. Nordgren, S. Pink         ||        micke@sm.luth.se, bcn@lulea.trab.se, steve@sm.luth.se 
  RFC2508          ||       S. Casner, V. Jacobson         ||        casner@cisco.com, van@cisco.com 
  RFC2509          ||       M. Engan, S. Casner, C. Bormann         ||        engan@effnet.com, casner@cisco.com, cabo@tzi.org 
  RFC2510          ||       C. Adams, S. Farrell         ||        cadams@entrust.com, stephen.farrell@sse.ie 
  RFC2511          ||       M. Myers, C. Adams, D. Solo, D. Kemp         ||        mmyers@verisign.com, cadams@entrust.com, david.solo@citicorp.com, dpkemp@missi.ncsc.mil 
  RFC2512          ||       K. McCloghrie, J. Heinanen, W. Greene, A. Prasad         ||        kzm@cisco.com, jh@telia.fi, wedge.greene@mci.com, aprasad@cisco.com 
  RFC2513          ||       K. McCloghrie, J. Heinanen, W. Greene, A. Prasad         ||        kzm@cisco.com, jh@telia.fi, wedge.greene@mci.com, aprasad@cisco.com 
  RFC2514          ||       M. Noto, E. Spiegel, K. Tesink         ||        mspiegel@cisco.com, kaj@bellcore.com 
  RFC2515          ||       K. Tesink, Ed         ||        kaj@bellcore.com 
  RFC2516          ||       L. Mamakos, K. Lidl, J. Evarts, D. Carrel, D. Simone, R. Wheeler         ||        louie@uu.net, lidl@uu.net, jde@uu.net, carrel@RedBack.net, dan@RedBack.net, ross@routerware.com 
  RFC2517          ||       R. Moats, R. Huber         ||        jayhawk@att.com, rvh@att.com 
  RFC2518          ||      Y. Goland, E. Whitehead, A. Faizi, S. Carter, D. Jensen         ||       yarong@microsoft.com, ejw@ics.uci.edu, asad@netscape.com, srcarter@novell.com, dcjensen@novell.com
  RFC2519          ||       E. Chen, J. Stewart         ||        enkechen@cisco.com, jstewart@juniper.net 
  RFC2520          ||       J. Luciani, H. Suzuki, N. Doraswamy, D. Horton         ||        luciani@baynetworks.com, hsuzuki@cisco.com, naganand@baynetworks.com, d.horton@citr.com.au 
  RFC2521          ||       P. Karn, W. Simpson         ||         
  RFC2522          ||       P. Karn, W. Simpson         ||         
  RFC2523          ||       P. Karn, W. Simpson         ||         
  RFC2524          ||       M. Banan         ||         
  RFC2525          ||       V. Paxson, M. Allman, S. Dawson, W. Fenner, J. Griner, I. Heavens, K. Lahey, J. Semke, B. Volz         ||        vern@aciri.org, sdawson@eecs.umich.edu, fenner@parc.xerox.com, jgriner@grc.nasa.gov, ian@spider.com, kml@nas.nasa.gov, semke@psc.edu, volz@process.com 
  RFC2526          ||       D. Johnson, S. Deering         ||        dbj@cs.cmu.edu, deering@cisco.com 
  RFC2527          ||       S. Chokhani, W. Ford         ||         
  RFC2528          ||       R. Housley, W. Polk         ||        housley@spyrus.com, wpolk@nist.gov 
  RFC2529          ||       B. Carpenter, C. Jung         ||        brian@hursley.ibm.com, cmj@3Com.com 
  RFC2530          ||       D. Wing         ||        dwing-ietf@fuggles.com 
  RFC2531          ||       G. Klyne, L. McIntyre         ||        GK@ACM.ORG, Lloyd.McIntyre@pahv.xerox.com 
  RFC2532          ||       L. Masinter, D. Wing         ||        masinter@parc.xerox.com, dwing-ietf@fuggles.com 
  RFC2533          ||       G. Klyne         ||        GK@ACM.ORG 
  RFC2534          ||       L. Masinter, D. Wing, A. Mutz, K. Holtman         ||        masinter@parc.xerox.com, dwing-ietf@fuggles.com, koen@win.tue.nl 
  RFC2535          ||       D. Eastlake 3rd         ||        dee3@us.ibm.com 
  RFC2536          ||      D. Eastlake 3rd         ||       dee3@us.ibm.com
  RFC2537          ||       D. Eastlake 3rd         ||        dee3@us.ibm.com 
  RFC2538          ||       D. Eastlake 3rd, O. Gudmundsson         ||        dee3@us.ibm.com, ogud@tislabs.com 
  RFC2539          ||      D. Eastlake 3rd         ||       dee3@us.ibm.com
  RFC2540          ||       D. Eastlake 3rd         ||        dee3@us.ibm.com 
  RFC2541          ||       D. Eastlake 3rd         ||        dee3@us.ibm.com 
  RFC2542          ||       L. Masinter         ||        masinter@parc.xerox.com 
  RFC2543          ||      M. Handley, H. Schulzrinne, E. Schooler, J. Rosenberg         ||       
  RFC2544          ||      S. Bradner, J. McQuaid         ||       
  RFC2545          ||       P. Marques, F. Dupont         ||         
  RFC2546          ||       A. Durand, B. Buclin         ||        Alain.Durand@imag.fr, Bertrand.Buclin@ch.att.com 
  RFC2547          ||       E. Rosen, Y. Rekhter         ||        erosen@cisco.com, yakov@cisco.com 
  RFC2548          ||       G. Zorn         ||         
  RFC2549          ||       D. Waitzman         ||        djw@vineyard.net 
  RFC2550          ||       S. Glassman, M. Manasse, J. Mogul         ||        steveg@pa.dec.com, msm@pa.dec.com, mogul@pa.dec.com 
  RFC2551          ||       S. Bradner         ||         
  RFC2552          ||       M. Blinov, M. Bessonov, C. Clissmann         ||        mch@net-cs.ucd.ie, mikeb@net-cs.ucd.ie, ciaranc@net-cs.ucd.ie 
  RFC2553          ||       R. Gilligan, S. Thomson, J. Bound, W. Stevens         ||        gilligan@freegate.com, set@thumper.bellcore.com, bound@zk3.dec.com, rstevens@kohala.com 
  RFC2554          ||      J. Myers         ||       jgmyers@netscape.com
  RFC2555          ||       RFC Editor, et al.         ||        braden@isi.edu, jkrey@isi.edu, crocker@mbl.edu, vcerf@mci.net, feinler@juno.com, celeste@isi.edu 
  RFC2556          ||       S. Bradner         ||        sob@harvard.edu 
  RFC2557          ||       J. Palme, A. Hopmann, N. Shelness         ||        jpalme@dsv.su.se, alexhop@microsoft.com, Shelness@lotus.com, stef@nma.com 
  RFC2558          ||       K. Tesink         ||        kaj@research.telcordia.com 
  RFC2559          ||       S. Boeyen, T. Howes, P. Richard         ||        sharon.boeyen@entrust.com, howes@netscape.com, patr@xcert.com 
  RFC2560          ||      M. Myers, R. Ankney, A. Malpani, S. Galperin, C. Adams         ||       mmyers@verisign.com, rankney@erols.com, ambarish@valicert.com, galperin@mycfo.com, cadams@entrust.com
  RFC2561          ||       K. White, R. Moore         ||        kennethw@vnet.ibm.com, remoore@us.ibm.com 
  RFC2562          ||       K. White, R. Moore         ||        kennethw@vnet.ibm.com, remoore@us.ibm.com 
  RFC2563          ||       R. Troll         ||        rtroll@corp.home.net 
  RFC2564          ||       C. Kalbfleisch, C. Krupczak, R. Presuhn, J. Saperia         ||        cwk@verio.net, cheryl@empiretech.com, randy_presuhn@bmc.com, saperia@mediaone.net 
  RFC2565          ||       R. Herriot, Ed., S. Butler, P. Moore, R. Turner         ||        rherriot@pahv.xerox.com, sbutler@boi.hp.com, paulmo@microsoft.com, rturner@sharplabs.com, rherriot@pahv.xerox.com 
  RFC2566          ||      R. deBry, T. Hastings, R. Herriot, S. Isaacson, P. Powell         ||       sisaacson@novell.com, tom.hastings@alum.mit.edu, robert.herriot@pahv.xerox.com, debryro@uvsc.edu, papowell@astart.com
  RFC2567          ||       F. Wright         ||         
  RFC2568          ||       S. Zilles         ||         
  RFC2569          ||      R. Herriot, Ed., T. Hastings, N. Jacobs, J. Martin         ||       rherriot@pahv.xerox.com, Norm.Jacobs@Central.sun.com, tom.hastings@alum.mit.edu, jkm@underscore.com
  RFC2570          ||       J. Case, R. Mundy, D. Partain, B. Stewart         ||         
  RFC2571          ||       B. Wijnen, D. Harrington, R. Presuhn         ||         
  RFC2572          ||       J. Case, D. Harrington, R. Presuhn, B. Wijnen         ||         
  RFC2573          ||       D. Levi, P. Meyer, B. Stewart         ||         
  RFC2574          ||       U. Blumenthal, B. Wijnen         ||         
  RFC2575          ||       B. Wijnen, R. Presuhn, K. McCloghrie         ||         
  RFC2576          ||       R. Frye, D. Levi, S. Routhier, B. Wijnen         ||         
  RFC2577          ||       M. Allman, S. Ostermann         ||        mallman@grc.nasa.gov, ostermann@cs.ohiou.edu 
  RFC2578          ||      K. McCloghrie, Ed., D. Perkins, Ed., J. Schoenwaelder, Ed.         ||       
  RFC2579          ||      K. McCloghrie, Ed., D. Perkins, Ed., J. Schoenwaelder, Ed.         ||       
  RFC2580          ||      K. McCloghrie, Ed., D. Perkins, Ed., J. Schoenwaelder, Ed.         ||       
  RFC2581          ||      M. Allman, V. Paxson, W. Stevens         ||       mallman@grc.nasa.gov, vern@aciri.org, rstevens@kohala.com
  RFC2582          ||       S. Floyd, T. Henderson         ||         
  RFC2583          ||       R. Carlson, L. Winkler         ||        RACarlson@anl.gov, lwinkler@anl.gov 
  RFC2584          ||       B. Clouston, B. Moore         ||        clouston@cisco.com, remoore@us.ibm.com 
  RFC2585          ||      R. Housley, P. Hoffman         ||       housley@spyrus.com, phoffman@imc.org 
  RFC2586          ||       J. Salsman, H. Alvestrand         ||        James@bovik.org, Harald.T.Alvestrand@uninett.no 
  RFC2587          ||       S. Boeyen, T. Howes, P. Richard         ||        sharon.boeyen@entrust.com, howes@netscape.com, patr@xcert.com 
  RFC2588          ||       R. Finlayson         ||        finlayson@live.com 
  RFC2589          ||       Y. Yaacovi, M. Wahl, T. Genovese         ||        yoramy@microsoft.com, tonyg@microsoft.com 
  RFC2590          ||      A. Conta, A. Malis, M. Mueller         ||       aconta@lucent.com, malis@ascend.com, memueller@lucent.com
  RFC2591          ||       D. Levi, J. Schoenwaelder         ||         
  RFC2592          ||       D. Levi, J. Schoenwaelder         ||         
  RFC2593          ||       J. Schoenwaelder, J. Quittek         ||        schoenw@ibr.cs.tu-bs.de, quittek@ccrle.nec.de 
  RFC2594          ||       H. Hazewinkel, C. Kalbfleisch, J. Schoenwaelder         ||         
  RFC2595          ||      C. Newman         ||       chris.newman@innosoft.com
  RFC2596          ||       M. Wahl, T. Howes         ||        M.Wahl@innosoft.com, howes@netscape.com 
  RFC2597          ||       J. Heinanen, F. Baker, W. Weiss, J. Wroclawski         ||        jh@telia.fi, fred@cisco.com, wweiss@lucent.com, jtw@lcs.mit.edu 
  RFC2598          ||       V. Jacobson, K. Nichols, K. Poduri         ||        van@cisco.com, kmn@cisco.com, kpoduri@baynetworks.com 
  RFC2599          ||       A. DeLaCruz         ||        delacruz@isi.edu 
  RFC2600          ||       J. Reynolds, R. Braden         ||         
  RFC2601          ||       M. Davison         ||        mike.davison@cisco.com 
  RFC2602          ||       M. Davison         ||        mike.davison@cisco.com 
  RFC2603          ||       M. Davison         ||        mike.davison@cisco.com 
  RFC2604          ||       R. Gellens         ||        randy@qualcomm.com 
  RFC2605          ||       G. Mansfield, S. Kille         ||        glenn@cysols.com, Steve.Kille@MessagingDirect.com 
  RFC2606          ||      D. Eastlake 3rd, A. Panitz         ||       dee3@us.ibm.com, buglady@fuschia.net
  RFC2607          ||       B. Aboba, J. Vollbrecht         ||        bernarda@microsoft.com, jrv@merit.edu 
  RFC2608          ||       E. Guttman, C. Perkins, J. Veizades, M. Day         ||        Erik.Guttman@sun.com, cperkins@sun.com, veizades@home.net, mday@vinca.com 
  RFC2609          ||       E. Guttman, C. Perkins, J. Kempf         ||        erik.guttman@sun.com, cperkins@sun.com, james.kempf@sun.com 
  RFC2610          ||       C. Perkins, E. Guttman         ||        Charles.Perkins@Sun.Com, Erik.Guttman@Sun.Com 
  RFC2611          ||      L. Daigle, D. van Gulik, R. Iannella, P. Faltstrom         ||       leslie@thinkingcat.com, Dirk.vanGulik@jrc.it, renato@dstc.edu.au, paf@swip.net
  RFC2612          ||       C. Adams, J. Gilchrist         ||        carlisle.adams@entrust.com, jeff.gilchrist@entrust.com 
  RFC2613          ||       R. Waterman, B. Lahaye, D. Romascanu, S. Waldbusser         ||        rich@allot.com, dromasca@gmail.com , waldbusser@ins.com 
  RFC2614          ||       J. Kempf, E. Guttman         ||        james.kempf@sun.com, erik.guttman@sun.com 
  RFC2615          ||       A. Malis, W. Simpson         ||        malis@ascend.com, wsimpson@GreenDragon.com 
  RFC2616          ||      R. Fielding, J. Gettys, J. Mogul, H. Frystyk, L. Masinter, P. Leach, T. Berners-Lee         ||       fielding@ics.uci.edu, jg@w3.org, mogul@wrl.dec.com, frystyk@w3.org, masinter@parc.xerox.com, paulle@microsoft.com, timbl@w3.org
  RFC2617          ||      J. Franks, P. Hallam-Baker, J. Hostetler, S. Lawrence, P. Leach, A. Luotonen, L. Stewart         ||       john@math.nwu.edu, pbaker@verisign.com, jeff@AbiSource.com, lawrence@agranat.com, paulle@microsoft.com, stewart@OpenMarket.com
  RFC2618          ||       B. Aboba, G. Zorn         ||        bernarda@microsoft.com, glennz@microsoft.com 
  RFC2619          ||       G. Zorn, B. Aboba         ||        bernarda@microsoft.com, glennz@microsoft.com 
  RFC2620          ||       B. Aboba, G. Zorn         ||        bernarda@microsoft.com, glennz@microsoft.com 
  RFC2621          ||       G. Zorn, B. Aboba         ||        bernarda@microsoft.com, glennz@microsoft.com 
  RFC2622          ||      C. Alaettinoglu, C. Villamizar, E. Gerich, D. Kessens, D. Meyer, T. Bates, D. Karrenberg, M. Terpstra         ||       cengiz@isi.edu, curtis@avici.com, epg@home.net, David.Kessens@qwest.net, meyer@antc.uoregon.edu, tbates@cisco.com, dfk@ripe.net, marten@BayNetworks.com
  RFC2623          ||      M. Eisler         ||       mre@eng.sun.com
  RFC2624          ||       S. Shepler         ||        spencer.shepler@eng.sun.com 
  RFC2625          ||       M. Rajagopal, R. Bhagwat, W. Rickard         ||        murali@gadzoox.com, raj@gadzoox.com, wayne@gadzoox.com 
  RFC2626          ||       P. Nesser II         ||         
  RFC2627          ||       D. Wallner, E. Harder, R. Agee         ||        dmwalln@orion.ncsc.mil, ejh@tycho.ncsc.mil 
  RFC2628          ||       V. Smyslov         ||        svan@trustworks.com 
  RFC2629          ||      M. Rose         ||       mrose17@gmail.com
  RFC2630          ||       R. Housley         ||        housley@spyrus.com 
  RFC2631          ||       E. Rescorla         ||        ekr@rtfm.com 
  RFC2632          ||       B. Ramsdell, Ed.         ||         
  RFC2633          ||       B. Ramsdell, Ed.         ||         
  RFC2634          ||      P. Hoffman, Ed.         ||       phoffman@imc.org
  RFC2635          ||       S. Hambridge, A. Lunde         ||         
  RFC2636          ||       R. Gellens         ||        randy@qualcomm.com 
  RFC2637          ||       K. Hamzeh, G. Pall, W. Verthein, J. Taarud, W. Little, G. Zorn         ||        kory@ascend.com, gurdeep@microsoft.com, glennz@microsoft.com 
  RFC2638          ||      K. Nichols, V. Jacobson, L. Zhang         ||       kmn@cisco.com, van@cisco.com, lixia@cs.ucla.edu
  RFC2639          ||      T. Hastings, C. Manros         ||       tom.hastings@alum.mit.edu, manros@cp10.es.xerox.com
  RFC2640          ||       B. Curtin         ||        curtinw@ftm.disa.mil 
  RFC2641          ||       D. Hamilton, D. Ruffen         ||        daveh@ctron.com, ruffen@ctron.com 
  RFC2642          ||       L. Kane         ||        lkane@ctron.com 
  RFC2643          ||      D. Ruffen, T. Len, J. Yanacek         ||       ruffen@ctron.com, len@ctron.com, jyanacek@ctron.com
  RFC2644          ||       D. Senie         ||        dts@senie.com 
  RFC2645          ||       R. Gellens         ||        randy@qualcomm.com 
  RFC2646          ||       R. Gellens, Ed.         ||         
  RFC2647          ||       D. Newman         ||         
  RFC2648          ||      R. Moats         ||       jayhawk@att.com
  RFC2649          ||       B. Greenblatt, P. Richard         ||        bgreenblatt@directory-applications.com, patr@xcert.com 
  RFC2650          ||       D. Meyer, J. Schmitz, C. Orange, M. Prior, C. Alaettinoglu         ||        dmm@cisco.com, SchmitzJo@aol.com, orange@spiritone.com, mrp@connect.com.au, cengiz@isi.edu 
  RFC2651          ||       J. Allen, M. Mealling         ||        jeff.allen@acm.org, michael.mealling@RWhois.net 
  RFC2652          ||       J. Allen, M. Mealling         ||        jeff.allen@acm.org, michael.mealling@RWhois.net 
  RFC2653          ||       J. Allen, P. Leach, R. Hedberg         ||        jeff.allen@acm.org, paulle@microsoft.com, roland@catalogix.ac.se 
  RFC2654          ||       R. Hedberg, B. Greenblatt, R. Moats, M. Wahl         ||        roland@catalogix.ac.se, bgreenblatt@directory-applications.com, jayhawk@att.com 
  RFC2655          ||       T. Hardie, M. Bowman, D. Hardy, M. Schwartz, D. Wessels         ||        hardie@equinix.com, mic@transarc.com, dhardy@netscape.com, wessels@nlanr.net 
  RFC2656          ||       T. Hardie         ||        hardie@equinix.com 
  RFC2657          ||       R. Hedberg         ||        roland@catalogix.ac.se 
  RFC2658          ||       K. McKay         ||        kylem@qualcomm.com 
  RFC2659          ||       E. Rescorla, A. Schiffman         ||        ekr@rtfm.com, ams@terisa.com 
  RFC2660          ||       E. Rescorla, A. Schiffman         ||        ekr@rtfm.com, ams@terisa.com 
  RFC2661          ||       W. Townsley, A. Valencia, A. Rubens, G. Pall, G. Zorn, B. Palter         ||        gurdeep@microsoft.com, palter@zev.net, acr@del.com, townsley@cisco.com, vandys@cisco.com, gwz@acm.org 
  RFC2662          ||       G. Bathrick, F. Ly         ||        bathricg@agcs.com, faye@coppermountain.com 
  RFC2663          ||       P. Srisuresh, M. Holdrege         ||        srisuresh@lucent.com, holdrege@lucent.com 
  RFC2664          ||       R. Plzak, A. Wells, E. Krol         ||        plzakr@saic.com, awel@cs.wisc.edu, krol@uiuc.edu 
  RFC2665          ||       J. Flick, J. Johnson         ||        johnf@rose.hp.com, jeff@redbacknetworks.com 
  RFC2666          ||       J. Flick         ||        johnf@rose.hp.com 
  RFC2667          ||       D. Thaler         ||        dthaler@microsoft.com 
  RFC2668          ||       A. Smith, J. Flick, K. de Graaf, D. Romascanu, D. McMaster, K. McCloghrie, S. Roberts         ||        andrew@extremenetworks.com, johnf@rose.hp.com, kdegraaf@argon.com, dromasca@gmail.com , mcmaster@cisco.com, kzm@cisco.com, sroberts@farallon.com 
  RFC2669          ||       M. St. Johns, Ed.         ||        stjohns@corp.home.net 
  RFC2670          ||       M. St. Johns, Ed.         ||        stjohns@corp.home.net 
  RFC2671          ||      P. Vixie         ||       vixie@isc.org
  RFC2672          ||      M. Crawford         ||       crawdad@fnal.gov
  RFC2673          ||      M. Crawford         ||       crawdad@fnal.gov
  RFC2674          ||       E. Bell, A. Smith, P. Langille, A. Rijhsinghani, K. McCloghrie         ||        Les_Bell@3Com.com, andrew@extremenetworks.com, langille@newbridge.com, anil@cabletron.com, kzm@cisco.com 
  RFC2675          ||      D. Borman, S. Deering, R. Hinden         ||       dab@bsdi.com, deering@cisco.com, bob.hinden@gmail.com
  RFC2676          ||       G. Apostolopoulos, S. Kama, D. Williams, R. Guerin, A. Orda, T. Przygienda         ||        georgeap@watson.ibm.com, guerin@ee.upenn.edu, ariel@ee.technion.ac.il, dougw@watson.ibm.com 
  RFC2677          ||       M. Greene, J. Cucchiara, J. Luciani         ||        luciani@baynetworks.com, maria@xedia.com, joan@ironbridgenetworks.com 
  RFC2678          ||       J. Mahdavi, V. Paxson         ||        mahdavi@psc.edu, vern@ee.lbl.gov 
  RFC2679          ||      G. Almes, S. Kalidindi, M. Zekauskas         ||       almes@advanced.org, kalidindi@advanced.org, matt@advanced.org
  RFC2680          ||      G. Almes, S. Kalidindi, M. Zekauskas         ||       almes@advanced.org, kalidindi@advanced.org, matt@advanced.org
  RFC2681          ||       G. Almes, S. Kalidindi, M. Zekauskas         ||        almes@advanced.org, kalidindi@advanced.org, matt@advanced.org 
  RFC2682          ||       I. Widjaja, A. Elwalid         ||        indra.widjaja@fnc.fujitsu.com, anwar@lucent.com 
  RFC2683          ||      B. Leiba         ||       leiba@watson.ibm.com
  RFC2684          ||       D. Grossman, J. Heinanen         ||        dan@dma.isg.mot.com, jh@telia.fi 
  RFC2685          ||       B. Fox, B. Gleeson         ||        barbarafox@lucent.com, bgleeson@shastanets.com 
  RFC2686          ||       C. Bormann         ||        cabo@tzi.org 
  RFC2687          ||       C. Bormann         ||        cabo@tzi.org 
  RFC2688          ||       S. Jackowski, D. Putzolu, E. Crawley, B. Davie         ||        stevej@DeterministicNetworks.com, David.Putzolu@intel.com, esc@argon.com, bdavie@cisco.com 
  RFC2689          ||       C. Bormann         ||        cabo@tzi.org 
  RFC2690          ||       S. Bradner         ||         
  RFC2691          ||       S. Bradner         ||         
  RFC2692          ||       C. Ellison         ||        carl.m.ellison@intel.com 
  RFC2693          ||       C. Ellison, B. Frantz, B. Lampson, R. Rivest, B. Thomas, T. Ylonen         ||        carl.m.ellison@intel.com, frantz@netcom.com, blampson@microsoft.com, rivest@theory.lcs.mit.edu, bt0008@sbc.com, ylo@ssh.fi 
  RFC2694          ||       P. Srisuresh, G. Tsirtsis, P. Akkiraju, A. Heffernan         ||        srisuresh@yahoo.com, george@gideon.bt.co.uk, spa@cisco.com, ahh@juniper.net 
  RFC2695          ||       A. Chiu         ||         
  RFC2696          ||       C. Weider, A. Herron, A. Anantha, T. Howes         ||        cweider@microsoft.com, andyhe@microsoft.com, anoopa@microsoft.com, howes@netscape.com 
  RFC2697          ||       J. Heinanen, R. Guerin         ||        jh@telia.fi, guerin@ee.upenn.edu 
  RFC2698          ||       J. Heinanen, R. Guerin         ||        jh@telia.fi, guerin@ee.upenn.edu 
  RFC2699          ||       S. Ginoza         ||        ginoza@isi.edu 
  RFC2700          ||       J. Reynolds, R. Braden         ||         
  RFC2701          ||       G. Malkin         ||         
  RFC2702          ||       D. Awduche, J. Malcolm, J. Agogbua, M. O'Dell, J. McManus         ||        awduche@uu.net, jmalcolm@uu.net, ja@uu.net, mo@uu.net, jmcmanus@uu.net 
  RFC2703          ||       G. Klyne         ||        GK@ACM.ORG 
  RFC2704          ||       M. Blaze, J. Feigenbaum, J. Ioannidis, A. Keromytis         ||        mab@research.att.com, jf@research.att.com, ji@research.att.com, angelos@dsl.cis.upenn.edu 
  RFC2705          ||       M. Arango, A. Dugan, I. Elliott, C. Huitema, S. Pickett         ||        marango@rslcom.com, andrew.dugan@l3.com, ike.elliott@l3.com, huitema@research.telcordia.com, ScottP@vertical.com 
  RFC2706          ||       D. Eastlake 3rd, T. Goldstein         ||        dee3@us.ibm.com, tgoldstein@brodia.com 
  RFC2707          ||      R. Bergman, T. Hastings, S. Isaacson, H. Lewis         ||       rbergma@dpc.com, tom.hastings@alum.mit.edu, scott_isaacson@novell.com, harryl@us.ibm.com
  RFC2708          ||      R. Bergman         ||       rbergman@dpc.com, tom.hastings@alum.mit.edu, scott_isaacson@novell.com, harryl@us.ibm.com, bpenteco@boi.hp.com
  RFC2709          ||       P. Srisuresh         ||        srisuresh@lucent.com 
  RFC2710          ||       S. Deering, W. Fenner, B. Haberman         ||        deering@cisco.com, fenner@research.att.com, haberman@raleigh.ibm.com 
  RFC2711          ||      C. Partridge, A. Jackson         ||       craig@bbn.com, awjacks@bbn.com
  RFC2712          ||       A. Medvinsky, M. Hur         ||        amedvins@excitecorp.com, matt.hur@cybersafe.com 
  RFC2713          ||       V. Ryan, S. Seligman, R. Lee         ||        vincent.ryan@ireland.sun.com, scott.seligman@eng.sun.com, rosanna.lee@eng.sun.com 
  RFC2714          ||       V. Ryan, R. Lee, S. Seligman         ||        vincent.ryan@ireland.sun.com, rosanna.lee@eng.sun.com, scott.seligman@eng.sun.com 
  RFC2715          ||       D. Thaler         ||        dthaler@microsoft.com 
  RFC2716          ||      B. Aboba, D. Simon         ||       bernarda@microsoft.com, dansimon@microsoft.com
  RFC2717          ||      R. Petke, I. King         ||       rpetke@wcom.net, iking@microsoft.com
  RFC2718          ||       L. Masinter, H. Alvestrand, D. Zigmond, R. Petke         ||        masinter@parc.xerox.com, harald.alvestrand@maxware.no, djz@corp.webtv.net, rpetke@wcom.net 
  RFC2719          ||       L. Ong, I. Rytina, M. Garcia, H. Schwarzbauer, L. Coene, H. Lin, I. Juhasz, M. Holdrege, C. Sharp         ||        long@nortelnetworks.com, ian.rytina@ericsson.com, holdrege@lucent.com, lode.coene@siemens.atea.be, Miguel.A.Garcia@ericsson.com, chsharp@cisco.com, imre.i.juhasz@telia.se, hlin@research.telcordia.com, HannsJuergen.Schwarzbauer@icn.siemens.de 
  RFC2720          ||       N. Brownlee         ||        n.brownlee@auckland.ac.nz 
  RFC2721          ||       N. Brownlee         ||        n.brownlee@auckland.ac.nz 
  RFC2722          ||       N. Brownlee, C. Mills, G. Ruth         ||        n.brownlee@auckland.ac.nz, cmills@gte.com, gruth@bbn.com 
  RFC2723          ||       N. Brownlee         ||        n.brownlee@auckland.ac.nz 
  RFC2724          ||       S. Handelman, S. Stibler, N. Brownlee, G. Ruth         ||        swhandel@us.ibm.com, stibler@us.ibm.com, n.brownlee@auckland.ac.nz, gruth@bbn.com 
  RFC2725          ||       C. Villamizar, C. Alaettinoglu, D. Meyer, S. Murphy         ||        curtis@avici.com, cengiz@ISI.EDU, dmm@cisco.com, sandy@tis.com 
  RFC2726          ||       J. Zsako         ||        zsako@banknet.net 
  RFC2727          ||       J. Galvin         ||         
  RFC2728          ||       R. Panabaker, S. Wegerif, D. Zigmond         ||         
  RFC2729          ||       P. Bagnall, R. Briscoe, A. Poppitt         ||        pete@surfaceeffect.com, bob.briscoe@bt.com, apoppitt@jungle.bt.co.uk 
  RFC2730          ||       S. Hanna, B. Patel, M. Shah         ||        steve.hanna@sun.com, baiju.v.patel@intel.com, munils@microsoft.com 
  RFC2731          ||      J. Kunze         ||       jak@ckm.ucsf.edu
  RFC2732          ||      R. Hinden, B. Carpenter, L. Masinter         ||       bob.hinden@gmail.com, brian@icair.org, LMM@acm.org
  RFC2733          ||      J. Rosenberg, H. Schulzrinne         ||       schulzrinne@cs.columbia.edu
  RFC2734          ||       P. Johansson         ||         
  RFC2735          ||       B. Fox, B. Petri         ||        bfox@equipecom.com, bernhard.petri@icn.siemens.de 
  RFC2736          ||       M. Handley, C. Perkins         ||        mjh@aciri.org, C.Perkins@cs.ucl.ac.uk 
  RFC2737          ||       K. McCloghrie, A. Bierman         ||        kzm@cisco.com, andy@yumaworks.com
  RFC2738          ||       G. Klyne         ||        GK@ACM.ORG 
  RFC2739          ||      T. Small, D. Hennessy, F. Dawson         ||       
  RFC2740          ||      R. Coltun, D. Ferguson, J. Moy         ||       rcoltun@siara.com, dennis@juniper.com, jmoy@sycamorenet.com
  RFC2741          ||       M. Daniele, B. Wijnen, M. Ellison, D. Francisco         ||        daniele@zk3.dec.com, wijnen@vnet.ibm.com, ellison@world.std.com, dfrancis@cisco.com 
  RFC2742          ||       L. Heintz, S. Gudur, M. Ellison         ||        lheintz@cisco.com, sgudur@hotmail.com 
  RFC2743          ||      J. Linn         ||       
  RFC2744          ||       J. Wray         ||        John_Wray@Iris.com 
  RFC2745          ||       A. Terzis, B. Braden, S. Vincent, L. Zhang         ||        terzis@cs.ucla.edu, braden@isi.edu, svincent@cisco.com, lixia@cs.ucla.edu 
  RFC2746          ||       A. Terzis, J. Krawczyk, J. Wroclawski, L. Zhang         ||        jj@arrowpoint.com, jtw@lcs.mit.edu, lixia@cs.ucla.edu, terzis@cs.ucla.edu 
  RFC2747          ||       F. Baker, B. Lindell, M. Talwar         ||        fred@cisco.com, lindell@ISI.EDU, mohitt@microsoft.com 
  RFC2748          ||       D. Durham, Ed., J. Boyle, R. Cohen, S. Herzog, R. Rajan, A. Sastry         ||         
  RFC2749          ||       S. Herzog, Ed., J. Boyle, R. Cohen, D. Durham, R. Rajan, A. Sastry         ||         
  RFC2750          ||       S. Herzog         ||         
  RFC2751          ||       S. Herzog         ||         
  RFC2752          ||       S. Yadav, R. Yavatkar, R. Pabbati, P. Ford, T. Moore, S. Herzog         ||         
  RFC2753          ||       R. Yavatkar, D. Pendarakis, R. Guerin         ||        raj.yavatkar@intel.com, dimitris@watson.ibm.com, guerin@ee.upenn.edu 
  RFC2754          ||      C. Alaettinoglu, C. Villamizar, R. Govindan         ||       cengiz@isi.edu, curtis@avici.com, govindan@isi.edu
  RFC2755          ||       A. Chiu, M. Eisler, B. Callaghan         ||        alex.chiu@Eng.sun.com, michael.eisler@Eng.sun.com, brent.callaghan@Eng.sun.com 
  RFC2756          ||       P. Vixie, D. Wessels         ||        vixie@isc.org, wessels@nlanr.net 
  RFC2757          ||       G. Montenegro, S. Dawkins, M. Kojo, V. Magret, N. Vaidya         ||        gab@sun.com, sdawkins@nortel.com, kojo@cs.helsinki.fi, vincent.magret@aud.alcatel.com, vaidya@cs.tamu.edu 
  RFC2758          ||       K. White         ||        wkenneth@us.ibm.com 
  RFC2759          ||       G. Zorn         ||        gwz@acm.org 
  RFC2760          ||       M. Allman, Ed., S. Dawkins, D. Glover, J. Griner, D. Tran, T. Henderson, J. Heidemann, J. Touch, H. Kruse, S. Ostermann, K. Scott, J. Semke         ||        mallman@grc.nasa.gov, Spencer.Dawkins.sdawkins@nt.com, Daniel.R.Glover@grc.nasa.gov, jgriner@grc.nasa.gov, dtran@grc.nasa.gov, tomh@cs.berkeley.edu, johnh@isi.edu, touch@isi.edu, hkruse1@ohiou.edu, ostermann@cs.ohiou.edu, kscott@mitre.org, semke@psc.edu 
  RFC2761          ||       J. Dunn, C. Martin         ||         
  RFC2762          ||       J. Rosenberg, H. Schulzrinne         ||        jdrosen@dynamicsoft.com, schulzrinne@cs.columbia.edu 
  RFC2763          ||      N. Shen, H. Smit         ||       naiming@siara.com, hsmit@cisco.com
  RFC2764          ||       B. Gleeson, A. Lin, J. Heinanen, G. Armitage, A. Malis         ||         
  RFC2765          ||      E. Nordmark         ||       nordmark@sun.com
  RFC2766          ||      G. Tsirtsis, P. Srisuresh         ||       george.tsirtsis@bt.com, srisuresh@yahoo.com
  RFC2767          ||      K. Tsuchiya, H. Higuchi, Y. Atarashi         ||       tsuchi@ebina.hitachi.co.jp, h-higuti@ebina.hitachi.co.jp, atarashi@ebina.hitachi.co.jp
  RFC2768          ||       B. Aiken, J. Strassner, B. Carpenter, I. Foster, C. Lynch, J. Mambretti, R. Moore, B. Teitelbaum         ||        raiken@cisco.com, raiken@cisco.com, johns@cisco.com, brian@hursley.ibm.com, foster@mcs.anl.gov, cliff@cni.org, j-mambretti@nwu.edu, moore@sdsc.edu, ben@internet2.edu 
  RFC2769          ||       C. Villamizar, C. Alaettinoglu, R. Govindan, D. Meyer         ||        curtis@avici.com, cengiz@ISI.EDU, govindan@ISI.EDU, dmm@cisco.com 
  RFC2770          ||       D. Meyer, P. Lothberg         ||        dmm@cisco.com, roll@sprint.net 
  RFC2771          ||       R. Finlayson         ||        finlayson@live.com 
  RFC2772          ||       R. Rockell, R. Fink         ||        rrockell@sprint.net, fink@es.net 
  RFC2773          ||       R. Housley, P. Yee, W. Nace         ||        housley@spyrus.com, yee@spyrus.com 
  RFC2774          ||       H. Nielsen, P. Leach, S. Lawrence         ||        frystyk@microsoft.com, paulle@microsoft.com, lawrence@agranat.com 
  RFC2775          ||       B. Carpenter         ||        brian@icair.org 
  RFC2776          ||      M. Handley, D. Thaler, R. Kermode         ||       mjh@aciri.org, dthaler@microsoft.com, Roger.Kermode@motorola.com
  RFC2777          ||       D. Eastlake 3rd         ||        Donald.Eastlake@motorola.com 
  RFC2778          ||       M. Day, J. Rosenberg, H. Sugano         ||        mday@alum.mit.edu, suga@flab.fujitsu.co.jp 
  RFC2779          ||       M. Day, S. Aggarwal, G. Mohr, J. Vincent         ||        mday@alum.mit.edu, sonuag@microsoft.com, gojomo@usa.net, jesse@intonet.com 
  RFC2780          ||      S. Bradner, V. Paxson         ||       sob@harvard.edu, vern@aciri.org
  RFC2781          ||       P. Hoffman, F. Yergeau         ||        phoffman@imc.org, fyergeau@alis.com 
  RFC2782          ||      A. Gulbrandsen, P. Vixie, L. Esibov         ||       arnt@troll.no, levone@microsoft.com
  RFC2783          ||       J. Mogul, D. Mills, J. Brittenson, J. Stone, U. Windl         ||        mogul@wrl.dec.com, mills@udel.edu, jonathan@dsg.stanford.edu, ulrich.windl@rz.uni-regensburg.de 
  RFC2784          ||      D. Farinacci, T. Li, S. Hanks, D. Meyer, P. Traina         ||       dino@procket.com, tony1@home.net, stan_hanks@enron.net, dmm@cisco.com, pst@juniper.net
  RFC2785          ||       R. Zuccherato         ||        robert.zuccherato@entrust.com 
  RFC2786          ||       M. St. Johns         ||        stjohns@corp.home.net 
  RFC2787          ||      B. Jewell, D. Chuang         ||       bjewell@coppermountain.com, david_chuang@cosinecom.com
  RFC2788          ||       N. Freed, S. Kille         ||        ned.freed@innosoft.com, Steve.Kille@MessagingDirect.com 
  RFC2789          ||       N. Freed, S. Kille         ||        ned.freed@innosoft.com, Steve.Kille@MessagingDirect.com 
  RFC2790          ||       S. Waldbusser, P. Grillo         ||        waldbusser@ins.com 
  RFC2791          ||       J. Yu         ||        jyy@cosinecom.com 
  RFC2792          ||       M. Blaze, J. Ioannidis, A. Keromytis         ||         
  RFC2793          ||       G. Hellstrom         ||        gunnar.hellstrom@omnitor.se 
  RFC2794          ||       P. Calhoun, C. Perkins         ||         
  RFC2795          ||       S. Christey         ||        steqve@shore.net 
  RFC2796          ||       T. Bates, R. Chandra, E. Chen         ||        tbates@cisco.com, rchandra@redback.com, enke@redback.com 
  RFC2797          ||      M. Myers, X. Liu, J. Schaad, J. Weinstein         ||       mmyers@verisign.com, xliu@cisco.com, jimsch@nwlink.com, jsw@meer.net
  RFC2798          ||       M. Smith         ||        mcs@netscape.com 
  RFC2799          ||       S. Ginoza         ||        ginoza@isi.edu 
  RFC2800          ||       J. Reynolds, R. Braden, S. Ginoza         ||         
  RFC2801          ||       D. Burdett         ||        david.burdett@commerceone.com 
  RFC2802          ||       K. Davidson, Y. Kawatsura         ||        kent@differential.com, kawatura@bisd.hitachi.co.jp 
  RFC2803          ||       H. Maruyama, K. Tamura, N. Uramoto         ||        maruyama@jp.ibm.com, kent@trl.ibm.co.jp, uramoto@jp.ibm.com 
  RFC2804          ||      IAB, IESG         ||       fred@cisco.com, brian@icair.org
  RFC2805          ||       N. Greene, M. Ramalho, B. Rosen         ||        ngreene@nortelnetworks.com, mramalho@cisco.com, brosen@eng.fore.com 
  RFC2806          ||       A. Vaha-Sipila         ||        avs@iki.fi 
  RFC2807          ||       J. Reagle         ||        reagle@w3.org 
  RFC2808          ||       M. Nystrom         ||        magnus@rsasecurity.com 
  RFC2809          ||       B. Aboba, G. Zorn         ||        bernarda@microsoft.com, gwz@cisco.com 
  RFC2810          ||      C. Kalt         ||       Christophe.Kalt@gmail.com
  RFC2811          ||      C. Kalt         ||       Christophe.Kalt@gmail.com
  RFC2812          ||      C. Kalt         ||       Christophe.Kalt@gmail.com
  RFC2813          ||      C. Kalt         ||       Christophe.Kalt@gmail.com
  RFC2814          ||       R. Yavatkar, D. Hoffman, Y. Bernet, F. Baker, M. Speer         ||        yavatkar@ibeam.intel.com, yoramb@microsoft.com, fred@cisco.com, speer@Eng.Sun.COM 
  RFC2815          ||       M. Seaman, A. Smith, E. Crawley, J. Wroclawski         ||        andrew@extremenetworks.com, jtw@lcs.mit.edu 
  RFC2816          ||       A. Ghanwani, J. Pace, V. Srinivasan, A. Smith, M. Seaman         ||        aghanwan@nortelnetworks.com, pacew@us.ibm.com, vijay@cosinecom.com, andrew@extremenetworks.com 
  RFC2817          ||      R. Khare, S. Lawrence         ||       rohit@4K-associates.com, lawrence@agranat.com
  RFC2818          ||      E. Rescorla         ||       ekr@rtfm.com
  RFC2819          ||       S. Waldbusser         ||         
  RFC2820          ||      E. Stokes, D. Byrne, B. Blakley, P. Behera         ||       blakley@dascom.com, stokes@austin.ibm.com, djbyrne@us.ibm.com, prasanta@netscape.com
  RFC2821          ||      J. Klensin, Ed.         ||       
  RFC2822          ||      P. Resnick, Ed.         ||       presnick@qti.qualcomm.com
  RFC2823          ||       J. Carlson, P. Langner, E. Hernandez-Valencia, J. Manchester         ||        james.d.carlson@sun.com, plangner@lucent.com, enrique@lucent.com, sterling@hotair.hobl.lucent.com 
  RFC2824          ||       J. Lennox, H. Schulzrinne         ||        lennox@cs.columbia.edu, schulzrinne@cs.columbia.edu 
  RFC2825          ||       IAB, L. Daigle, Ed.         ||        iab@iab.org 
  RFC2826          ||       Internet Architecture Board         ||        iab@iab.org 
  RFC2827          ||      P. Ferguson, D. Senie         ||       ferguson@cisco.com, dts@senie.com
  RFC2828          ||      R. Shirey         ||       rshirey@bbn.com
  RFC2829          ||       M. Wahl, H. Alvestrand, J. Hodges, R. Morgan         ||        M.Wahl@innosoft.com, Harald@Alvestrand.no, JHodges@oblix.com, rlmorgan@washington.edu 
  RFC2830          ||       J. Hodges, R. Morgan, M. Wahl         ||        JHodges@oblix.com, rlmorgan@washington.edu, M.Wahl@innosoft.com 
  RFC2831          ||      P. Leach, C. Newman         ||       paulle@microsoft.com, chris.newman@innosoft.com
  RFC2832          ||       S. Hollenbeck, M. Srivastava         ||        shollenb@netsol.com, manojs@netsol.com 
  RFC2833          ||       H. Schulzrinne, S. Petrack         ||        schulzrinne@cs.columbia.edu, scott.petrack@metatel.com 
  RFC2834          ||      J.-M. Pittet         ||       jmp@sgi.com
  RFC2835          ||      J.-M. Pittet         ||       jmp@sgi.com
  RFC2836          ||       S. Brim, B. Carpenter, F. Le Faucheur         ||        sbrim@cisco.com, brian@icair.org, flefauch@cisco.com 
  RFC2837          ||       K. Teow         ||         
  RFC2838          ||       D. Zigmond, M. Vickers         ||        djz@corp.webtv.net, mav@liberate.com 
  RFC2839          ||       F. da Cruz, J. Altman         ||         
  RFC2840          ||       J. Altman, F. da Cruz         ||         
  RFC2841          ||       P. Metzger, W. Simpson         ||         
  RFC2842          ||       R. Chandra, J. Scudder         ||        rchandra@redback.com, jgs@cisco.com 
  RFC2843          ||       P. Droz, T. Przygienda         ||        dro@zurich.ibm.com, prz@siara.com 
  RFC2844          ||       T. Przygienda, P. Droz, R. Haas         ||        prz@siara.com, dro@zurich.ibm.com, rha@zurich.ibm.com 
  RFC2845          ||      P. Vixie, O. Gudmundsson, D. Eastlake 3rd, B. Wellington         ||       vixie@isc.org, ogud@tislabs.com, dee3@torque.pothole.com, Brian.Wellington@nominum.com
  RFC2846          ||       C. Allocchio         ||         
  RFC2847          ||       M. Eisler         ||        mike@eisler.com 
  RFC2848          ||       S. Petrack, L. Conroy         ||        scott.petrack@metatel.com, lwc@roke.co.uk 
  RFC2849          ||      G. Good         ||       ggood@netscape.com
  RFC2850          ||       Internet Architecture Board, B. Carpenter, Ed.         ||        brian@icair.org 
  RFC2851          ||       M. Daniele, B. Haberman, S. Routhier, J. Schoenwaelder         ||        daniele@zk3.dec.com, haberman@nortelnetworks.com, sar@epilogue.com, schoenw@ibr.cs.tu-bs.de 
  RFC2852          ||       D. Newman         ||        dan.newman@sun.com 
  RFC2853          ||      J. Kabat, M. Upadhyay         ||       jackk@valicert.com, mdu@eng.sun.com
  RFC2854          ||       D. Connolly, L. Masinter         ||        connolly@w3.org, LM@att.com 
  RFC2855          ||       K. Fujisawa         ||        fujisawa@sm.sony.co.jp 
  RFC2856          ||       A. Bierman, K. McCloghrie, R. Presuhn         ||       andy@yumaworks.com, kzm@cisco.com, rpresuhn@bmc.com 
  RFC2857          ||       A. Keromytis, N. Provos         ||        angelos@dsl.cis.upenn.edu, provos@citi.umich.edu, rgm@icsa.net, tytso@valinux.com 
  RFC2858          ||      T. Bates, Y. Rekhter, R. Chandra, D. Katz         ||       tbates@cisco.com, rchandra@redback.com, dkatz@jnx.com, yakov@cisco.com
  RFC2859          ||       W. Fang, N. Seddigh, B. Nandy         ||        wfang@cs.princeton.edu, nseddigh@nortelnetworks.com, bnandy@nortelnetworks.com 
  RFC2860          ||       B. Carpenter, F. Baker, M. Roberts         ||        brian@icair.org, fred@cisco.com, roberts@icann.org 
  RFC2861          ||      M. Handley, J. Padhye, S. Floyd         ||       mjh@aciri.org, padhye@aciri.org, floyd@aciri.org
  RFC2862          ||       M. Civanlar, G. Cash         ||        civanlar@research.att.com, glenn@research.att.com 
  RFC2863          ||       K. McCloghrie, F. Kastenholz         ||        kzm@cisco.com, kasten@argon.com 
  RFC2864          ||       K. McCloghrie, G. Hanson         ||        kzm@cisco.com, gary_hanson@adc.com 
  RFC2865          ||      C. Rigney, S. Willens, A. Rubens, W. Simpson         ||       cdr@telemancy.com, acr@merit.edu, wsimpson@greendragon.com, steve@livingston.com
  RFC2866          ||      C. Rigney         ||       cdr@telemancy.com
  RFC2867          ||       G. Zorn, B. Aboba, D. Mitton         ||        gwz@cisco.com, dmitton@nortelnetworks.com, aboba@internaut.com 
  RFC2868          ||      G. Zorn, D. Leifer, A. Rubens, J. Shriver, M. Holdrege, I. Goyret         ||       gwz@cisco.com, leifer@del.com, John.Shriver@intel.com, acr@del.com, matt@ipverse.com, igoyret@lucent.com
  RFC2869          ||      C. Rigney, W. Willats, P. Calhoun         ||       cdr@telemancy.com, ward@cyno.com, pcalhoun@eng.sun.com, arubens@tutsys.com, bernarda@microsoft.com
  RFC2870          ||      R. Bush, D. Karrenberg, M. Kosters, R. Plzak         ||       randy@psg.com, daniel.karrenberg@ripe.net, markk@netsol.com, plzakr@saic.com
  RFC2871          ||       J. Rosenberg, H. Schulzrinne         ||         
  RFC2872          ||       Y. Bernet, R. Pabbati         ||        yoramb@microsoft.com, rameshpa@microsoft.com 
  RFC2873          ||       X. Xiao, A. Hannan, V. Paxson, E. Crabbe         ||        xipeng@gblx.net, alan@ivmg.net, edc@explosive.net, vern@aciri.org 
  RFC2874          ||      M. Crawford, C. Huitema         ||       crawdad@fnal.gov, huitema@microsoft.com
  RFC2875          ||      H. Prafullchandra, J. Schaad         ||       hemma@cp.net, jimsch@exmsft.com
  RFC2876          ||       J. Pawling         ||        john.pawling@wang.com 
  RFC2877          ||      T. Murphy Jr., P. Rieth, J. Stevens         ||       murphyte@us.ibm.com, rieth@us.ibm.com, jssteven@us.ibm.com
  RFC2878          ||       M. Higashiyama, F. Baker         ||        Mitsuru.Higashiyama@yy.anritsu.co.jp, fred.baker@cisco.com 
  RFC2879          ||       G. Klyne, L. McIntyre         ||        GK@ACM.ORG, Lloyd.McIntyre@pahv.xerox.com 
  RFC2880          ||       L. McIntyre, G. Klyne         ||        Lloyd.McIntyre@pahv.xerox.com, GK@ACM.ORG 
  RFC2881          ||       D. Mitton, M. Beadles         ||        dmitton@nortelnetworks.com, mbeadles@smartpipes.com 
  RFC2882          ||       D. Mitton         ||        dmitton@nortelnetworks.com 
  RFC2883          ||       S. Floyd, J. Mahdavi, M. Mathis, M. Podolsky         ||        floyd@aciri.org, mahdavi@novell.com, mathis@psc.edu, podolsky@eecs.berkeley.edu 
  RFC2884          ||       J. Hadi Salim, U. Ahmed         ||        hadi@nortelnetworks.com, ahmed@sce.carleton.ca 
  RFC2885          ||       F. Cuervo, N. Greene, C. Huitema, A. Rayhan, B. Rosen, J. Segers         ||         
  RFC2886          ||      T. Taylor         ||       tom.taylor.stds@gmail.com
  RFC2887          ||       M. Handley, S. Floyd, B. Whetten, R. Kermode, L. Vicisano, M. Luby         ||        mjh@aciri.org, floyd@aciri.org, whetten@talarian.com, Roger.Kermode@motorola.com, lorenzo@cisco.com, luby@digitalfountain.com 
  RFC2888          ||       P. Srisuresh         ||        srisuresh@yahoo.com 
  RFC2889          ||       R. Mandeville, J. Perser         ||        bob@cqos.com, jerry_perser@netcomsystems.com 
  RFC2890          ||      G. Dommety         ||       gdommety@cisco.com
  RFC2891          ||       T. Howes, M. Wahl, A. Anantha         ||        anoopa@microsoft.com, howes@loudcloud.com, Mark.Wahl@sun.com 
  RFC2892          ||       D. Tsiang, G. Suwala         ||        tsiang@cisco.com, gsuwala@cisco.com 
  RFC2893          ||       R. Gilligan, E. Nordmark         ||        gilligan@freegate.com, nordmark@eng.sun.com 
  RFC2894          ||       M. Crawford         ||        crawdad@fnal.gov 
  RFC2895          ||       A. Bierman, C. Bucci, R. Iddon         ||       andy@yumaworks.com, cbucci@cisco.com 
  RFC2896          ||       A. Bierman, C. Bucci, R. Iddon         ||        andy@yumaworks.com, cbucci@cisco.com 
  RFC2897          ||       D. Cromwell         ||        cromwell@nortelnetworks.com 
  RFC2898          ||      B. Kaliski         ||       bkaliski@rsasecurity.com
  RFC2899          ||       S. Ginoza         ||        ginoza@isi.edu 
  RFC2900          ||       J. Reynolds, R. Braden, S. Ginoza         ||         
  RFC2901          ||       Z. Wenzel, J. Klensin, R. Bush, S. Huter         ||        zita@nsrc.org, klensin@nsrc.org, randy@nsrc.org, sghuter@nsrc.org 
  RFC2902          ||       S. Deering, S. Hares, C. Perkins, R. Perlman         ||        deering@cisco.com, skh@nexthop.com, Radia.Perlman@sun.com, Charles.Perkins@nokia.com 
  RFC2903          ||       C. de Laat, G. Gross, L. Gommans, J. Vollbrecht, D. Spence         ||        delaat@phys.uu.nl, gmgross@lucent.com, jrv@interlinknetworks.com, dspence@interlinknetworks.com 
  RFC2904          ||       J. Vollbrecht, P. Calhoun, S. Farrell, L. Gommans, G. Gross, B. de Bruijn, C. de Laat, M. Holdrege, D. Spence         ||        pcalhoun@eng.sun.com, stephen.farrell@baltimore.ie, betty@euronet.nl, delaat@phys.uu.nl, matt@ipverse.com, dspence@interlinknetworks.com 
  RFC2905          ||       J. Vollbrecht, P. Calhoun, S. Farrell, L. Gommans, G. Gross, B. de Bruijn, C. de Laat, M. Holdrege, D. Spence         ||        jrv@interlinknetworks.com, pcalhoun@eng.sun.com, stephen.farrell@baltimore.ie, gmgross@lucent.com, betty@euronet.nl, delaat@phys.uu.nl, matt@ipverse.com, dspence@interlinknetworks.com 
  RFC2906          ||       S. Farrell, J. Vollbrecht, P. Calhoun, L. Gommans, G. Gross, B. de Bruijn, C. de Laat, M. Holdrege, D. Spence         ||        stephen.farrell@baltimore.ie, jrv@interlinknetworks.com, pcalhoun@eng.sun.com, gmgross@lucent.com, betty@euronet.nl, delaat@phys.uu.nl, matt@ipverse.com, dspence@interlinknetworks.com 
  RFC2907          ||       R. Kermode         ||        Roger.Kermode@motorola.com 
  RFC2908          ||      D. Thaler, M. Handley, D. Estrin         ||       dthaler@microsoft.com, mjh@aciri.org, estrin@usc.edu
  RFC2909          ||      P. Radoslavov, D. Estrin, R. Govindan, M. Handley, S. Kumar, D. Thaler         ||       pavlin@catarina.usc.edu, estrin@isi.edu, govindan@isi.edu, mjh@aciri.org, kkumar@usc.edu, dthaler@microsoft.com
  RFC2910          ||      R. Herriot, Ed., S. Butler, P. Moore, R. Turner, J. Wenn         ||       robert.herriot@pahv.xerox.com, sbutler@boi.hp.com, pmoore@peerless.com, jwenn@cp10.es.xerox.com, tom.hastings@alum.mit.edu, robert.herriot@pahv.xerox.com
  RFC2911          ||      T. Hastings, Ed., R. Herriot, R. deBry, S. Isaacson, P. Powell         ||       sisaacson@novell.com, tom.hastings@alum.mit.edu, robert.herriot@pahv.xerox.com, debryro@uvsc.edu, papowell@astart.com
  RFC2912          ||       G. Klyne         ||        GK@ACM.ORG 
  RFC2913          ||       G. Klyne         ||        GK@ACM.ORG 
  RFC2914          ||      S. Floyd         ||       
  RFC2915          ||       M. Mealling, R. Daniel         ||        michaelm@netsol.com, rdaniel@datafusion.net 
  RFC2916          ||      P. Faltstrom         ||       paf@cisco.com
  RFC2917          ||       K. Muthukrishnan, A. Malis         ||        mkarthik@lucent.com, Andy.Malis@vivacenetworks.com 
  RFC2918          ||      E. Chen         ||       enke@redback.com
  RFC2919          ||      R. Chandhok, G. Wenger         ||       chandhok@qualcomm.com, gwenger@qualcomm.com
  RFC2920          ||       N. Freed         ||        ned.freed@innosoft.com 
  RFC2921          ||       B. Fink         ||        fink@es.net 
  RFC2922          ||       A. Bierman, K. Jones         ||       andy@yumaworks.com, kejones@nortelnetworks.com 
  RFC2923          ||       K. Lahey         ||         
  RFC2924          ||       N. Brownlee, A. Blount         ||        n.brownlee@auckland.ac.nz, blount@alum.mit.edu 
  RFC2925          ||       K. White         ||        wkenneth@us.ibm.com 
  RFC2926          ||       J. Kempf, R. Moats, P. St. Pierre         ||        james.kempf@sun.com, rmoats@coreon.net, Pete.StPierre@Eng.Sun.COM 
  RFC2927          ||       M. Wahl         ||        Mark.Wahl@sun.com 
  RFC2928          ||      R. Hinden, S. Deering, R. Fink, T. Hain         ||       bob.hinden@gmail.com, deering@cisco.com, rlfink@lbl.gov, tonyhain@microsoft.com
  RFC2929          ||      D. Eastlake 3rd, E. Brunner-Williams, B. Manning         ||       Donald.Eastlake@motorola.com, brunner@engage.com, bmanning@isi.edu
  RFC2930          ||      D. Eastlake 3rd         ||       Donald.Eastlake@motorola.com
  RFC2931          ||       D. Eastlake 3rd         ||        Donald.Eastlake@motorola.com 
  RFC2932          ||      K. McCloghrie, D. Farinacci, D. Thaler         ||       kzm@cisco.com, dthaler@microsoft.com
  RFC2933          ||      K. McCloghrie, D. Farinacci, D. Thaler         ||       kzm@cisco.com, dthaler@microsoft.com
  RFC2934          ||       K. McCloghrie, D. Farinacci, D. Thaler, B. Fenner         ||        kzm@cisco.com, dthaler@microsoft.com, fenner@research.att.com 
  RFC2935          ||       D. Eastlake 3rd, C. Smith         ||        Donald.Eastlake@motorola.com, chris.smith@royalbank.com 
  RFC2936          ||       D. Eastlake 3rd, C. Smith, D. Soroka         ||        Donald.Eastlake@motorola.com, chris.smith@royalbank.com, dsoroka@us.ibm.com 
  RFC2937          ||       C. Smith         ||        cs@Eng.Sun.COM 
  RFC2938          ||       G. Klyne, L. Masinter         ||        GK@ACM.ORG, LMM@acm.org 
  RFC2939          ||      R. Droms         ||       droms@bucknell.edu
  RFC2940          ||       A. Smith, D. Partain, J. Seligson         ||        David.Partain@ericsson.com, jseligso@nortelnetworks.com 
  RFC2941          ||       T. Ts'o, Ed., J. Altman         ||        tytso@mit.edu, jaltman@columbia.edu 
  RFC2942          ||       T. Ts'o         ||         
  RFC2943          ||       R. Housley, T. Horting, P. Yee         ||        housley@spyrus.com, thorting@spyrus.com, yee@spyrus.com 
  RFC2944          ||       T. Wu         ||        tjw@cs.Stanford.EDU 
  RFC2945          ||       T. Wu         ||        tjw@cs.Stanford.EDU 
  RFC2946          ||       T. Ts'o         ||        tytso@mit.edu 
  RFC2947          ||       J. Altman         ||        jaltman@columbia.edu 
  RFC2948          ||       J. Altman         ||        jaltman@columbia.edu 
  RFC2949          ||       J. Altman         ||        jaltman@columbia.edu 
  RFC2950          ||       J. Altman         ||        jaltman@columbia.edu 
  RFC2951          ||       R. Housley, T. Horting, P. Yee         ||        housley@spyrus.com, thorting@spyrus.com, yee@spyrus.com 
  RFC2952          ||       T. Ts'o         ||        tytso@mit.edu 
  RFC2953          ||       T. Ts'o         ||        tytso@mit.edu 
  RFC2954          ||       K. Rehbehn, D. Fowler         ||        krehbehn@megisto.com, fowler@syndesis.com 
  RFC2955          ||       K. Rehbehn, O. Nicklass, G. Mouradian         ||        krehbehn@megisto.com, orly_n@rad.co.il, gvm@att.com 
  RFC2956          ||       M. Kaat         ||        Marijke.Kaat@surfnet.nl 
  RFC2957          ||       L. Daigle, P. Faltstrom         ||        paf@cisco.com 
  RFC2958          ||       L. Daigle, P. Faltstrom         ||        paf@cisco.com 
  RFC2959          ||       M. Baugher, B. Strahm, I. Suconick         ||        mbaugher@passedge.com, Bill.Strahm@intel.com, irina@ennovatenetworks.com 
  RFC2960          ||      R. Stewart, Q. Xie, K. Morneault, C. Sharp, H. Schwarzbauer, T. Taylor, I. Rytina, M. Kalla, L. Zhang, V. Paxson         ||       randall@lakerest.net, qxie1@email.mot.com, kmorneau@cisco.com, chsharp@cisco.com, HannsJuergen.Schwarzbauer@icn.siemens.de, tom.taylor.stds@gmail.com, ian.rytina@ericsson.com, mkalla@telcordia.com, lixia@cs.ucla.edu, vern@aciri.org
  RFC2961          ||      L. Berger, D. Gan, G. Swallow, P. Pan, F. Tommasi, S. Molendini         ||       lberger@labn.net, swallow@cisco.com, franco.tommasi@unile.it, molendini@ultra5.unile.it
  RFC2962          ||       D. Raz, J. Schoenwaelder, B. Sugla         ||        raz@lucent.com, schoenw@ibr.cs.tu-bs.de, sugla@ispsoft.com 
  RFC2963          ||       O. Bonaventure, S. De Cnodder         ||        Olivier.Bonaventure@info.fundp.ac.be, stefaan.de_cnodder@alcatel.be 
  RFC2964          ||       K. Moore, N. Freed         ||        moore@cs.utk.edu, ned.freed@innosoft.com 
  RFC2965          ||      D. Kristol, L. Montulli         ||       
  RFC2966          ||      T. Li, T. Przygienda, H. Smit         ||       tli@procket.com, prz@redback.com, henk@procket.com
  RFC2967          ||       L. Daigle, R. Hedberg         ||        leslie@thinkingcat.com, Roland@catalogix.se 
  RFC2968          ||       L. Daigle, T. Eklof         ||        leslie@thinkingcat.com, thommy.eklof@hotsip.com 
  RFC2969          ||       T. Eklof, L. Daigle         ||        thommy.eklof@hotsip.com, leslie@thinkingcat.com 
  RFC2970          ||       L. Daigle, T. Eklof         ||        leslie@thinkingcat.com, thommy.eklof@hotsip.com 
  RFC2971          ||       T. Showalter         ||        tjs@mirapoint.com 
  RFC2972          ||       N. Popp, M. Mealling, L. Masinter, K. Sollins         ||        LMM@acm.org, michaelm@netsol.com, nico@realnames.com, sollins@lcs.mit.edu 
  RFC2973          ||       R. Balay, D. Katz, J. Parker         ||        Rajesh.Balay@cosinecom.com, dkatz@juniper.net, jparker@axiowave.com 
  RFC2974          ||       M. Handley, C. Perkins, E. Whelan         ||        mjh@aciri.org, csp@isi.edu, e.whelan@cs.ucl.ac.uk 
  RFC2975          ||       B. Aboba, J. Arkko, D. Harrington         ||        bernarda@microsoft.com, Jari.Arkko@ericsson.com, dbh@cabletron.com 
  RFC2976          ||      S. Donovan         ||       
  RFC2977          ||       S. Glass, T. Hiller, S. Jacobs, C. Perkins         ||         
  RFC2978          ||       N. Freed, J. Postel         ||        ned.freed@innosoft.com 
  RFC2979          ||       N. Freed         ||        ned.freed@innosoft.com 
  RFC2980          ||      S. Barber         ||       sob@academ.com
  RFC2981          ||      R. Kavasseri, Ed.         ||       ramk@cisco.com 
  RFC2982          ||      R. Kavasseri, Ed.         ||       ramk@cisco.com 
  RFC2983          ||       D. Black         ||        black_david@emc.com 
  RFC2984          ||       C. Adams         ||        cadams@entrust.com 
  RFC2985          ||       M. Nystrom, B. Kaliski         ||        magnus@rsasecurity.com, bkaliski@rsasecurity.com 
  RFC2986          ||      M. Nystrom, B. Kaliski         ||       magnus@rsasecurity.com, bkaliski@rsasecurity.com
  RFC2987          ||       P. Hoffman         ||        phoffman@imc.org 
  RFC2988          ||      V. Paxson, M. Allman         ||       vern@aciri.org, mallman@grc.nasa.gov
  RFC2989          ||      B. Aboba, P. Calhoun, S. Glass, T. Hiller, P. McCann, H. Shiino, P. Walsh, G. Zorn, G. Dommety, C. Perkins, B. Patil, D. Mitton, S. Manning, M. Beadles, X. Chen, S. Sivalingham, A. Hameed, M. Munson, S. Jacobs, B. Lim, B. Hirschman, R. Hsu, H. Koo, M. Lipford, E. Campbell, Y. Xu, S. Baba, E. Jaques         ||       bernarda@microsoft.com, pcalhoun@eng.sun.com, steven.glass@sun.com, tom.hiller@lucent.com, mccap@lucent.com, hshiino@lucent.com, walshp@lucent.com, gwz@cisco.com, gdommety@cisco.com, charliep@iprg.nokia.com, Basavaraj.Patil@nokia.com, dmitton@nortelnetworks.com, smanning@nortelnetworks.com, mbeadles@smartpipes.com, xing.chen@usa.alcatel.com, s.sivalingham@ericsson.com, none, mmunson@mobilnet.gte.com, sjacobs@gte.com, bklim@lgic.co.kr, qa4053@email.mot.com, rhsu@qualcomm.com, hskoo@sta.samsung.com, mlipfo01@sprintspectrum.com, ed_campbell@3com.com, yxu@watercove.com, sbaba@tari.toshiba.com, ejaques@akamail.com
  RFC2990          ||       G. Huston         ||        gih@telstra.net 
  RFC2991          ||       D. Thaler, C. Hopps         ||        dthaler@dthaler.microsoft.com, chopps@nexthop.com 
  RFC2992          ||       C. Hopps         ||        chopps@nexthop.com 
  RFC2993          ||       T. Hain         ||        tonyhain@microsoft.com 
  RFC2994          ||       H. Ohta, M. Matsui         ||        hidenori@iss.isl.melco.co.jp, matsui@iss.isl.melco.co.jp 
  RFC2995          ||       H. Lu, Ed., I. Faynberg, J. Voelker, M. Weissman, W. Zhang, S. Rhim, J. Hwang, S. Ago, S. Moeenuddin, S. Hadvani, S. Nyckelgard, J. Yoakum, L. Robart         ||        faynberg@lucent.com, huilanlu@lucent.com, jvoelker@lucent.com, maw1@lucent.com, wzz@lucent.com, syrhim@kt.co.kr, jkhwang@kt.co.kr, ago@ssf.abk.nec.co.jp, moeen@asl.dl.nec.com, hadvani@asl.dl.nec.com, soren.m.nyckelgard@telia.se, yoakum@nortelnetworks.com, robart@nortelnetworks.com 
  RFC2996          ||       Y. Bernet         ||        yoramb@microsoft.com 
  RFC2997          ||       Y. Bernet, A. Smith, B. Davie         ||        Yoramb@microsoft.com, bsd@cisco.com 
  RFC2998          ||       Y. Bernet, P. Ford, R. Yavatkar, F. Baker, L. Zhang, M. Speer, R. Braden, B. Davie, J. Wroclawski, E. Felstaine         ||        yoramb@microsoft.com, raj.yavatkar@intel.com, peterf@microsoft.com, fred@cisco.com, lixia@cs.ucla.edu, speer@Eng.Sun.COM, braden@isi.edu, bsd@cisco.com, jtw@lcs.mit.edu 
  RFC2999          ||       S. Ginoza         ||        ginoza@isi.edu 
  RFC3000          ||      J. Reynolds, R. Braden, S. Ginoza, L. Shiota         ||       
  RFC3001          ||       M. Mealling         ||        michaelm@netsol.com 
  RFC3002          ||       D. Mitzel         ||        mitzel@iprg.nokia.com 
  RFC3003          ||       M. Nilsson         ||        nilsson@id3.org 
  RFC3004          ||       G. Stump, R. Droms, Y. Gu, R. Vyaghrapuri, A. Demirtjis, B. Beser, J. Privat         ||        stumpga@us.ibm.com, rdroms@cisco.com, yegu@microsoft.com, rameshv@microsoft.com, annd@microsoft.com 
  RFC3005          ||       S. Harris         ||        srh@merit.edu 
  RFC3006          ||       B. Davie, C. Iturralde, D. Oran, S. Casner, J. Wroclawski         ||        bsd@cisco.com, cei@cisco.com, oran@cisco.com, casner@acm.org, jtw@lcs.mit.edu 
  RFC3007          ||      B. Wellington         ||       Brian.Wellington@nominum.com
  RFC3008          ||       B. Wellington         ||        Brian.Wellington@nominum.com 
  RFC3009          ||      J. Rosenberg, H. Schulzrinne         ||       jdrosen@dynamicsoft.com, schulzrinne@cs.columbia.edu
  RFC3010          ||       S. Shepler, B. Callaghan, D. Robinson, R. Thurlow, C. Beame, M. Eisler, D. Noveck         ||        beame@bws.com, brent.callaghan@sun.com, mike@eisler.com, david.robinson@sun.com, robert.thurlow@sun.com 
  RFC3011          ||       G. Waters         ||         
  RFC3012          ||       C. Perkins, P. Calhoun         ||         
  RFC3013          ||       T. Killalea         ||        tomk@neart.org 
  RFC3014          ||       R. Kavasseri         ||        ramk@cisco.com 
  RFC3015          ||       F. Cuervo, N. Greene, A. Rayhan, C. Huitema, B. Rosen, J. Segers         ||         
  RFC3016          ||      Y. Kikuchi, T. Nomura, S. Fukunaga, Y. Matsui, H. Kimata         ||       yoshihiro.kikuchi@toshiba.co.jp, matsui@drl.mei.co.jp, t-nomura@ccm.cl.nec.co.jp, fukunaga444@oki.co.jp, kimata@nttvdt.hil.ntt.co.jp
  RFC3017          ||       M. Riegel, G. Zorn         ||        maximilian.riegel@icn.siemens.de, gwz@cisco.com 
  RFC3018          ||       A. Bogdanov         ||        a_bogdanov@iname.ru 
  RFC3019          ||      B. Haberman, R. Worzella         ||       haberman@nortelnetworks.com, worzella@us.ibm.com
  RFC3020          ||       P. Pate, B. Lynch, K. Rehbehn         ||        prayson.pate@overturenetworks.com, bob.lynch@overturenetworks.com, krehbehn@megisto.com 
  RFC3021          ||       A. Retana, R. White, V. Fuller, D. McPherson         ||        aretana@cisco.com, riw@cisco.com, vaf@valinor.barrnet.net, danny@ambernetworks.com 
  RFC3022          ||       P. Srisuresh, K. Egevang         ||        srisuresh@yahoo.com, kjeld.egevang@intel.com 
  RFC3023          ||      M. Murata, S. St. Laurent, D. Kohn         ||       mmurata@trl.ibm.co.jp, simonstl@simonstl.com, dan@dankohn.com
  RFC3024          ||       G. Montenegro, Ed.         ||         
  RFC3025          ||       G. Dommety, K. Leung         ||        gdommety@cisco.com, kleung@cisco.com 
  RFC3026          ||       R. Blane         ||        Roy_Blane@inmarsat.com 
  RFC3027          ||       M. Holdrege, P. Srisuresh         ||        matt@ipverse.com, srisuresh@yahoo.com 
  RFC3028          ||      T. Showalter         ||       tjs@mirapoint.com
  RFC3029          ||       C. Adams, P. Sylvester, M. Zolotarev, R. Zuccherato         ||        cadams@entrust.com, mzolotarev@baltimore.com, peter.sylvester@edelweb.fr, robert.zuccherato@entrust.com 
  RFC3030          ||       G. Vaudreuil         ||        GregV@ieee.org 
  RFC3031          ||      E. Rosen, A. Viswanathan, R. Callon         ||       erosen@cisco.com, arun@force10networks.com, rcallon@juniper.net
  RFC3032          ||      E. Rosen, D. Tappan, G. Fedorkow, Y. Rekhter, D. Farinacci, T. Li, A. Conta         ||       erosen@cisco.com, tappan@cisco.com, yakov@juniper.net, fedorkow@cisco.com, dino@procket.com, tli@procket.com, aconta@txc.com
  RFC3033          ||       M. Suzuki         ||        suzuki.muneyoshi@lab.ntt.co.jp 
  RFC3034          ||       A. Conta, P. Doolan, A. Malis         ||        aconta@txc.com, pdoolan@ennovatenetworks.com, Andy.Malis@vivacenetworks.com 
  RFC3035          ||       B. Davie, J. Lawrence, K. McCloghrie, E. Rosen, G. Swallow, Y. Rekhter, P. Doolan         ||        bsd@cisco.com, pdoolan@ennovatenetworks.com, jlawrenc@cisco.com, kzm@cisco.com, yakov@juniper.net, erosen@cisco.com, swallow@cisco.com 
  RFC3036          ||      L. Andersson, P. Doolan, N. Feldman, A. Fredette, B. Thomas         ||       loa.andersson@nortelnetworks.com, pdoolan@ennovatenetworks.com, nkf@us.ibm.com, fredette@photonex.com, rhthomas@cisco.com
  RFC3037          ||       B. Thomas, E. Gray         ||        ewgray@mindspring.com, rhthomas@cisco.com 
  RFC3038          ||      K. Nagami, Y. Katsube, N. Demizu, H. Esaki, P. Doolan         ||       ken.nagami@toshiba.co.jp, demizu@dd.iij4u.or.jp, hiroshi@wide.ad.jp, yasuhiro.katsube@toshiba.co.jp, pdoolan@ennovatenetworks.com
  RFC3039          ||       S. Santesson, W. Polk, P. Barzin, M. Nystrom         ||        stefan@addtrust.com, wpolk@nist.gov, barzin@secude.com, magnus@rsasecurity.com 
  RFC3040          ||       I. Cooper, I. Melve, G. Tomlinson         ||        icooper@equinix.com, Ingrid.Melve@uninett.no, gary.tomlinson@cacheflow.com 
  RFC3041          ||      T. Narten, R. Draves         ||       narten@raleigh.ibm.com, richdr@microsoft.com
  RFC3042          ||       M. Allman, H. Balakrishnan, S. Floyd         ||        mallman@grc.nasa.gov, hari@lcs.mit.edu, floyd@aciri.org 
  RFC3043          ||       M. Mealling         ||        michaelm@netsol.com 
  RFC3044          ||       S. Rozenfeld         ||         
  RFC3045          ||       M. Meredith         ||        mark_meredith@novell.com 
  RFC3046          ||      M. Patrick         ||       michael.patrick@motorola.com
  RFC3047          ||      P. Luthi         ||       luthip@pictel.com
  RFC3048          ||       B. Whetten, L. Vicisano, R. Kermode, M. Handley, S. Floyd, M. Luby         ||        whetten@talarian.com, lorenzo@cisco.com, Roger.Kermode@motorola.com, mjh@aciri.org, luby@digitalfountain.com 
  RFC3049          ||       J. Naugle, K. Kasthurirangan, G. Ledford         ||        jnaugle@us.ibm.com, kasthuri@us.ibm.com, gledford@zephyrcorp.com 
  RFC3050          ||       J. Lennox, H. Schulzrinne, J. Rosenberg         ||        lennox@cs.columbia.edu, jdrosen@dynamicsoft.com, schulzrinne@cs.columbia.edu 
  RFC3051          ||       J. Heath, J. Border         ||        jheath@hns.com, border@hns.com 
  RFC3052          ||       M. Eder, S. Nag         ||        michael.eder@nokia.com, thinker@monmouth.com 
  RFC3053          ||       A. Durand, P. Fasano, I. Guardini, D. Lento         ||        Alain.Durand@sun.com, paolo.fasano@cselt.it, ivano.guardini@cselt.it, dlento@mail.tim.it 
  RFC3054          ||       P. Blatherwick, R. Bell, P. Holland         ||        blather@nortelnetworks.com, rtbell@cisco.com, phil.holland@circa.ca 
  RFC3055          ||       M. Krishnaswamy, D. Romascanu         ||        murali@lucent.com, dromasca@gmail.com  
  RFC3056          ||       B. Carpenter, K. Moore         ||        brian@icair.org, moore@cs.utk.edu 
  RFC3057          ||       K. Morneault, S. Rengasami, M. Kalla, G. Sidebottom         ||        kmorneau@cisco.com, mkalla@telcordia.com, srengasa@telcordia.com, gregside@nortelnetworks.com 
  RFC3058          ||       S. Teiwes, P. Hartmann, D. Kuenzi         ||        stephan.teiwes@it-sec.com, peter.hartmann@it-sec.com, dkuenzi@724.com 
  RFC3059          ||       E. Guttman         ||        Erik.Guttman@sun.com 
  RFC3060          ||       B. Moore, E. Ellesson, J. Strassner, A. Westerinen         ||        eellesson@lboard.com, remoore@us.ibm.com, johns@cisco.com, andreaw@cisco.com 
  RFC3061          ||       M. Mealling         ||        michaelm@netsol.com 
  RFC3062          ||       K. Zeilenga         ||        Kurt@OpenLDAP.org 
  RFC3063          ||       Y. Ohba, Y. Katsube, E. Rosen, P. Doolan         ||        yoshihiro.ohba@toshiba.co.jp, yasuhiro.katsube@toshiba.co.jp, erosen@cisco.com, pdoolan@ennovatenetworks.com 
  RFC3064          ||       B. Foster         ||        bfoster@cisco.com 
  RFC3065          ||      P. Traina, D. McPherson, J. Scudder         ||       danny@ambernetworks.com, jgs@cisco.com
  RFC3066          ||       H. Alvestrand         ||        Harald@Alvestrand.no 
  RFC3067          ||       J. Arvidsson, A. Cormack, Y. Demchenko, J. Meijer         ||        Jimmy.J.Arvidsson@telia.se, Andrew.Cormack@ukerna.ac.uk, demch@terena.nl, jan.meijer@surfnet.nl 
  RFC3068          ||      C. Huitema         ||       huitema@microsoft.com
  RFC3069          ||       D. McPherson, B. Dykes         ||        danny@ambernetworks.com, bdykes@onesecure.com 
  RFC3070          ||       V. Rawat, R. Tio, S. Nanji, R. Verma         ||        vrawat@oni.com, tor@redback.com, rverma@dc.com, suhail@redback.com 
  RFC3071          ||       J. Klensin         ||        klensin@jck.com 
  RFC3072          ||       M. Wildgrube         ||        max@wildgrube.com 
  RFC3073          ||       J. Collins         ||        jcollins@bitstream.com 
  RFC3074          ||       B. Volz, S. Gonczi, T. Lemon, R. Stevens         ||        bernie.volz@ericsson.com, steve.gonczi@networkengines.com, ted.lemon@nominum.com, robs@join.com 
  RFC3075          ||       D. Eastlake 3rd, J. Reagle, D. Solo         ||        Donald.Eastlake@motorola.com, reagle@w3.org, dsolo@alum.mit.edu 
  RFC3076          ||       J. Boyer         ||        jboyer@PureEdge.com 
  RFC3077          ||       E. Duros, W. Dabbous, H. Izumiyama, N. Fujii, Y. Zhang         ||         
  RFC3078          ||       G. Pall, G. Zorn         ||        gurdeep@microsoft.com, gwz@cisco.com 
  RFC3079          ||       G. Zorn         ||        gwz@cisco.com 
  RFC3080          ||      M. Rose         ||       mrose17@gmail.com
  RFC3081          ||       M. Rose         ||       mrose17@gmail.com
  RFC3082          ||       J. Kempf, J. Goldschmidt         ||        james.kempf@sun.com, jason.goldschmidt@sun.com 
  RFC3083          ||       R. Woundy         ||        rwoundy@cisco.com 
  RFC3084          ||      K. Chan, J. Seligson, D. Durham, S. Gai, K. McCloghrie, S. Herzog, F. Reichmeyer, R. Yavatkar, A. Smith         ||       khchan@nortelnetworks.com, sgai@cisco.com, Herzog@iphighway.com, kzm@cisco.com, franr@pfn.com, raj.yavatkar@intel.com, andrew@allegronetworks.com
  RFC3085          ||       A. Coates, D. Allen, D. Rivers-Moore         ||        tony.coates@reuters.com, ho73@dial.pipex.com, daniel.rivers-moore@rivcom.com 
  RFC3086          ||       K. Nichols, B. Carpenter         ||        nichols@packetdesign.com, brian@icair.org 
  RFC3087          ||       B. Campbell, R. Sparks         ||        bcampbell@dynamicsoft.com, rsparks@dynamicsoft.com 
  RFC3088          ||       K. Zeilenga         ||        kurt@openldap.org 
  RFC3089          ||       H. Kitamura         ||        kitamura@da.jp.nec.com 
  RFC3090          ||       E. Lewis         ||        lewis@tislabs.com 
  RFC3091          ||       H. Kennedy         ||        kennedyh@engin.umich.edu 
  RFC3092          ||      D. Eastlake 3rd, C. Manros, E. Raymond         ||       Donald.Eastlake@motorola.com, manros@cp10.es.xerox.com, esr@thyrsus.com
  RFC3093          ||       M. Gaynor, S. Bradner         ||         
  RFC3094          ||       D. Sprague, R. Benedyk, D. Brendes, J. Keller         ||        david.sprague@tekelec.com, dan.brendes@tekelec.com, robby.benedyk@tekelec.com, joe.keller@tekelec.com 
  RFC3095          ||       C. Bormann, C. Burmeister, M. Degermark, H. Fukushima, H. Hannu, L-E. Jonsson, R. Hakenberg, T. Koren, K. Le, Z. Liu, A. Martensson, A. Miyazaki, K. Svanbro, T. Wiebke, T. Yoshimura, H. Zheng         ||        cabo@tzi.org, burmeister@panasonic.de, micke@cs.arizona.edu, fukusima@isl.mei.co.jp, hans.hannu@ericsson.com, lars-erik.jonsson@ericsson.com, hakenberg@panasonic.de, tmima@cisco.com, khiem.le@nokia.com, zhigang.liu@nokia.com, anton.martensson@era.ericsson.se, akihiro@isl.mei.co.jp, krister.svanbro@ericsson.com, wiebke@panasonic.de, yoshi@spg.yrp.nttdocomo.co.jp, haihong.zheng@nokia.com 
  RFC3096          ||       M. Degermark, Ed.         ||         
  RFC3097          ||       R. Braden, L. Zhang         ||        Braden@ISI.EDU, lixia@cs.ucla.edu 
  RFC3098          ||       T. Gavin, D. Eastlake 3rd, S. Hambridge         ||        tedgavin@newsguy.com, Donald.Eastlake@motorola.com, sallyh@ludwig.sc.intel.com 
  RFC3099          ||       S. Ginoza         ||        ginoza@isi.edu 
  RFC3100          ||               ||         
  RFC3101          ||       P. Murphy         ||        pmurphy@noc.usgs.net 
  RFC3102          ||       M. Borella, J. Lo, D. Grabelsky, G. Montenegro         ||        mike_borella@commworks.com, yidarlo@yahoo.com, david_grabelsky@commworks.com, gab@sun.com 
  RFC3103          ||       M. Borella, D. Grabelsky, J. Lo, K. Taniguchi         ||        mike_borella@commworks.com, david_grabelsky@commworks.com, yidarlo@yahoo.com, taniguti@ccrl.sj.nec.com 
  RFC3104          ||       G. Montenegro, M. Borella         ||        gab@sun.com, mike_borella@commworks.com 
  RFC3105          ||       J. Kempf, G. Montenegro         ||        gab@sun.com 
  RFC3106          ||       D. Eastlake 3rd, T. Goldstein         ||        Donald.Eastlake@motorola.com, tgoldstein@brodia.com 
  RFC3107          ||      Y. Rekhter, E. Rosen         ||       yakov@juniper.net, erosen@cisco.com
  RFC3108          ||       R. Kumar, M. Mostafa         ||        rkumar@cisco.com, mmostafa@cisco.com 
  RFC3109          ||       R. Braden, R. Bush, J. Klensin         ||        braden@isi.edu, randy@psg.com, klensin@jck.com 
  RFC3110          ||      D. Eastlake 3rd         ||       Donald.Eastlake@motorola.com
  RFC3111          ||       E. Guttman         ||        Erik.Guttman@germany.sun.com 
  RFC3112          ||       K. Zeilenga         ||        Kurt@OpenLDAP.org 
  RFC3113          ||       K. Rosenbrock, R. Sanmugam, S. Bradner, J. Klensin         ||        rosenbrock@etsi.fr, sob@harvard.edu, 3GPPContact@etsi.fr 
  RFC3114          ||      W. Nicolls         ||       wnicolls@forsythesolutions.com
  RFC3115          ||       G. Dommety, K. Leung         ||        gdommety@cisco.com, kleung@cisco.com 
  RFC3116          ||       J. Dunn, C. Martin         ||        Jeffrey.Dunn@worldnet.att.net, Cynthia.E.Martin@worldnet.att.net 
  RFC3117          ||       M. Rose         ||       mrose17@gmail.com
  RFC3118          ||      R. Droms, Ed., W. Arbaugh, Ed.         ||       
  RFC3119          ||      R. Finlayson         ||       finlayson@live.com
  RFC3120          ||       K. Best, N. Walsh         ||        karl.best@oasis-open.org, Norman.Walsh@East.Sun.COM 
  RFC3121          ||       K. Best, N. Walsh         ||        karl.best@oasis-open.org, Norman.Walsh@East.Sun.COM 
  RFC3122          ||       A. Conta         ||        aconta@txc.com 
  RFC3123          ||       P. Koch         ||        pk@TechFak.Uni-Bielefeld.DE 
  RFC3124          ||       H. Balakrishnan, S. Seshan         ||        hari@lcs.mit.edu, srini@cmu.edu 
  RFC3125          ||       J. Ross, D. Pinkas, N. Pope         ||        harri.rasilainen@etsi.fr, ross@secstan.com, Denis.Pinkas@bull.net, pope@secstan.com 
  RFC3126          ||      D. Pinkas, J. Ross, N. Pope         ||       harri.rasilainen@etsi.fr, Denis.Pinkas@bull.net, ross@secstan.com, pope@secstan.com
  RFC3127          ||       D. Mitton, M. St.Johns, S. Barkley, D. Nelson, B. Patil, M. Stevens, B. Wolff         ||        dmitton@nortelnetworks.com, stjohns@rainmakertechnologies.com, stuartb@uu.net, dnelson@enterasys.com, Basavaraj.Patil@nokia.com, mstevens@ellacoya.com, barney@databus.com 
  RFC3128          ||       I. Miller         ||        Ian_Miller@singularis.ltd.uk 
  RFC3129          ||       M. Thomas         ||        mat@cisco.com 
  RFC3130          ||       E. Lewis         ||         
  RFC3131          ||       S. Bradner, P. Calhoun, H. Cuschieri, S. Dennett, G. Flynn, M. Lipford, M. McPheters         ||        sob@harvard.edu, pcalhoun@eng.sun.com, hcuschie@tia.eia.org, S.Dennett@motorola.com, gerry.flynn@verizonwireless.com, mjmcpheters@lucent.com 
  RFC3132          ||       J. Kempf         ||         
  RFC3133          ||       J. Dunn, C. Martin         ||         
  RFC3134          ||       J. Dunn, C. Martin         ||         
  RFC3135          ||       J. Border, M. Kojo, J. Griner, G. Montenegro, Z. Shelby         ||        border@hns.com, kojo@cs.helsinki.fi, jgriner@grc.nasa.gov, gab@sun.com, zach.shelby@ee.oulu.fi 
  RFC3136          ||       L. Slutsman, Ed., I. Faynberg, H. Lu, M. Weissman         ||        faynberg@lucent.com, huilanlu@lucent.com, maw1@lucent.com, lslutsman@att.com 
  RFC3137          ||      A. Retana, L. Nguyen, R. White, A. Zinin, D. McPherson         ||       aretana@cisco.com, lhnguyen@cisco.com, riw@cisco.com, azinin@nexsi.com, danny@ambernetworks.com
  RFC3138          ||      D. Meyer         ||       dmm@sprint.net
  RFC3139          ||       L. Sanchez, K. McCloghrie, J. Saperia         ||        kzm@cisco.com, lsanchez@megisto.com, saperia@jdscons.com 
  RFC3140          ||       D. Black, S. Brim, B. Carpenter, F. Le Faucheur         ||        black_david@emc.com, sbrim@cisco.com, brian@icair.org, flefauch@cisco.com 
  RFC3141          ||       T. Hiller, P. Walsh, X. Chen, M. Munson, G. Dommety, S. Sivalingham, B. Lim, P. McCann, H. Shiino, B. Hirschman, S. Manning, R. Hsu, H. Koo, M. Lipford, P. Calhoun, C. Lo, E. Jaques, E. Campbell, Y.Xu,S.Baba,T.Ayaki,T.Seki,A.Hameed         ||        pcalhoun@eng.sun.com, gdommety@cisco.com, tom.hiller@lucent.com, rhsu@qualcomm.com, mlipfo01@sprintspectrum.com, serge@awardsolutions.com, mccap@lucent.com, mmunson@gte.net, hskoo@sta.samsung.com, walshp@lucent.com, yxu@watercove.com, qa4053@email.mot.com, ejaques@akamail.com, s.sivalingham@ericsson.com, xing.chen@usa.alcatel.com, bklim@lge.com, hshiino@lucent.com, sbaba@tari.toshiba.com, ayaki@ddi.co.jp, Charles.Lo@vodafone-us.com, t-seki@kddi.com 
  RFC3142          ||       J. Hagino, K. Yamamoto         ||        itojun@iijlab.net, kazu@iijlab.net 
  RFC3143          ||       I. Cooper, J. Dilley         ||        icooper@equinix.com, jad@akamai.com 
  RFC3144          ||       D. Romascanu         ||        dromasca@gmail.com  
  RFC3145          ||       R. Verma, M. Verma, J. Carlson         ||        rverma@dc.com, Madhvi_Verma@3com.com, james.d.carlson@sun.com 
  RFC3146          ||      K. Fujisawa, A. Onoe         ||       fujisawa@sm.sony.co.jp, onoe@sm.sony.co.jp
  RFC3147          ||       P. Christian         ||        christi@nortelnetworks.com 
  RFC3148          ||       M. Mathis, M. Allman         ||        mathis@psc.edu, mallman@bbn.com 
  RFC3149          ||       A. Srinath, G. Levendel, K. Fritz, R. Kalyanaram         ||        Ashok.Srinath@sylantro.com, Gil.Levendel@sylantro.com, Kent.Fritz@sylantro.com, Raghuraman.Kal@wipro.com 
  RFC3150          ||       S. Dawkins, G. Montenegro, M. Kojo, V. Magret         ||        spencer.dawkins@fnc.fujitsu.com, gab@sun.com, kojo@cs.helsinki.fi, vincent.magret@alcatel.com 
  RFC3151          ||       N. Walsh, J. Cowan, P. Grosso         ||        Norman.Walsh@East.Sun.COM, jcowan@reutershealth.com, pgrosso@arbortext.com 
  RFC3152          ||       R. Bush         ||        randy@psg.com 
  RFC3153          ||       R. Pazhyannur, I. Ali, C. Fox         ||        pazhynnr@cig.mot.com, fia225@email.mot.com, fox@cisco.com 
  RFC3154          ||       J. Kempf, C. Castelluccia, P. Mutaf, N. Nakajima, Y. Ohba, R. Ramjee, Y. Saifullah, B. Sarikaya, X. Xu         ||        James.Kempf@Sun.COM, pars.mutaf@inria.fr, claude.castelluccia@inria.fr, nnakajima@tari.toshiba.com, yohba@tari.toshiba.com, ramjee@bell-labs.com, Yousuf.Saifullah@nokia.com, Behcet.Sarikaya@usa.alcatel.com 
  RFC3155          ||       S. Dawkins, G. Montenegro, M. Kojo, V. Magret, N. Vaidya         ||        spencer.dawkins@fnc.fujitsu.com, gab@sun.com, kojo@cs.helsinki.fi, vincent.magret@alcatel.com 
  RFC3156          ||       M. Elkins, D. Del Torto, R. Levien, T. Roessler         ||         
  RFC3157          ||       A. Arsenault, S. Farrell         ||        aarsenault@dvnet.com, stephen.farrell@baltimore.ie 
  RFC3158          ||       C. Perkins, J. Rosenberg, H. Schulzrinne         ||        csp@isi.edu, jdrosen@dynamicsoft.com, schulzrinne@cs.columbia.edu 
  RFC3159          ||      K. McCloghrie, M. Fine, J. Seligson, K. Chan, S. Hahn, R. Sahita, A. Smith, F. Reichmeyer         ||       mfine@cisco.com, jseligso@nortelnetworks.com, khchan@nortelnetworks.com, scott.hahn@intel.com, ravi.sahita@intel.com, andrew@allegronetworks.com, franr@pfn.com
  RFC3160          ||      S. Harris         ||       
  RFC3161          ||      C. Adams, P. Cain, D. Pinkas, R. Zuccherato         ||       cadams@entrust.com, pcain@bbn.com, Denis.Pinkas@bull.net, robert.zuccherato@entrust.com
  RFC3162          ||      B. Aboba, G. Zorn, D. Mitton         ||       bernarda@microsoft.com, gwz@cisco.com
  RFC3163          ||       R. Zuccherato, M. Nystrom         ||        robert.zuccherato@entrust.com, magnus@rsasecurity.com 
  RFC3164          ||      C. Lonvick         ||       clonvick@cisco.com
  RFC3165          ||       D. Levi, J. Schoenwaelder         ||         
  RFC3166          ||       D. Meyer, J. Scudder         ||        dmm@sprint.net, jgs@cisco.com 
  RFC3167          ||       D. Meyer, J. Scudder         ||        dmm@sprint.net, jgs@cisco.com 
  RFC3168          ||      K. Ramakrishnan, S. Floyd, D. Black         ||       kk@teraoptic.com, floyd@aciri.org, black_david@emc.com
  RFC3169          ||       M. Beadles, D. Mitton         ||        dmitton@nortelnetworks.com 
  RFC3170          ||       B. Quinn, K. Almeroth         ||        bquinn@celoxnetworks.com, almeroth@cs.ucsb.edu 
  RFC3171          ||      Z. Albanna, K. Almeroth, D. Meyer, M. Schipper         ||       zaid@juniper.net, almeroth@cs.ucsb.edu, dmm@sprint.net, iana@iana.org
  RFC3172          ||       G. Huston, Ed.         ||         
  RFC3173          ||       A. Shacham, B. Monsour, R. Pereira, M. Thomas         ||        shacham@shacham.net, bob@bobmonsour.com, royp@cisco.com, matt@3am-software.com 
  RFC3174          ||      D. Eastlake 3rd, P. Jones         ||       Donald.Eastlake@motorola.com, paulej@packetizer.com
  RFC3175          ||      F. Baker, C. Iturralde, F. Le Faucheur, B. Davie         ||       fred@cisco.com, cei@cisco.com, flefauch@cisco.com, bdavie@cisco.com
  RFC3176          ||       P. Phaal, S. Panchen, N. McKee         ||        peter_phaal@INMON.COM, sonia_panchen@INMON.COM, neil_mckee@INMON.COM 
  RFC3177          ||      IAB, IESG         ||       
  RFC3178          ||       J. Hagino, H. Snyder         ||        itojun@iijlab.net, hal@vailsys.com 
  RFC3179          ||       J. Schoenwaelder, J. Quittek         ||        schoenw@ibr.cs.tu-bs.de, quittek@ccrle.nec.de 
  RFC3180          ||       D. Meyer, P. Lothberg         ||        dmm@sprint.net, roll@sprint.net 
  RFC3181          ||       S. Herzog         ||        herzog@policyconsulting.com 
  RFC3182          ||       S. Yadav, R. Yavatkar, R. Pabbati, P. Ford, T. Moore, S. Herzog, R. Hess         ||        Satyendra.Yadav@intel.com, Raj.Yavatkar@intel.com, rameshpa@microsoft.com, peterf@microsoft.com, timmoore@microsoft.com, herzog@policyconsulting.com, rodney.hess@intel.com 
  RFC3183          ||       T. Dean, W. Ottaway         ||        tbdean@QinetiQ.com, wjottaway@QinetiQ.com 
  RFC3184          ||      S. Harris         ||       srh@merit.edu
  RFC3185          ||       S. Farrell, S. Turner         ||        stephen.farrell@baltimore.ie, turners@ieca.com 
  RFC3186          ||       S. Shimizu, T. Kawano, K. Murakami, E. Beier         ||        shimizu@ntt-20.ecl.net, kawano@core.ecl.net, murakami@ntt-20.ecl.net, Beier@bina.de 
  RFC3187          ||       J. Hakala, H. Walravens         ||        juha.hakala@helsinki.fi, hartmut.walravens@sbb.spk-berlin.de 
  RFC3188          ||       J. Hakala         ||        juha.hakala@helsinki.fi 
  RFC3189          ||      K. Kobayashi, A. Ogawa, S. Casner, C. Bormann         ||       ikob@koganei.wide.ad.jp, akimichi@sfc.wide.ad.jp, casner@acm.org, cabo@tzi.org
  RFC3190          ||       K. Kobayashi, A. Ogawa, S. Casner, C. Bormann         ||        ikob@koganei.wide.ad.jp, akimichi@sfc.wide.ad.jp, casner@acm.org, cabo@tzi.org 
  RFC3191          ||       C. Allocchio         ||         
  RFC3192          ||       C. Allocchio         ||         
  RFC3193          ||       B. Patel, B. Aboba, W. Dixon, G. Zorn, S. Booth         ||        baiju.v.patel@intel.com, bernarda@microsoft.com, wdixon@microsoft.com, gwz@cisco.com, ebooth@cisco.com 
  RFC3194          ||       A. Durand, C. Huitema         ||         
  RFC3195          ||       D. New, M. Rose         ||        dnew@san.rr.com, mrose17@gmail.com
  RFC3196          ||      T. Hastings, C. Manros, P. Zehler, C. Kugler, H. Holst         ||       tom.hastings@alum.mit.edu, Kugler@us.ibm.com, hh@I-data.com, Peter.Zehler@xerox.com
  RFC3197          ||       R. Austein         ||        sra@hactrn.net 
  RFC3198          ||      A. Westerinen, J. Schnizlein, J. Strassner, M. Scherling, B. Quinn, S. Herzog, A. Huynh, M. Carlson, J. Perry, S. Waldbusser         ||       andreaw@cisco.com, john.schnizlein@cisco.com, john.strassner@intelliden.com, mscherling@xcert.com, bquinn@celoxnetworks.com, jay.perry@netapp.com, herzog@PolicyConsulting.com, mark.carlson@sun.com, waldbusser@nextbeacon.com
  RFC3199          ||       S. Ginoza         ||        ginoza@isi.edu 
  RFC3200          ||               ||         
  RFC3201          ||       R. Steinberger, O. Nicklass         ||        robert.steinberger@fnc.fujitsu.com, Orly_n@rad.co.il 
  RFC3202          ||       R. Steinberger, O. Nicklass         ||        robert.steinberger@fnc.fujitsu.com, Orly_n@rad.co.il 
  RFC3203          ||      Y. T'Joens, C. Hublet, P. De Schrijver         ||       yves.tjoens@alcatel.be, p2@mind.be, Christian.Hublet@alcatel.be
  RFC3204          ||      E. Zimmerer, J. Peterson, A. Vemuri, L. Ong, F. Audet, M. Watson, M. Zonoun         ||       eric_zimmerer@yahoo.com, Aparna.Vemuri@Qwest.com, jon.peterson@neustar.com, lyndon_ong@yahoo.com, mzonoun@nortelnetworks.com, audet@nortelnetworks.com, mwatson@nortelnetworks.com
  RFC3205          ||       K. Moore         ||        moore@cs.utk.edu 
  RFC3206          ||       R. Gellens         ||        randy@qualcomm.com 
  RFC3207          ||      P. Hoffman         ||       phoffman@imc.org
  RFC3208          ||       T. Speakman, J. Crowcroft, J. Gemmell, D. Farinacci, S. Lin, D. Leshchiner, M. Luby, T. Montgomery, L. Rizzo, A. Tweedly, N. Bhaskar, R. Edmonstone, R. Sumanasekera, L. Vicisano         ||        speakman@cisco.com, dino@procket.com, steven@juniper.net, agt@cisco.com, nbhaskar@cisco.com, redmonst@cisco.com, rajitha@cisco.com, lorenzo@cisco.com, j.crowcroft@cs.ucl.ac.uk, jgemmell@microsoft.com, dleshc@tibco.com, luby@digitalfountain.com, todd@talarian.com, luigi@iet.unipi.it 
  RFC3209          ||      D. Awduche, L. Berger, D. Gan, T. Li, V. Srinivasan, G. Swallow         ||       awduche@movaz.com, lberger@movaz.com, dhg@juniper.net, tli@procket.com, vsriniva@cosinecom.com, swallow@cisco.com
  RFC3210          ||      D. Awduche, A. Hannan, X. Xiao         ||       awduche@movaz.com, alan@routingloop.com, xxiao@photuris.com 
  RFC3211          ||       P. Gutmann         ||        pgut001@cs.auckland.ac.nz 
  RFC3212          ||      B. Jamoussi, Ed., L. Andersson, R. Callon, R. Dantu, L. Wu, P. Doolan, T. Worster, N. Feldman, A. Fredette, M. Girish, E. Gray, J. Heinanen, T. Kilty, A. Malis         ||       loa.andersson@utfors.se, rcallon@juniper.net, rdantu@netrake.com, pdoolan@acm.org, Nkf@us.ibm.com, afredette@charter.net, eric.gray@sandburst.com, jh@song.fi, tim-kilty@mediaone.net, Andy.Malis@vivacenetworks.com, muckai@atoga.com, fsb@thefsb.org, liwwu@cisco.com
  RFC3213          ||       J. Ash, M. Girish, E. Gray, B. Jamoussi, G. Wright         ||        gash@att.com, eric.gray@sandburst.com, gwright@nortelnetworks.com, muckai@atoga.com, Jamoussi@nortelnetworks.com 
  RFC3214          ||       J. Ash, Y. Lee, P. Ashwood-Smith, B. Jamoussi, D. Fedyk, D. Skalecki, L. Li         ||        gash@att.com, jamoussi@NortelNetworks.com, petera@NortelNetworks.com, dareks@nortelnetworks.com, ylee@ceterusnetworks.com, lili@ss8networks.com, dwfedyk@nortelnetworks.com 
  RFC3215          ||       C. Boscher, P. Cheval, L. Wu, E. Gray         ||        christophe.boscher@alcatel.fr, pierrick.cheval@space.alcatel.fr, liwwu@cisco.com, eric.gray@sandburst.com 
  RFC3216          ||       C. Elliott, D. Harrington, J. Jason, J. Schoenwaelder, F. Strauss, W. Weiss         ||        chelliot@cisco.com, dbh@enterasys.com, jamie.jason@intel.com, schoenw@ibr.cs.tu-bs.de, strauss@ibr.cs.tu-bs.de, wweiss@ellacoya.com 
  RFC3217          ||       R. Housley         ||        rhousley@rsasecurity.com 
  RFC3218          ||       E. Rescorla         ||        ekr@rtfm.com 
  RFC3219          ||       J. Rosenberg, H. Salama, M. Squire         ||        jdrosen@dynamicsoft.com, hsalama@cisco.com, mattsquire@acm.org 
  RFC3220          ||      C. Perkins, Ed.         ||       charliep@iprg.nokia.com
  RFC3221          ||       G. Huston         ||         
  RFC3222          ||       G. Trotter         ||        Guy_Trotter@agilent.com 
  RFC3223          ||               ||         
  RFC3224          ||       E. Guttman         ||        erik.guttman@sun.com 
  RFC3225          ||       D. Conrad         ||        david.conrad@nominum.com 
  RFC3226          ||       O. Gudmundsson         ||        ogud@ogud.com 
  RFC3227          ||       D. Brezinski, T. Killalea         ||        dbrezinski@In-Q-Tel.org, tomk@neart.org 
  RFC3228          ||       B. Fenner         ||        fenner@research.att.com 
  RFC3229          ||       J. Mogul, B. Krishnamurthy, F. Douglis, A. Feldmann, Y. Goland, A. van Hoff, D. Hellerstein         ||         
  RFC3230          ||       J. Mogul, A. Van Hoff         ||        JeffMogul@acm.org, avh@marimba.com 
  RFC3231          ||       D. Levi, J. Schoenwaelder         ||         
  RFC3232          ||       J. Reynolds, Ed.         ||        rfc-editor@rfc-editor.org 
  RFC3233          ||       P. Hoffman, S. Bradner         ||         
  RFC3234          ||       B. Carpenter, S. Brim         ||        brian@hursley.ibm.com, sbrim@cisco.com 
  RFC3235          ||       D. Senie         ||        dts@senie.com 
  RFC3236          ||       M. Baker, P. Stark         ||        mbaker@planetfred.com, distobj@acm.org, Peter.Stark@ecs.ericsson.com 
  RFC3237          ||       M. Tuexen, Q. Xie, R. Stewart, M. Shore, L. Ong, J. Loughney, M. Stillman         ||       Michael.Tuexen@icn.siemens.de, qxie1@email.mot.com, randall@lakerest.net, mshore@cisco.com, lyong@ciena.com, john.loughney@nokia.com, maureen.stillman@nokia.com
  RFC3238          ||       S. Floyd, L. Daigle         ||        iab@iab.org 
  RFC3239          ||      C. Kugler, H. Lewis, T. Hastings         ||       kugler@us.ibm.com, tom.hastings@alum.mit.edu, harryl@us.ibm.com
  RFC3240          ||       D. Clunie, E. Cordonnier         ||        dclunie@dclunie.com, emmanuel.cordonnier@etiam.com 
  RFC3241          ||      C. Bormann         ||       cabo@tzi.org
  RFC3242          ||       L-E. Jonsson, G. Pelletier         ||        lars-erik.jonsson@ericsson.com, ghyslain.pelletier@epl.ericsson.se 
  RFC3243          ||       L-E. Jonsson         ||        lars-erik.jonsson@ericsson.com 
  RFC3244          ||       M. Swift, J. Trostle, J. Brezak         ||        mikesw@cs.washington.edu, john3725@world.std.com, jbrezak@microsoft.com 
  RFC3245          ||      J. Klensin, Ed., IAB         ||       iab@iab.org, sob@harvard.edu, paf@cisco.com
  RFC3246          ||      B. Davie, A. Charny, J.C.R. Bennet, K. Benson, J.Y. Le Boudec, W. Courtney, S. Davari, V. Firoiu, D. Stiliadis         ||       bsd@cisco.com, acharny@cisco.com, jcrb@motorola.com, Kent.Benson@tellabs.com, jean-yves.leboudec@epfl.ch, bill.courtney@trw.com, shahram_davari@pmc-sierra.com, vfiroiu@nortelnetworks.com, stiliadi@bell-labs.com
  RFC3247          ||      A. Charny, J. Bennet, K. Benson, J. Boudec, A. Chiu, W. Courtney, S. Davari, V. Firoiu, C. Kalmanek, K. Ramakrishnan         ||       acharny@cisco.com, jcrb@motorola.com, Kent.Benson@tellabs.com, jean-yves.leboudec@epfl.ch, angela.chiu@celion.com, bill.courtney@trw.com, shahram_davari@pmc-sierra.com, vfiroiu@nortelnetworks.com, crk@research.att.com, kk@teraoptic.com
  RFC3248          ||      G. Armitage, B. Carpenter, A. Casati, J. Crowcroft, J. Halpern, B. Kumar, J. Schnizlein         ||       
  RFC3249          ||       V. Cancio, M. Moldovan, H. Tamura, D. Wing         ||        vcancio@pacbell.net, mmoldovan@g3nova.com, tamura@toda.ricoh.co.jp, dwing-ietf@fuggles.com 
  RFC3250          ||      L. McIntyre, G. Parsons, J. Rafferty         ||       lmcintyre@pahv.xerox.com, gparsons@nortelnetworks.com, jraff@brooktrout.com
  RFC3251          ||       B. Rajagopalan         ||        braja@tellium.com 
  RFC3252          ||       H. Kennedy         ||        kennedyh@engin.umich.edu 
  RFC3253          ||      G. Clemm, J. Amsden, T. Ellison, C. Kaler, J. Whitehead         ||       geoffrey.clemm@rational.com, jamsden@us.ibm.com, tim_ellison@uk.ibm.com, ckaler@microsoft.com, ejw@cse.ucsc.edu
  RFC3254          ||       H. Alvestrand         ||        Harald@alvestrand.no 
  RFC3255          ||       N. Jones, C. Murton         ||        nrjones@agere.com, murton@nortelnetworks.com 
  RFC3256          ||       D. Jones, R. Woundy         ||        doug@yas.com, rwoundy@broadband.att.com 
  RFC3257          ||       L. Coene         ||         
  RFC3258          ||       T. Hardie         ||        Ted.Hardie@nominum.com 
  RFC3259          ||       J. Ott, C. Perkins, D. Kutscher         ||        jo@tzi.uni-bremen.de, csp@isi.edu, dku@tzi.uni-bremen.de 
  RFC3260          ||       D. Grossman         ||        dan@dma.isg.mot.com 
  RFC3261          ||      J. Rosenberg, H. Schulzrinne, G. Camarillo, A. Johnston, J. Peterson, R. Sparks, M. Handley, E. Schooler         ||       jdrosen@dynamicsoft.com, schulzrinne@cs.columbia.edu, Gonzalo.Camarillo@ericsson.com, alan.johnston@wcom.com, jon.peterson@neustar.com, rsparks@dynamicsoft.com, mjh@icir.org, schooler@research.att.com
  RFC3262          ||      J. Rosenberg, H. Schulzrinne         ||       jdrosen@dynamicsoft.com, schulzrinne@cs.columbia.edu
  RFC3263          ||      J. Rosenberg, H. Schulzrinne         ||       jdrosen@dynamicsoft.com, schulzrinne@cs.columbia.edu
  RFC3264          ||      J. Rosenberg, H. Schulzrinne         ||       jdrosen@dynamicsoft.com, schulzrinne@cs.columbia.edu
  RFC3265          ||      A. B. Roach         ||       adam@dynamicsoft.com
  RFC3266          ||      S. Olson, G. Camarillo, A. B. Roach         ||       seanol@microsoft.com, Gonzalo.Camarillo@ericsson.com, adam@dynamicsoft.com
  RFC3267          ||      J. Sjoberg, M. Westerlund, A. Lakaniemi, Q. Xie         ||       Johan.Sjoberg@ericsson.com, Magnus.Westerlund@ericsson.com, ari.lakaniemi@nokia.com, qxie1@email.mot.com
  RFC3268          ||      P. Chown         ||       pc@skygate.co.uk
  RFC3269          ||       R. Kermode, L. Vicisano         ||        Roger.Kermode@motorola.com, lorenzo@cisco.com 
  RFC3270          ||      F. Le Faucheur, L. Wu, B. Davie, S. Davari, P. Vaananen, R. Krishnan, P. Cheval, J. Heinanen         ||       flefauch@cisco.com, liwwu@cisco.com, bsd@cisco.com, davari@ieee.org, pasi.vaananen@nokia.com, ram@axiowave.com, pierrick.cheval@space.alcatel.fr, jh@song.fi
  RFC3271          ||      V. Cerf         ||       vinton.g.cerf@wcom.com
  RFC3272          ||      D. Awduche, A. Chiu, A. Elwalid, I. Widjaja, X. Xiao         ||       awduche@movaz.com, angela.chiu@celion.com, anwar@lucent.com, iwidjaja@research.bell-labs.com, xipeng@redback.com
  RFC3273          ||      S. Waldbusser         ||       waldbusser@nextbeacon.com
  RFC3274          ||      P. Gutmann         ||       pgut001@cs.auckland.ac.nz
  RFC3275          ||      D. Eastlake 3rd, J. Reagle, D. Solo         ||       Donald.Eastlake@motorola.com, reagle@w3.org, dsolo@alum.mit.edu
  RFC3276          ||      B. Ray, R. Abbi         ||       rray@pesa.com, Rajesh.Abbi@alcatel.com
  RFC3277          ||       D. McPherson         ||        danny@tcb.net 
  RFC3278          ||      S. Blake-Wilson, D. Brown, P. Lambert         ||       sblakewi@certicom.com, dbrown@certicom.com, plambert@sprintmail.com
  RFC3279          ||      L. Bassham, W. Polk, R. Housley         ||       tim.polk@nist.gov, rhousley@rsasecurity.com, lbassham@nist.gov
  RFC3280          ||      R. Housley, W. Polk, W. Ford, D. Solo         ||       rhousley@rsasecurity.com, wford@verisign.com, wpolk@nist.gov, dsolo@alum.mit.edu
  RFC3281          ||      S. Farrell, R. Housley         ||       stephen.farrell@baltimore.ie, rhousley@rsasecurity.com
  RFC3282          ||      H. Alvestrand         ||       Harald@Alvestrand.no
  RFC3283          ||      B. Mahoney, G. Babics, A. Taler         ||       bobmah@mit.edu, georgeb@steltor.com, alex@0--0.org
  RFC3284          ||      D. Korn, J. MacDonald, J. Mogul, K. Vo         ||       kpv@research.att.com, dgk@research.att.com, JeffMogul@acm.org, jmacd@cs.berkeley.edu
  RFC3285          ||      M. Gahrns, T. Hain         ||       mikega@microsoft.com, ahain@cisco.com
  RFC3286          ||      L. Ong, J. Yoakum         ||       lyong@ciena.com, yoakum@nortelnetworks.com
  RFC3287          ||      A. Bierman         ||       andy@yumaworks.com
  RFC3288          ||      E. O'Tuathail, M. Rose         ||       eamon.otuathail@clipcode.com, mrose17@gmail.com
  RFC3289          ||      F. Baker, K. Chan, A. Smith         ||       fred@cisco.com, khchan@nortelnetworks.com, ah_smith@acm.org
  RFC3290          ||      Y. Bernet, S. Blake, D. Grossman, A. Smith         ||       ybernet@msn.com, steven.blake@ericsson.com, dan@dma.isg.mot.com, ah_smith@acm.org
  RFC3291          ||      M. Daniele, B. Haberman, S. Routhier, J. Schoenwaelder         ||       md@world.std.com, bkhabs@nc.rr.com, sar@epilogue.com, schoenw@ibr.cs.tu-bs.de
  RFC3292          ||      A. Doria, F. Hellstrand, K. Sundell, T. Worster         ||       avri@acm.org, fiffi@nortelnetworks.com, ksundell@nortelnetworks.com, fsb@thefsb.org
  RFC3293          ||      T. Worster, A. Doria, J. Buerkle         ||       fsb@thefsb.org, avri@acm.com, Joachim.Buerkle@nortelnetworks.com
  RFC3294          ||      A. Doria, K. Sundell         ||       avri@acm.org, sundell@nortelnetworks.com
  RFC3295          ||      H. Sjostrand, J. Buerkle, B. Srinivasan         ||       hans@ipunplugged.com, joachim.buerkle@nortelnetworks.com, balaji@cplane.com
  RFC3296          ||      K. Zeilenga         ||       Kurt@OpenLDAP.org
  RFC3297          ||      G. Klyne, R. Iwazaki, D. Crocker         ||       GK@ACM.ORG, iwa@rdl.toshibatec.co.jp, dcrocker@brandenburg.com
  RFC3298          ||       I. Faynberg, J. Gato, H. Lu, L. Slutsman         ||        lslutsman@att.com, faynberg@lucent.com, jgato@airtel.es, huilanlu@lucent.com 
  RFC3299          ||       S. Ginoza         ||        ginoza@isi.edu 
  RFC3300          ||      J. Reynolds, R. Braden, S. Ginoza, A. De La Cruz         ||       
  RFC3301          ||      Y. T'Joens, P. Crivellari, B. Sales         ||       paolo.crivellari@belgacom.be
  RFC3302          ||      G. Parsons, J. Rafferty         ||       gparsons@nortelnetworks.com, jraff@brooktrout.com
  RFC3303          ||       P. Srisuresh, J. Kuthan, J. Rosenberg, A. Molitor, A. Rayhan         ||        srisuresh@yahoo.com, kuthan@fokus.fhg.de, jdrosen@dynamicsoft.com, amolitor@visi.com, rayhan@ee.ryerson.ca 
  RFC3304          ||       R. P. Swale, P. A. Mart, P. Sijben, S. Brim, M. Shore         ||        richard.swale@bt.com, paul.sijben@picopoint.com, philip.mart@marconi.com, sbrim@cisco.com, mshore@cisco.com 
  RFC3305          ||      M. Mealling, Ed., R. Denenberg, Ed.         ||       michael@verisignlabs.com, rden@loc.gov
  RFC3306          ||      B. Haberman, D. Thaler         ||       bkhabs@nc.rr.com, dthaler@microsoft.com
  RFC3307          ||      B. Haberman         ||       bkhabs@nc.rr.com
  RFC3308          ||      P. Calhoun, W. Luo, D. McPherson, K. Peirce         ||       pcalhoun@bstormnetworks.com, luo@cisco.com, danny@tcb.net, Ken@malibunetworks.com
  RFC3309          ||      J. Stone, R. Stewart, D. Otis         ||       jonathan@dsg.stanford.edu, randall@lakerest.net, dotis@sanlight.net
  RFC3310          ||      A. Niemi, J. Arkko, V. Torvinen         ||       aki.niemi@nokia.com, jari.arkko@ericsson.com, vesa.torvinen@ericsson.fi
  RFC3311          ||      J. Rosenberg         ||       jdrosen@dynamicsoft.com
  RFC3312          ||      G. Camarillo, Ed., W. Marshall, Ed., J. Rosenberg         ||       Gonzalo.Camarillo@ericsson.com, wtm@research.att.com, jdrosen@dynamicsoft.com
  RFC3313          ||      W. Marshall, Ed.         ||       
  RFC3314          ||      M. Wasserman, Ed.         ||       
  RFC3315          ||      R. Droms, Ed., J. Bound, B. Volz, T. Lemon, C. Perkins, M. Carney         ||       Jim.Bound@hp.com, volz@metrocast.net, Ted.Lemon@nominum.com, charles.perkins@nokia.com, michael.carney@sun.com
  RFC3316          ||      J. Arkko, G. Kuijpers, H. Soliman, J. Loughney, J. Wiljakka         ||       jari.arkko@ericsson.com, gerben.a.kuijpers@ted.ericsson.se, john.loughney@nokia.com, hesham.soliman@era.ericsson.se, juha.wiljakka@nokia.com
  RFC3317          ||      K. Chan, R. Sahita, S. Hahn, K. McCloghrie         ||       khchan@nortelnetworks.com, ravi.sahita@intel.com, scott.hahn@intel.com, kzm@cisco.com
  RFC3318          ||      R. Sahita, Ed., S. Hahn, K. Chan, K. McCloghrie         ||       ravi.sahita@intel.com, scott.hahn@intel.com, khchan@nortelnetworks.com, kzm@cisco.com
  RFC3319          ||       H. Schulzrinne, B. Volz         ||        schulzrinne@cs.columbia.edu, volz@metrocast.net 
  RFC3320          ||      R. Price, C. Bormann, J. Christoffersson, H. Hannu, Z. Liu, J. Rosenberg         ||       richard.price@roke.co.uk, cabo@tzi.org, jan.christoffersson@epl.ericsson.se, hans.hannu@epl.ericsson.se, zhigang.c.liu@nokia.com, jdrosen@dynamicsoft.com
  RFC3321          ||      H. Hannu, J. Christoffersson, S. Forsgren, K.-C. Leung, Z. Liu, R. Price         ||       hans.hannu@epl.ericsson.se, jan.christoffersson@epl.ericsson.se, StefanForsgren@alvishagglunds.se, kcleung@cs.ttu.edu, zhigang.c.liu@nokia.com, richard.price@roke.co.uk
  RFC3322          ||      H. Hannu         ||       hans.hannu@epl.ericsson.se
  RFC3323          ||      J. Peterson         ||       jon.peterson@neustar.biz
  RFC3324          ||      M. Watson         ||       mwatson@nortelnetworks.com
  RFC3325          ||      C. Jennings, J. Peterson, M. Watson         ||       fluffy@cisco.com, Jon.Peterson@NeuStar.biz, mwatson@nortelnetworks.com
  RFC3326          ||      H. Schulzrinne, D. Oran, G. Camarillo         ||       schulzrinne@cs.columbia.edu, oran@cisco.com, Gonzalo.Camarillo@ericsson.com
  RFC3327          ||      D. Willis, B. Hoeneisen         ||       dean.willis@softarmor.com, hoeneisen@switch.ch
  RFC3328          ||               ||         
  RFC3329          ||      J. Arkko, V. Torvinen, G. Camarillo, A. Niemi, T. Haukka         ||       jari.arkko@ericsson.com, vesa.torvinen@ericsson.fi, Gonzalo.Camarillo@ericsson.com, aki.niemi@nokia.com, tao.haukka@nokia.com
  RFC3330          ||      IANA         ||       iana@iana.org
  RFC3331          ||      K. Morneault, R. Dantu, G. Sidebottom, B. Bidulock, J. Heitz         ||       kmorneau@cisco.com, rdantu@netrake.com, greg@signatustechnologies.com, bidulock@openss7.org, jheitz@lucent.com
  RFC3332          ||      G. Sidebottom, Ed., K. Morneault, Ed., J. Pastor-Balbas, Ed.         ||       
  RFC3334          ||       T. Zseby, S. Zander, C. Carle         ||        zseby@fokus.fhg.de, zander@fokus.fhg.de, carle@fokus.fhg.de 
  RFC3335          ||      T. Harding, R. Drummond, C. Shih         ||       tharding@cyclonecommerce.com, chuck.shih@gartner.com, rik@drummondgroup.com
  RFC3336          ||      B. Thompson, T. Koren, B. Buffam         ||       brucet@cisco.com, tmima@cisco.com, bruce@seawaynetworks.com
  RFC3337          ||      B. Thompson, T. Koren, B. Buffam         ||       brucet@cisco.com, bruce@seawaynetworks.com, tmima@cisco.com
  RFC3338          ||      S. Lee, M-K. Shin, Y-J. Kim, E. Nordmark, A. Durand         ||       syl@pec.etri.re.kr, mkshin@pec.etri.re.kr, yjkim@pec.etri.re.kr, Alain.Durand@sun.com, erik.nordmark@sun.com
  RFC3339          ||      G. Klyne, C. Newman         ||       chris.newman@sun.com, GK@ACM.ORG
  RFC3340          ||      M. Rose, G. Klyne, D. Crocker         ||       mrose17@gmail.com, Graham.Klyne@MIMEsweeper.com, dcrocker@brandenburg.com
  RFC3341          ||      M. Rose, G. Klyne, D. Crocker         ||       mrose17@gmail.com, Graham.Klyne@MIMEsweeper.com, dcrocker@brandenburg.com
  RFC3342          ||      E. Dixon, H. Franklin, J. Kint, G. Klyne, D. New, S. Pead, M. Rose, M. Schwartz         ||       Graham.Klyne@MIMEsweeper.com, mrose17@gmail.com, schwartz@CodeOnTheRoad.com, edixon@myrealbox.com, huston@franklin.ro, d20@icosahedron.org, dnew@san.rr.com, spead@fiber.net
  RFC3343          ||      M. Rose, G. Klyne, D. Crocker         ||       mrose17@gmail.com, gk@ninebynine.org, dcrocker@brandenburg.com
  RFC3344          ||      C. Perkins, Ed.         ||       Basavaraj.Patil@nokia.com, PRoberts@MEGISTO.com, charliep@iprg.nokia.com
  RFC3345          ||      D. McPherson, V. Gill, D. Walton, A. Retana         ||       danny@tcb.net, vijay@umbc.edu, dwalton@cisco.com, aretana@cisco.com
  RFC3346          ||      J. Boyle, V. Gill, A. Hannan, D. Cooper, D. Awduche, B. Christian, W.S. Lai         ||       jboyle@pdnets.com, vijay@umbc.edu, alan@routingloop.com, dcooper@gblx.net, awduche@movaz.com, blaine@uu.net, wlai@att.com
  RFC3347          ||      M. Krueger, R. Haagens         ||       marjorie_krueger@hp.com, Randy_Haagens@hp.com, csapuntz@stanford.edu, mbakke@cisco.com
  RFC3348          ||      M. Gahrns, R. Cheng         ||       mikega@microsoft.com, raych@microsoft.com
  RFC3349          ||      M. Rose         ||       mrose17@gmail.com
  RFC3351          ||      N. Charlton, M. Gasson, G. Gybels, M. Spanner, A. van Wijk         ||       nathan@millpark.com, michael.gasson@korusolutions.com, Guido.Gybels@rnid.org.uk, mike.spanner@rnid.org.uk, Arnoud.van.Wijk@eln.ericsson.se
  RFC3352          ||       K. Zeilenga         ||        Kurt@OpenLDAP.org 
  RFC3353          ||      D. Ooms, B. Sales, W. Livens, A. Acharya, F. Griffoul, F. Ansari         ||       Dirk.Ooms@alcatel.be, Bernard.Sales@alcatel.be, WLivens@colt-telecom.be, arup@us.ibm.com, griffoul@ulticom.com, furquan@dnrc.bell-labs.com
  RFC3354          ||      D. Eastlake 3rd         ||       Donald.Eastlake@motorola.com
  RFC3355          ||      A. Singh, R. Turner, R. Tio, S. Nanji         ||       rturner@eng.paradyne.com, tor@redback.com, asingh1@motorola.com, suhail@redback.com
  RFC3356          ||      G. Fishman, S. Bradner         ||       
  RFC3357          ||      R. Koodli, R. Ravikanth         ||       rajeev.koodli@nokia.com, rravikanth@axiowave.com
  RFC3358          ||      T. Przygienda         ||       prz@xebeo.com
  RFC3359          ||      T. Przygienda         ||       
  RFC3360          ||       S. Floyd         ||        floyd@icir.org 
  RFC3361          ||      H. Schulzrinne         ||       schulzrinne@cs.columbia.edu
  RFC3362          ||       G. Parsons         ||        gparsons@nortelnetworks.com 
  RFC3363          ||      R. Bush, A. Durand, B. Fink, O. Gudmundsson, T. Hain         ||       
  RFC3364          ||      R. Austein         ||       sra@hactrn.net
  RFC3365          ||       J. Schiller         ||        jis@mit.edu 
  RFC3366          ||      G. Fairhurst, L. Wood         ||       gorry@erg.abdn.ac.uk, lwood@cisco.com
  RFC3367          ||       N. Popp, M. Mealling, M. Moseley         ||        npopp@verisign.com, michael@verisignlabs.com, marshall@netword.com 
  RFC3368          ||       M. Mealling         ||        michael@verisignlabs.com 
  RFC3369          ||      R. Housley         ||       rhousley@rsasecurity.com
  RFC3370          ||      R. Housley         ||       rhousley@rsasecurity.com
  RFC3371          ||      E. Caves, P. Calhoun, R. Wheeler         ||       evan@occamnetworks.com, pcalhoun@bstormnetworks.com
  RFC3372          ||      A. Vemuri, J. Peterson         ||       Aparna.Vemuri@Qwest.com, jon.peterson@neustar.biz
  RFC3373          ||      D. Katz, R. Saluja         ||       dkatz@juniper.net, rajesh.saluja@tenetindia.com
  RFC3374          ||      J. Kempf, Ed.         ||       henrik@levkowetz.com, pcalhoun@bstormnetworks.com, kempf@docomolabs-usa.com, gkenward@nortelnetworks.com, hmsyed@nortelnetworks.com, jmanner@cs.helsinki.fi, madjid.nakhjiri@motorola.com, govind.krishnamurthi@nokia.com, rajeev.koodli@nokia.com, kulwinder.atwal@zucotto.com, mat@cisco.com, mat.horan@comdev.cc, phil_neumiller@3com.com
  RFC3375          ||      S. Hollenbeck         ||       
  RFC3376          ||      B. Cain, S. Deering, I. Kouvelas, B. Fenner, A. Thyagarajan         ||       deering@cisco.com, fenner@research.att.com, kouvelas@cisco.com
  RFC3377          ||      J. Hodges, R. Morgan         ||       Jeff.Hodges@sun.com, rlmorgan@washington.edu
  RFC3378          ||       R. Housley, S. Hollenbeck         ||        rhousley@rsasecurity.com, shollenbeck@verisign.com 
  RFC3379          ||      D. Pinkas, R. Housley         ||       Denis.Pinkas@bull.net, rhousley@rsasecurity.com
  RFC3380          ||      T. Hastings, R. Herriot, C. Kugler, H. Lewis         ||       kugler@us.ibm.com, tom.hastings@alum.mit.edu, bob@Herriot.com, harryl@us.ibm.com
  RFC3381          ||      T. Hastings, H. Lewis, R. Bergman         ||       tom.hastings@alum.mit.edu, harryl@us.ibm.com, rbergma@hitachi-hkis.com
  RFC3382          ||      R. deBry, T. Hastings, R. Herriot, K. Ocke, P. Zehler         ||       debryro@uvsc.edu, tom.hastings@alum.mit.edu, bob@herriot.com, KOcke@crt.xerox.com, Peter.Zehler@xerox.com
  RFC3383          ||      K. Zeilenga         ||       Kurt@OpenLDAP.org
  RFC3384          ||      E. Stokes, R. Weiser, R. Moats, R. Huber         ||       rweiser@trustdst.com, stokese@us.ibm.com, rmoats@lemurnetworks.net, rvh@att.com
  RFC3385          ||       D. Sheinwald, J. Satran, P. Thaler, V. Cavanna         ||        julian_satran@il.ibm.com, Dafna_Sheinwald@il.ibm.com, pat_thaler@agilent.com, vince_cavanna@agilent.com 
  RFC3386          ||      W. Lai, Ed., D. McDysan, Ed.         ||       
  RFC3387          ||       M. Eder, H. Chaskar, S. Nag         ||        Michael.eder@nokia.com, thinker@monmouth.com, hemant.chaskar@nokia.com 
  RFC3388          ||      G. Camarillo, G. Eriksson, J. Holler, H. Schulzrinne         ||       Gonzalo.Camarillo@ericsson.com, Jan.Holler@era.ericsson.se, Goran.AP.Eriksson@era.ericsson.se, schulzrinne@cs.columbia.edu
  RFC3389          ||      R. Zopf         ||       zopf@lucent.com
  RFC3390          ||      M. Allman, S. Floyd, C. Partridge         ||       mallman@bbn.com, floyd@icir.org, craig@bbn.com
  RFC3391          ||       R. Herriot         ||        bob@herriot.com 
  RFC3392          ||      R. Chandra, J. Scudder         ||       rchandra@redback.com, jgs@cisco.com
  RFC3393          ||      C. Demichelis, P. Chimento         ||       carlo.demichelis@tilab.com, chimento@torrentnet.com
  RFC3394          ||      J. Schaad, R. Housley         ||       jimsch@exmsft.com, rhousley@rsasecurity.com
  RFC3395          ||      A. Bierman, C. Bucci, R. Dietz, A. Warth         ||       andy@yumaworks.com, cbucci@cisco.com, rdietz@hifn.com, dahoss@earthlink.net
  RFC3396          ||      T. Lemon, S. Cheshire         ||       mellon@nominum.com, rfc@stuartcheshire.org
  RFC3397          ||      B. Aboba, S. Cheshire         ||       bernarda@microsoft.com, rfc@stuartcheshire.org
  RFC3398          ||      G. Camarillo, A. B. Roach, J. Peterson, L. Ong         ||       Gonzalo.Camarillo@Ericsson.com, adam@dynamicsoft.com, jon.peterson@neustar.biz, lyOng@ciena.com
  RFC3400          ||               ||         
  RFC3401          ||      M. Mealling         ||       michael@neonym.net
  RFC3402          ||      M. Mealling         ||       michael@neonym.net
  RFC3403          ||      M. Mealling         ||       michael@neonym.net
  RFC3404          ||      M. Mealling         ||       michael@neonym.net
  RFC3405          ||      M. Mealling         ||       michael@neonym.net
  RFC3406          ||      L. Daigle, D. van Gulik, R. Iannella, P. Faltstrom         ||       leslie@thinkingcat.com, renato@iprsystems.com, paf@cisco.com
  RFC3407          ||      F. Andreasen         ||       fandreas@cisco.com
  RFC3408          ||      Z. Liu, K. Le         ||       khiem.le@nokia.com
  RFC3409          ||       K. Svanbro         ||        krister.svanbro@ericsson.com 
  RFC3410          ||       J. Case, R. Mundy, D. Partain, B. Stewart         ||         
  RFC3411          ||      D. Harrington, R. Presuhn, B. Wijnen         ||       
  RFC3412          ||      J. Case, D. Harrington, R. Presuhn, B. Wijnen         ||       
  RFC3413          ||       D. Levi, P. Meyer, B. Stewart         ||         
  RFC3414          ||      U. Blumenthal, B. Wijnen         ||       
  RFC3415          ||       B. Wijnen, R. Presuhn, K. McCloghrie         ||         
  RFC3416          ||       R. Presuhn, Ed.         ||         
  RFC3417          ||      R. Presuhn, Ed.         ||       
  RFC3418          ||       R. Presuhn, Ed.         ||         
  RFC3419          ||       M. Daniele, J. Schoenwaelder         ||        md@world.std.com, schoenw@ibr.cs.tu-bs.de 
  RFC3420          ||      R. Sparks         ||       rsparks@dynamicsoft.com
  RFC3421          ||      W. Zhao, H. Schulzrinne, E. Guttman, C. Bisdikian, W. Jerome         ||       zwb@cs.columbia.edu, hgs@cs.columbia.edu, Erik.Guttman@sun.com, bisdik@us.ibm.com, wfj@us.ibm.com
  RFC3422          ||      O. Okamoto, M. Maruyama, T. Sajima         ||       okamoto.osamu@lab.ntt.co.jp, mitsuru@core.ecl.net, tjs@sun.com
  RFC3423          ||       K. Zhang, E. Elkin         ||        kevinzhang@ieee.org, eitan@xacct.com 
  RFC3424          ||      L. Daigle, Ed., IAB         ||       iab@iab.org
  RFC3425          ||      D. Lawrence         ||       tale@nominum.com
  RFC3426          ||      S. Floyd         ||       iab@iab.org
  RFC3427          ||      A. Mankin, S. Bradner, R. Mahy, D. Willis, J. Ott, B. Rosen         ||       mankin@psg.com, sob@harvard.edu, rohan@cisco.com, dean.willis@softarmor.com, brian.rosen@marconi.com, jo@ipdialog.com
  RFC3428          ||       B. Campbell, Ed., J. Rosenberg, H. Schulzrinne, C. Huitema, D. Gurle         ||        bcampbell@dynamicsoft.com, jdrosen@dynamicsoft.com, schulzrinne@cs.columbia.edu, huitema@microsoft.com, dgurle@microsoft.com 
  RFC3429          ||      H. Ohta         ||       ohta.hiroshi@lab.ntt.co.jp
  RFC3430          ||      J. Schoenwaelder         ||       schoenw@ibr.cs.tu-bs.de
  RFC3431          ||      W. Segmuller         ||       whs@watson.ibm.com
  RFC3432          ||      V. Raisanen, G. Grotefeld, A. Morton         ||       Vilho.Raisanen@nokia.com, g.grotefeld@motorola.com, acmorton@att.com
  RFC3433          ||      A. Bierman, D. Romascanu, K.C. Norseth         ||       andy@yumaworks.com, dromasca@gmail.com , kenyon.c.norseth@L-3com.com
  RFC3434          ||      A. Bierman, K. McCloghrie         ||       andy@yumaworks.com, kzm@cisco.com
  RFC3435          ||      F. Andreasen, B. Foster         ||       fandreas@cisco.com, bfoster@cisco.com
  RFC3436          ||      A. Jungmaier, E. Rescorla, M. Tuexen         ||       ajung@exp-math.uni-essen.de, ekr@rtfm.com, Michael.Tuexen@siemens.com
  RFC3437          ||      W. Palter, W. Townsley         ||       mark@townsley.net, palter.ietf@zev.net
  RFC3438          ||      W. Townsley         ||       mark@townsley.net
  RFC3439          ||      R. Bush, D. Meyer         ||       randy@psg.com, dmm@maoz.com
  RFC3440          ||      F. Ly, G. Bathrick         ||       faye@pedestalnetworks.com, greg.bathrick@nokia.com
  RFC3441          ||      R. Kumar         ||       rkumar@cisco.com
  RFC3442          ||      T. Lemon, S. Cheshire, B. Volz         ||       Ted.Lemon@nominum.com, rfc@stuartcheshire.org, bernie.volz@ericsson.com
  RFC3443          ||      P. Agarwal, B. Akyol         ||       puneet@acm.org, bora@cisco.com
  RFC3444          ||      A. Pras, J. Schoenwaelder         ||       pras@ctit.utwente.nl, schoenw@informatik.uni-osnabrueck.de
  RFC3445          ||      D. Massey, S. Rose         ||       masseyd@isi.edu, scott.rose@nist.gov
  RFC3446          ||      D. Kim, D. Meyer, H. Kilmer, D. Farinacci         ||       dorian@blackrose.org, hank@rem.com, dino@procket.com, dmm@maoz.com
  RFC3447          ||      J. Jonsson, B. Kaliski         ||       jonsson@mathematik.uni-marburg.de, bkaliski@rsasecurity.com
  RFC3448          ||      M. Handley, S. Floyd, J. Padhye, J. Widmer         ||       mjh@icir.org, floyd@icir.org, padhye@microsoft.com, widmer@informatik.uni-mannheim.de
  RFC3449          ||      H. Balakrishnan, V. Padmanabhan, G. Fairhurst, M. Sooriyabandara         ||       hari@lcs.mit.edu, padmanab@microsoft.com, gorry@erg.abdn.ac.uk, mahesh@erg.abdn.ac.uk
  RFC3450          ||      M. Luby, J. Gemmell, L. Vicisano, L. Rizzo, J. Crowcroft         ||       luby@digitalfountain.com, jgemmell@microsoft.com, lorenzo@cisco.com, luigi@iet.unipi.it, Jon.Crowcroft@cl.cam.ac.uk
  RFC3451          ||      M. Luby, J. Gemmell, L. Vicisano, L. Rizzo, M. Handley, J. Crowcroft         ||       luby@digitalfountain.com, jgemmell@microsoft.com, lorenzo@cisco.com, luigi@iet.unipi.it, mjh@icir.org, Jon.Crowcroft@cl.cam.ac.uk
  RFC3452          ||      M. Luby, L. Vicisano, J. Gemmell, L. Rizzo, M. Handley, J. Crowcroft         ||       luby@digitalfountain.com, lorenzo@cisco.com, jgemmell@microsoft.com, luigi@iet.unipi.it, mjh@icir.org, Jon.Crowcroft@cl.cam.ac.uk
  RFC3453          ||      M. Luby, L. Vicisano, J. Gemmell, L. Rizzo, M. Handley, J. Crowcroft         ||       luby@digitalfountain.com, lorenzo@cisco.com, jgemmell@microsoft.com, luigi@iet.unipi.it, mjh@icir.org, Jon.Crowcroft@cl.cam.ac.uk
  RFC3454          ||      P. Hoffman, M. Blanchet         ||       paul.hoffman@imc.org, Marc.Blanchet@viagenie.qc.ca
  RFC3455          ||      M. Garcia-Martin, E. Henrikson, D. Mills         ||       miguel.a.garcia@ericsson.com, ehenrikson@lucent.com, duncan.mills@vf.vodafone.co.uk
  RFC3456          ||      B. Patel, B. Aboba, S. Kelly, V. Gupta         ||       baiju.v.patel@intel.com, bernarda@microsoft.com, scott@hyperthought.com, vipul.gupta@sun.com
  RFC3457          ||      S. Kelly, S. Ramamoorthi         ||       
  RFC3458          ||      E. Burger, E. Candell, C. Eliot, G. Klyne         ||       e.burger@ieee.org, emily.candell@comverse.com, GK-IETF@ninebynine.org, charle@Microsoft.com
  RFC3459          ||      E. Burger         ||       e.burger@ieee.org
  RFC3460          ||      B. Moore, Ed.         ||       remoore@us.ibm.com
  RFC3461          ||      K. Moore         ||       moore@cs.utk.edu
  RFC3462          ||      G. Vaudreuil         ||       GregV@ieee.org
  RFC3463          ||      G. Vaudreuil         ||       GregV@ieee.org
  RFC3464          ||      K. Moore, G. Vaudreuil         ||       moore@cs.utk.edu, GregV@ieee.org
  RFC3465          ||      M. Allman         ||       mallman@bbn.com
  RFC3466          ||      M. Day, B. Cain, G. Tomlinson, P. Rzewski         ||       mday@alum.mit.edu, bcain@storigen.com, gary@tomlinsongroup.net, philrz@yahoo.com
  RFC3467          ||      J. Klensin         ||       
  RFC3468          ||      L. Andersson, G. Swallow         ||       loa@pi.se, swallow@cisco.com
  RFC3469          ||      V. Sharma, Ed., F. Hellstrand, Ed.         ||       
  RFC3470          ||      S. Hollenbeck, M. Rose, L. Masinter         ||       shollenbeck@verisign.com, mrose17@gmail.com,  LMM@acm.org
  RFC3471          ||      L. Berger, Ed.         ||       lberger@movaz.com
  RFC3472          ||      P. Ashwood-Smith, Ed., L. Berger, Ed.         ||       petera@nortelnetworks.com, lberger@movaz.com
  RFC3473          ||      L. Berger, Ed.         ||       lberger@movaz.com
  RFC3474          ||      Z. Lin, D. Pendarakis         ||       zhiwlin@nyct.com, dpendarakis@tellium.com
  RFC3475          ||      O. Aboul-Magd         ||       osama@nortelnetworks.com
  RFC3476          ||      B. Rajagopalan         ||       braja@tellium.com
  RFC3477          ||      K. Kompella, Y. Rekhter         ||       kireeti@juniper.net, yakov@juniper.net
  RFC3478          ||      M. Leelanivas, Y. Rekhter, R. Aggarwal         ||       manoj@juniper.net, yakov@juniper.net, rahul@redback.com
  RFC3479          ||      A. Farrel, Ed.         ||       afarrel@movaz.com, pjb@dataconnection.com, pmatthews@hyperchip.com, ewgray@GraIyMage.com, jack.shaio@vivacenetworks.com, tob@laurelnetworks.com, andy.malis@vivacenetworks.com
  RFC3480          ||      K. Kompella, Y. Rekhter, A. Kullberg         ||       kireeti@juniper.net, yakov@juniper.net, akullber@netplane.com
  RFC3481          ||      H. Inamura, Ed., G. Montenegro, Ed., R. Ludwig, A. Gurtov, F. Khafizov         ||       inamura@mml.yrp.nttdocomo.co.jp, gab@sun.com, Reiner.Ludwig@Ericsson.com, andrei.gurtov@sonera.com, faridk@nortelnetworks.com
  RFC3482          ||      M. Foster, T. McGarry, J. Yu         ||       mark.foster@neustar.biz, tom.mcgarry@neustar.biz, james.yu@neustar.biz
  RFC3483          ||       D. Rawlins, A. Kulkarni, M. Bokaemper, K. Chan         ||        Diana.Rawlins@wcom.com, amol.kulkarni@intel.com, khchan@nortelnetworks.com, mbokaemper@juniper.net 
  RFC3484          ||      R. Draves         ||       richdr@microsoft.com
  RFC3485          ||       M. Garcia-Martin, C. Bormann, J. Ott, R. Price, A. B. Roach         ||        miguel.a.garcia@ericsson.com, cabo@tzi.org, jo@tzi.org, richard.price@roke.co.uk, adam@dynamicsoft.com 
  RFC3486          ||      G. Camarillo         ||       Gonzalo.Camarillo@ericsson.com
  RFC3487          ||       H. Schulzrinne         ||        schulzrinne@cs.columbia.edu 
  RFC3488          ||       I. Wu, T. Eckert         ||        iwu@cisco.com 
  RFC3489          ||      J. Rosenberg, J. Weinberger, C. Huitema, R. Mahy         ||       jdrosen@dynamicsoft.com, jweinberger@dynamicsoft.com, huitema@microsoft.com, rohan@cisco.com
  RFC3490          ||      P. Faltstrom, P. Hoffman, A. Costello         ||       paf@cisco.com, phoffman@imc.org
  RFC3491          ||      P. Hoffman, M. Blanchet         ||       paul.hoffman@imc.org, Marc.Blanchet@viagenie.qc.ca
  RFC3492          ||      A. Costello         ||       
  RFC3493          ||       R. Gilligan, S. Thomson, J. Bound, J. McCann, W. Stevens         ||        gilligan@intransa.com, sethomso@cisco.com, Jim.Bound@hp.com, Jack.McCann@hp.com 
  RFC3494          ||       K. Zeilenga         ||        Kurt@OpenLDAP.org 
  RFC3495          ||       B. Beser, P. Duffy, Ed.         ||        burcak@juniper.net, paduffy@cisco.com 
  RFC3496          ||       A. G. Malis, T. Hsiao         ||        Andy.Malis@vivacenetworks.com, Tony.Hsiao@VivaceNetworks.com 
  RFC3497          ||       L. Gharai, C. Perkins, G. Goncher, A. Mankin         ||        ladan@isi.edu, csp@csperkins.org, mankin@psg.com, Gary.Goncher@tek.com 
  RFC3498          ||       J. Kuhfeld, J. Johnson, M. Thatcher         ||         
  RFC3499          ||       S. Ginoza         ||        ginoza@isi.edu 
  RFC3500          ||               ||         
  RFC3501          ||      M. Crispin         ||       MRC@CAC.Washington.EDU
  RFC3502          ||       M. Crispin         ||        MRC@CAC.Washington.EDU 
  RFC3503          ||       A. Melnikov         ||        mel@messagingdirect.com 
  RFC3504          ||       D. Eastlake         ||        Donald.Eastlake@motorola.com 
  RFC3505          ||       D. Eastlake         ||        Donald.Eastlake@motorola.com 
  RFC3506          ||       K. Fujimura, D. Eastlake         ||        fujimura@isl.ntt.co.jp, Donald.Eastlake@motorola.com 
  RFC3507          ||       J. Elson, A. Cerpa         ||        jelson@cs.ucla.edu, cerpa@cs.ucla.edu 
  RFC3508          ||       O. Levin         ||        orit@radvision.com 
  RFC3509          ||       A. Zinin, A. Lindem, D. Yeung         ||        zinin@psg.com, myeung@procket.com, acee@redback.com 
  RFC3510          ||       R. Herriot, I. McDonald         ||        bob@herriot.com, imcdonald@sharplabs.com 
  RFC3511          ||       B. Hickman, D. Newman, S. Tadjudin, T. Martin         ||        brooks.hickman@spirentcom.com, dnewman@networktest.com, Saldju.Tadjudin@spirentcom.com, tmartin@gvnw.com 
  RFC3512          ||       M. MacFaden, D. Partain, J. Saperia, W. Tackabury         ||         
  RFC3513          ||      R. Hinden, S. Deering         ||       bob.hinden@gmail.com, deering@cisco.com
  RFC3514          ||       S. Bellovin         ||        bellovin@acm.org 
  RFC3515          ||      R. Sparks         ||       rsparks@dynamicsoft.com
  RFC3516          ||       L. Nerenberg         ||        lyndon@orthanc.ab.ca 
  RFC3517          ||      E. Blanton, M. Allman, K. Fall, L. Wang         ||       eblanton@cs.purdue.edu, mallman@bbn.com, kfall@intel-research.net, lwang0@uky.edu
  RFC3518          ||       M. Higashiyama, F. Baker, T. Liao         ||        Mitsuru.Higashiyama@yy.anritsu.co.jp, fred@cisco.com, tawei@cisco.com 
  RFC3519          ||      H. Levkowetz, S. Vaarala         ||       henrik@levkowetz.com, sami.vaarala@iki.fi
  RFC3520          ||       L-N. Hamer, B. Gage, B. Kosinski, H. Shieh         ||        nhamer@nortelnetworks.com, brettk@invidi.com, gageb@nortelnetworks.com, hugh.shieh@attws.com 
  RFC3521          ||       L-N. Hamer, B. Gage, H. Shieh         ||        nhamer@nortelnetworks.com, gageb@nortelnetworks.com, hugh.shieh@attws.com 
  RFC3522          ||       R. Ludwig, M. Meyer         ||        Reiner.Ludwig@eed.ericsson.se, Michael.Meyer@eed.ericsson.se 
  RFC3523          ||       J. Polk         ||        jmpolk@cisco.com 
  RFC3524          ||       G. Camarillo, A. Monrad         ||        Gonzalo.Camarillo@ericsson.com, atle.monrad@ericsson.com 
  RFC3525          ||      C. Groves, Ed., M. Pantaleo, Ed., T. Anderson, Ed., T. Taylor, Ed.         ||       tlatla@verizon.net, Christian.Groves@ericsson.com.au, Marcello.Pantaleo@eed.ericsson.se, tom.taylor.stds@gmail.com
  RFC3526          ||       T. Kivinen, M. Kojo         ||        kivinen@ssh.fi, mika.kojo@helsinki.fi 
  RFC3527          ||       K. Kinnear, M. Stapp, R. Johnson, J. Kumarasamy         ||        kkinnear@cisco.com, mjs@cisco.com, jayk@cisco.com, raj@cisco.com 
  RFC3528          ||       W. Zhao, H. Schulzrinne, E. Guttman         ||        zwb@cs.columbia.edu, hgs@cs.columbia.edu, Erik.Guttman@sun.com 
  RFC3529          ||       W. Harold         ||        wharold@us.ibm.com 
  RFC3530          ||      S. Shepler, B. Callaghan, D. Robinson, R. Thurlow, C. Beame, M. Eisler, D. Noveck         ||       beame@bws.com, brent.callaghan@sun.com, mike@eisler.com, dnoveck@netapp.com, david.robinson@sun.com, robert.thurlow@sun.com
  RFC3531          ||       M. Blanchet         ||        Marc.Blanchet@viagenie.qc.ca 
  RFC3532          ||       T. Anderson, J. Buerkle         ||        todd.a.anderson@intel.com, joachim.buerkle@nortelnetworks.com 
  RFC3533          ||       S. Pfeiffer         ||        Silvia.Pfeiffer@csiro.au 
  RFC3534          ||      L. Walleij         ||       triad@df.lth.se
  RFC3535          ||       J. Schoenwaelder         ||        j.schoenwaelder@iu-bremen.de 
  RFC3536          ||      P. Hoffman         ||       paul.hoffman@imc.org
  RFC3537          ||       J. Schaad, R. Housley         ||        jimsch@exmsft.com, housley@vigilsec.com 
  RFC3538          ||       Y. Kawatsura         ||        kawatura@bisd.hitachi.co.jp 
  RFC3539          ||       B. Aboba, J. Wood         ||        bernarda@microsoft.com, jonwood@speakeasy.net 
  RFC3540          ||       N. Spring, D. Wetherall, D. Ely         ||        nspring@cs.washington.edu, djw@cs.washington.edu, ely@cs.washington.edu 
  RFC3541          ||       A. Walsh         ||        aaron@mantiscorp.com 
  RFC3542          ||       W. Stevens, M. Thomas, E. Nordmark, T. Jinmei         ||        matt@3am-software.com, Erik.Nordmark@sun.com, jinmei@isl.rdc.toshiba.co.jp 
  RFC3543          ||       S. Glass, M. Chandra         ||        steven.glass@sun.com, mchandra@cisco.com 
  RFC3544          ||      T. Koren, S. Casner, C. Bormann         ||       tmima@cisco.com, casner@packetdesign.com, cabo@tzi.org
  RFC3545          ||       T. Koren, S. Casner, J. Geevarghese, B. Thompson, P. Ruddy         ||        tmima@cisco.com, casner@acm.org, geevjohn@hotmail.com, brucet@cisco.com, pruddy@cisco.com 
  RFC3546          ||       S. Blake-Wilson, M. Nystrom, D. Hopwood, J. Mikkelsen, T. Wright         ||        sblakewilson@bcisse.com, magnus@rsasecurity.com, david.hopwood@zetnet.co.uk, janm@transactionware.com, timothy.wright@vodafone.com 
  RFC3547          ||      M. Baugher, B. Weis, T. Hardjono, H. Harney         ||       mbaugher@cisco.com, thardjono@verisign.com, hh@sparta.com, bew@cisco.com
  RFC3548          ||       S. Josefsson, Ed.         ||         
  RFC3549          ||       J. Salim, H. Khosravi, A. Kleen, A. Kuznetsov         ||        hadi@znyx.com, hormuzd.m.khosravi@intel.com, ak@suse.de, kuznet@ms2.inr.ac.ru 
  RFC3550          ||      H. Schulzrinne, S. Casner, R. Frederick, V. Jacobson         ||       schulzrinne@cs.columbia.edu, casner@acm.org, ronf@bluecoat.com, van@packetdesign.com
  RFC3551          ||      H. Schulzrinne, S. Casner         ||       schulzrinne@cs.columbia.edu, casner@acm.org
  RFC3552          ||       E. Rescorla, B. Korver         ||        ekr@rtfm.com, briank@xythos.com, iab@iab.org 
  RFC3553          ||       M. Mealling, L. Masinter, T. Hardie, G. Klyne         ||        michael@verisignlabs.com, LMM@acm.org, hardie@qualcomm.com, GK-IETF@ninebynine.org 
  RFC3554          ||       S. Bellovin, J. Ioannidis, A. Keromytis, R. Stewart         ||       smb@research.att.com, ji@research.att.com, angelos@cs.columbia.edu, randall@lakerest.net
  RFC3555          ||       S. Casner, P. Hoschka         ||        casner@acm.org, ph@w3.org 
  RFC3556          ||       S. Casner         ||        casner@acm.org 
  RFC3557          ||       Q. Xie, Ed.         ||        bdp003@motorola.com, Senaka.Balasuriya@motorola.com, yoonie@verbaltek.com, stephane.maes@oracle.com, hgarudad@qualcomm.com, Qiaobing.Xie@motorola.com 
  RFC3558          ||       A. Li         ||        adamli@icsl.ucla.edu 
  RFC3559          ||       D. Thaler         ||        dthaler@microsoft.com 
  RFC3560          ||       R. Housley         ||        housley@vigilsec.com 
  RFC3561          ||       C. Perkins, E. Belding-Royer, S. Das         ||        Charles.Perkins@nokia.com, ebelding@cs.ucsb.edu, sdas@ececs.uc.edu 
  RFC3562          ||       M. Leech         ||        mleech@nortelnetworks.com 
  RFC3563          ||      A. Zinin         ||       zinin@psg.com
  RFC3564          ||      F. Le Faucheur, W. Lai         ||       
  RFC3565          ||       J. Schaad         ||        jimsch@exmsft.com 
  RFC3566          ||       S. Frankel, H. Herbert         ||        sheila.frankel@nist.gov, howard.c.herbert@intel.com 
  RFC3567          ||      T. Li, R. Atkinson         ||       tli@procket.net, rja@extremenetworks.com
  RFC3568          ||       A. Barbir, B. Cain, R. Nair, O. Spatscheck         ||        abbieb@nortelnetworks.com, bcain@storigen.com, nair_raj@yahoo.com, spatsch@research.att.com 
  RFC3569          ||       S. Bhattacharyya, Ed.         ||         
  RFC3570          ||      P. Rzewski, M. Day, D. Gilletti         ||       mday@alum.mit.edu, dgilletti@yahoo.com, philrz@yahoo.com
  RFC3571          ||      D. Rawlins, A. Kulkarni, K. Ho Chan, M. Bokaemper, D. Dutt         ||       Diana.Rawlins@mci.com, amol.kulkarni@intel.com, khchan@nortelnetworks.com, mbokaemper@juniper.net, ddutt@cisco.com
  RFC3572          ||      T. Ogura, M. Maruyama, T. Yoshida         ||       ogura@core.ecl.net, mitsuru@core.ecl.net, yoshida@peta.arch.ecl.net
  RFC3573          ||       I. Goyret         ||        igoyret@lucent.com 
  RFC3574          ||       J. Soininen, Ed.         ||         
  RFC3575          ||      B. Aboba         ||       bernarda@microsoft.com
  RFC3576          ||      M. Chiba, G. Dommety, M. Eklund, D. Mitton, B. Aboba         ||       mchiba@cisco.com, gdommety@cisco.com, meklund@cisco.com, david@mitton.com, bernarda@microsoft.com
  RFC3577          ||       S. Waldbusser, R. Cole, C. Kalbfleisch, D. Romascanu         ||        waldbusser@nextbeacon.com, cwk@verio.net, rgcole@att.com, dromasca@gmail.com  
  RFC3578          ||       G. Camarillo, A. B. Roach, J. Peterson, L. Ong         ||        Gonzalo.Camarillo@ericsson.com, adam@dynamicsoft.com, jon.peterson@neustar.biz, lyong@ciena.com 
  RFC3579          ||      B. Aboba, P. Calhoun         ||       bernarda@microsoft.com, pcalhoun@airespace.com
  RFC3580          ||      P. Congdon, B. Aboba, A. Smith, G. Zorn, J. Roese         ||       paul_congdon@hp.com, bernarda@microsoft.com, ah_smith@acm.org, jjr@enterasys.com, gwz@cisco.com
  RFC3581          ||       J. Rosenberg, H. Schulzrinne         ||        jdrosen@dynamicsoft.com, schulzrinne@cs.columbia.edu 
  RFC3582          ||       J. Abley, B. Black, V. Gill         ||        jabley@isc.org, ben@layer8.net, vijaygill9@aol.com 
  RFC3583          ||       H. Chaskar, Ed.         ||        john.loughney@nokia.com, hemant.chaskar@nokia.com 
  RFC3584          ||       R. Frye, D. Levi, S. Routhier, B. Wijnen         ||         
  RFC3585          ||       J. Jason, L. Rafalow, E. Vyncke         ||        jamie.jason@intel.com, rafalow@watson.ibm.com, evyncke@cisco.com 
  RFC3586          ||       M. Blaze, A. Keromytis, M. Richardson, L. Sanchez         ||        mab@crypto.com, angelos@cs.columbia.edu, mcr@sandelman.ottawa.on.ca, lsanchez@xapiens.com 
  RFC3587          ||      R. Hinden, S. Deering, E. Nordmark         ||       bob.hinden@gmail.com, erik.nordmark@sun.com
  RFC3588          ||      P. Calhoun, J. Loughney, E. Guttman, G. Zorn, J. Arkko         ||       pcalhoun@airespace.com, john.Loughney@nokia.com, Jari.Arkko@ericsson.com, erik.guttman@sun.com
  RFC3589          ||       J. Loughney         ||        john.Loughney@Nokia.com 
  RFC3590          ||       B. Haberman         ||        brian@innovationslab.net 
  RFC3591          ||       H-K. Lam, M. Stewart, A. Huynh         ||        mstewart1@nc.rr.com, a_n_huynh@yahoo.com, hklam@lucent.com 
  RFC3592          ||       K. Tesink         ||        kaj@research.telcordia.com 
  RFC3593          ||       K. Tesink, Ed.         ||         
  RFC3594          ||       P. Duffy         ||        paduffy@cisco.com 
  RFC3595          ||       B. Wijnen         ||        bwijnen@lucent.com 
  RFC3596          ||       S. Thomson, C. Huitema, V. Ksinant, M. Souissi         ||        sethomso@cisco.com, huitema@microsoft.com, vladimir.ksinant@6wind.com, Mohsen.Souissi@nic.fr 
  RFC3597          ||      A. Gustafsson         ||       gson@nominum.com
  RFC3598          ||      K. Murchison         ||       ken@oceana.com
  RFC3599          ||       S. Ginoza         ||        ginoza@isi.edu 
  RFC3600          ||      J. Reynolds, Ed., S. Ginoza, Ed.         ||       
  RFC3601          ||       C. Allocchio         ||        Claudio.Allocchio@garr.it 
  RFC3602          ||       S. Frankel, R. Glenn, S. Kelly         ||        sheila.frankel@nist.gov, scott@hyperthought.com, rob.glenn@nist.gov 
  RFC3603          ||      W. Marshall, Ed., F. Andreasen, Ed.         ||       
  RFC3604          ||       H. Khosravi, G. Kullgren, S. Shew, J. Sadler, A. Watanabe         ||        hormuzd.m.khosravi@intel.com, geku@nortelnetworks.com, Jonathan.Sadler@tellabs.com, sdshew@nortelnetworks.com, Shiomoto.Kohei@lab.ntt.co.jp, atsushi@exa.onlab.ntt.co.jp, okamoto@exa.onlab.ntt.co.jp 
  RFC3605          ||       C. Huitema         ||        huitema@microsoft.com 
  RFC3606          ||       F. Ly, M. Noto, A. Smith, E. Spiegel, K. Tesink         ||        faye@pedestalnetworks.com, mnoto@cisco.com, ah_smith@acm.org, mspiegel@cisco.com, kaj@research.telcordia.com 
  RFC3607          ||       M. Leech         ||        mleech@nortelnetworks.com 
  RFC3608          ||      D. Willis, B. Hoeneisen         ||       dean.willis@softarmor.com, hoeneisen@switch.ch
  RFC3609          ||       R. Bonica, K. Kompella, D. Meyer         ||        ronald.p.bonica@mci.com, kireeti@juniper.net, dmm@maoz.com 
  RFC3610          ||       D. Whiting, R. Housley, N. Ferguson         ||        dwhiting@hifn.com, housley@vigilsec.com, niels@macfergus.com 
  RFC3611          ||       T. Friedman, Ed., R. Caceres, Ed., A. Clark, Ed.         ||        almeroth@cs.ucsb.edu, caceres@watson.ibm.com, alan@telchemy.com, robert.cole@jhuapl.edu, duffield@research.att.com, timur.friedman@lip6.fr, khedayat@brixnet.com, ksarac@utdallas.edu, magnus.westerlund@ericsson.com 
  RFC3612          ||       A. Farrel         ||        adrian@olddog.co.uk 
  RFC3613          ||       R. Morgan, K. Hazelton         ||        rlmorgan@washington.edu, hazelton@doit.wisc.edu 
  RFC3614          ||       J. Smith         ||        jrsmith@watson.ibm.com 
  RFC3615          ||       J. Gustin, A. Goyens         ||        jean-marc.gustin@swift.com, andre.goyens@swift.com 
  RFC3616          ||       F. Bellifemine, I. Constantinescu, S. Willmott         ||        Fabio.Bellifemine@TILAB.COM, ion.constantinescu@epfl.ch, steve@lsi.upc.es 
  RFC3617          ||       E. Lear         ||        lear@cisco.com 
  RFC3618          ||       B. Fenner, Ed., D. Meyer, Ed.         ||         
  RFC3619          ||       S. Shah, M. Yip         ||        sshah@extremenetworks.com, my@extremenetworks.com 
  RFC3620          ||       D. New         ||        dnew@san.rr.com 
  RFC3621          ||       A. Berger, D. Romascanu         ||        avib@PowerDsine.com, dromasca@gmail.com  
  RFC3622          ||       M. Mealling         ||        michael@neonym.net 
  RFC3623          ||       J. Moy, P. Pillay-Esnault, A. Lindem         ||        jmoy@sycamorenet.com, padma@juniper.net, acee@redback.com 
  RFC3624          ||       B. Foster, D. Auerbach, F. Andreasen         ||        fandreas@cisco.com, dea@cisco.com, bfoster@cisco.com 
  RFC3625          ||       R. Gellens, H. Garudadri         ||         
  RFC3626          ||       T. Clausen, Ed., P. Jacquet, Ed.         ||        T.Clausen@computer.org, Philippe.Jacquet@inria.fr 
  RFC3627          ||      P. Savola         ||       psavola@funet.fi
  RFC3628          ||       D. Pinkas, N. Pope, J. Ross         ||        Denis.Pinkas@bull.net, pope@secstan.com, ross@secstan.com, claire.desclercs@etsi.org 
  RFC3629          ||       F. Yergeau         ||        fyergeau@alis.com 
  RFC3630          ||      D. Katz, K. Kompella, D. Yeung         ||       dkatz@juniper.net, myeung@procket.com, kireeti@juniper.net
  RFC3631          ||       S. Bellovin, Ed., J. Schiller, Ed., C. Kaufman, Ed.         ||         
  RFC3632          ||       S. Hollenbeck, S. Veeramachaneni, S. Yalamanchilli         ||        shollenbeck@verisign.com, sveerama@verisign.com, syalamanchilli@verisign.com 
  RFC3633          ||      O. Troan, R. Droms         ||       ot@cisco.com, rdroms@cisco.com
  RFC3634          ||       K. Luehrs, R. Woundy, J. Bevilacqua, N. Davoust         ||        k.luehrs@cablelabs.com, richard_woundy@cable.comcast.com, john@yas.com, nancy@yas.com 
  RFC3635          ||       J. Flick         ||        johnf@rose.hp.com 
  RFC3636          ||       J. Flick         ||        johnf@rose.hp.com 
  RFC3637          ||       C.M. Heard, Ed.         ||         
  RFC3638          ||       J. Flick, C. M. Heard         ||        johnf@rose.hp.com, heard@pobox.com 
  RFC3639          ||       M. St. Johns, Ed., G. Huston, Ed., IAB         ||         
  RFC3640          ||      J. van der Meer, D. Mackie, V. Swaminathan, D. Singer, P. Gentric         ||       jan.vandermeer@philips.com, dmackie@apple.com, viswanathan.swaminathan@sun.com, singer@apple.com, philippe.gentric@philips.com
  RFC3641          ||       S. Legg         ||        steven.legg@adacel.com.au 
  RFC3642          ||       S. Legg         ||        steven.legg@adacel.com.au 
  RFC3643          ||       R. Weber, M. Rajagopal, F. Travostino, M. O'Donnell, C. Monia, M. Merhar         ||        roweber@ieee.org, muralir@broadcom.com, travos@nortelnetworks.com, cmonia@pacbell.net, milan.merhar@sun.com 
  RFC3644          ||       Y. Snir, Y. Ramberg, J. Strassner, R. Cohen, B. Moore         ||        yramberg@cisco.com, ysnir@cisco.com, john.strassner@intelliden.com, ronc@lyciumnetworks.com, remoore@us.ibm.com 
  RFC3645          ||       S. Kwan, P. Garg, J. Gilroy, L. Esibov, J. Westhead, R. Hall         ||        skwan@microsoft.com, praeritg@microsoft.com, jamesg@microsoft.com, levone@microsoft.com, randyhall@lucent.com, jwesth@microsoft.com 
  RFC3646          ||       R. Droms, Ed.         ||        rdroms@cisco.com 
  RFC3647          ||       S. Chokhani, W. Ford, R. Sabett, C. Merrill, S. Wu         ||        chokhani@orionsec.com, wford@verisign.com, rsabett@cooley.com, cmerrill@mccarter.com, swu@infoliance.com 
  RFC3648          ||       J. Whitehead, J. Reschke, Ed.         ||        ejw@cse.ucsc.edu, julian.reschke@greenbytes.de 
  RFC3649          ||       S. Floyd         ||        floyd@acm.org 
  RFC3650          ||       S. Sun, L. Lannom, B. Boesch         ||        ssun@cnri.reston.va.us, llannom@cnri.reston.va.us, bboesch@cnri.reston.va.us 
  RFC3651          ||       S. Sun, S. Reilly, L. Lannom         ||        ssun@cnri.reston.va.us, sreilly@cnri.reston.va.us, llannom@cnri.reston.va.us 
  RFC3652          ||       S. Sun, S. Reilly, L. Lannom, J. Petrone         ||        ssun@cnri.reston.va.us, sreilly@cnri.reston.va.us, llannom@cnri.reston.va.us, jpetrone@cnri.reston.va.us 
  RFC3653          ||       J. Boyer, M. Hughes, J. Reagle         ||        jboyer@PureEdge.com, Merlin.Hughes@betrusted.com, reagle@mit.edu 
  RFC3654          ||       H. Khosravi, Ed., T. Anderson, Ed.         ||        edbowen@us.ibm.com, rdantu@unt.edu, avri@acm.org, ram.gopal@nokia.com, hadi@znyx.com, muneyb@avaya.com, margaret.wasserman@nokia.com, hormuzd.m.khosravi@intel.com, todd.a.anderson@intel.com 
  RFC3655          ||       B. Wellington, O. Gudmundsson         ||        Brian.Wellington@nominum.com, ogud@ogud.com 
  RFC3656          ||       R. Siemborski         ||         
  RFC3657          ||       S. Moriai, A. Kato         ||        camellia@isl.ntt.co.jp, akato@po.ntts.co.jp 
  RFC3658          ||       O. Gudmundsson         ||        ds-rfc@ogud.com 
  RFC3659          ||      P. Hethmon         ||       phethmon@hethmon.com
  RFC3660          ||       B. Foster, F. Andreasen         ||        bfoster@cisco.com, fandreas@cisco.com 
  RFC3661          ||       B. Foster, C. Sivachelvan         ||        chelliah@cisco.com, bfoster@cisco.com 
  RFC3662          ||       R. Bless, K. Nichols, K. Wehrle         ||        bless@tm.uka.de, knichols@ieee.org, Klaus.Wehrle@uni-tuebingen.de 
  RFC3663          ||       A. Newton         ||        anewton@verisignlabs.com 
  RFC3664          ||       P. Hoffman         ||        paul.hoffman@vpnc.org 
  RFC3665          ||       A. Johnston, S. Donovan, R. Sparks, C. Cunningham, K. Summers         ||        alan.johnston@mci.com, sdonovan@dynamicsoft.com, rsparks@dynamicsoft.com, ccunningham@dynamicsoft.com, kevin.summers@sonusnet.com 
  RFC3666          ||       A. Johnston, S. Donovan, R. Sparks, C. Cunningham, K. Summers         ||        alan.johnston@mci.com, sdonovan@dynamicsoft.com, rsparks@dynamicsoft.com, ccunningham@dynamicsoft.com, kevin.summers@sonusnet.com 
  RFC3667          ||       S. Bradner         ||         
  RFC3668          ||      S. Bradner         ||       
  RFC3669          ||       S. Brim         ||        sbrim@cisco.com 
  RFC3670          ||       B. Moore, D. Durham, J. Strassner, A. Westerinen, W. Weiss         ||        remoore@us.ibm.com, david.durham@intel.com, john.strassner@intelliden.com, andreaw@cisco.com, walterweiss@attbi.com 
  RFC3671          ||       K. Zeilenga         ||        Kurt@OpenLDAP.org 
  RFC3672          ||       K. Zeilenga         ||        Kurt@OpenLDAP.org, steven.legg@adacel.com.au 
  RFC3673          ||       K. Zeilenga         ||        Kurt@OpenLDAP.org 
  RFC3674          ||       K. Zeilenga         ||        Kurt@OpenLDAP.org 
  RFC3675          ||       D. Eastlake 3rd         ||        dee3@torque.pothole.com 
  RFC3676          ||       R. Gellens         ||        randy@qualcomm.com 
  RFC3677          ||      L. Daigle, Ed., Internet Architecture Board         ||       iab@iab.org
  RFC3678          ||       D. Thaler, B. Fenner, B. Quinn         ||        dthaler@microsoft.com, fenner@research.att.com, rcq@ipmulticast.com 
  RFC3679          ||       R. Droms         ||        rdroms@cisco.com 
  RFC3680          ||      J. Rosenberg         ||       jdrosen@dynamicsoft.com
  RFC3681          ||       R. Bush, R. Fink         ||        randy@psg.com, bob@thefinks.com 
  RFC3682          ||      V. Gill, J. Heasley, D. Meyer         ||       vijay@umbc.edu, heas@shrubbery.net, dmm@1-4-5.net
  RFC3683          ||       M. Rose         ||       mrose17@gmail.com
  RFC3684          ||       R. Ogier, F. Templin, M. Lewis         ||        ogier@erg.sri.com, ftemplin@iprg.nokia.com, lewis@erg.sri.com 
  RFC3685          ||      C. Daboo         ||       daboo@cyrusoft.com
  RFC3686          ||       R. Housley         ||        housley@vigilsec.com 
  RFC3687          ||       S. Legg         ||        steven.legg@adacel.com.au 
  RFC3688          ||       M. Mealling         ||        michael@verisignlabs.com 
  RFC3689          ||       K. Carlberg, R. Atkinson         ||        k.carlberg@cs.ucl.ac.uk, rja@extremenetworks.com 
  RFC3690          ||       K. Carlberg, R. Atkinson         ||        k.carlberg@cs.ucl.ac.uk, rja@extremenetworks.com 
  RFC3691          ||      A. Melnikov         ||       Alexey.Melnikov@isode.com
  RFC3692          ||       T. Narten         ||        narten@us.ibm.com 
  RFC3693          ||      J. Cuellar, J. Morris, D. Mulligan, J. Peterson, J. Polk         ||       Jorge.Cuellar@siemens.com, jmorris@cdt.org, dmulligan@law.berkeley.edu, jon.peterson@neustar.biz, jmpolk@cisco.com
  RFC3694          ||      M. Danley, D. Mulligan, J. Morris, J. Peterson         ||       mre213@nyu.edu, dmulligan@law.berkeley.edu, jmorris@cdt.org, jon.peterson@neustar.biz
  RFC3695          ||      M. Luby, L. Vicisano         ||       luby@digitalfountain.com, lorenzo@cisco.com
  RFC3696          ||       J. Klensin         ||        john-ietf@jck.com 
  RFC3697          ||      J. Rajahalme, A. Conta, B. Carpenter, S. Deering         ||       jarno.rajahalme@nokia.com, aconta@txc.com, brc@zurich.ibm.com
  RFC3698          ||       K. Zeilenga, Ed.         ||        Kurt@OpenLDAP.org 
  RFC3700          ||      J. Reynolds, Ed., S. Ginoza, Ed.         ||       
  RFC3701          ||      R. Fink, R. Hinden         ||       bob@thefinks.com, bob.hinden@gmail.com
  RFC3702          ||       J. Loughney, G. Camarillo         ||        John.Loughney@nokia.com, Gonzalo.Camarillo@ericsson.com 
  RFC3703          ||       J. Strassner, B. Moore, R. Moats, E. Ellesson         ||        john.strassner@intelliden.com, remoore@us.ibm.com, rmoats@lemurnetworks.net, ellesson@mindspring.com 
  RFC3704          ||       F. Baker, P. Savola         ||        fred@cisco.com, psavola@funet.fi 
  RFC3705          ||       B. Ray, R. Abbi         ||        rray@pesa.com, Rajesh.Abbi@alcatel.com 
  RFC3706          ||       G. Huang, S. Beaulieu, D. Rochefort         ||         
  RFC3707          ||       A. Newton         ||        anewton@verisignlabs.com 
  RFC3708          ||       E. Blanton, M. Allman         ||        eblanton@cs.purdue.edu, mallman@icir.org 
  RFC3709          ||      S. Santesson, R. Housley, T. Freeman         ||       stefans@microsoft.com, housley@vigilsec.com, trevorf@microsoft.com
  RFC3710          ||      H. Alvestrand         ||       harald@alvestrand.no
  RFC3711          ||      M. Baugher, D. McGrew, M. Naslund, E. Carrara, K. Norrman         ||       mbaugher@cisco.com, elisabetta.carrara@ericsson.com, mcgrew@cisco.com, mats.naslund@ericsson.com, karl.norrman@ericsson.com
  RFC3712          ||      P. Fleming, I. McDonald         ||       flemingp@us.ibm.com, flemingp@us.ibm.com, flemingp@us.ibm.com
  RFC3713          ||       M. Matsui, J. Nakajima, S. Moriai         ||        matsui@iss.isl.melco.co.jp, june15@iss.isl.melco.co.jp, shiho@rd.scei.sony.co.jp 
  RFC3714          ||      S. Floyd, Ed., J. Kempf, Ed.         ||       iab@iab.org
  RFC3715          ||       B. Aboba, W. Dixon         ||        bernarda@microsoft.com, ietf-wd@v6security.com 
  RFC3716          ||       IAB Advisory Committee         ||        iab@iab.org 
  RFC3717          ||       B. Rajagopalan, J. Luciani, D. Awduche         ||        braja@tellium.com, james_luciani@mindspring.com, awduche@awduche.com 
  RFC3718          ||       R. McGowan         ||         
  RFC3719          ||       J. Parker, Ed.         ||        jparker@axiowave.com 
  RFC3720          ||      J. Satran, K. Meth, C. Sapuntzakis, M. Chadalapaka, E. Zeidner         ||       Julian_Satran@il.ibm.com, meth@il.ibm.com, csapuntz@alum.mit.edu, efri@xiv.co.il, cbm@rose.hp.com
  RFC3721          ||      M. Bakke, J. Hafner, J. Hufferd, K. Voruganti, M. Krueger         ||       kaladhar@us.ibm.com, mbakke@cisco.com, hafner@almaden.ibm.com, hufferd@us.ibm.com, marjorie_krueger@hp.com
  RFC3722          ||       M. Bakke         ||        mbakke@cisco.com 
  RFC3723          ||      B. Aboba, J. Tseng, J. Walker, V. Rangan, F. Travostino         ||       bernarda@microsoft.com, joshtseng@yahoo.com, jesse.walker@intel.com, vrangan@brocade.com, travos@nortelnetworks.com
  RFC3724          ||      J. Kempf, Ed., R. Austein, Ed., IAB         ||       
  RFC3725          ||       J. Rosenberg, J. Peterson, H. Schulzrinne, G. Camarillo         ||        jdrosen@dynamicsoft.com, jon.peterson@neustar.biz, schulzrinne@cs.columbia.edu, Gonzalo.Camarillo@ericsson.com 
  RFC3726          ||       M. Brunner, Ed.         ||        brunner@netlab.nec.de, robert.hancock@roke.co.uk, eleanor.hepworth@roke.co.uk, cornelia.kappler@siemens.com, Hannes.Tschofenig@mchp.siemens.de 
  RFC3727          ||       S. Legg         ||        steven.legg@adacel.com.au 
  RFC3728          ||       B. Ray, R. Abbi         ||        rray@pesa.com, Rajesh.Abbi@alcatel.com 
  RFC3729          ||       S. Waldbusser         ||        waldbusser@nextbeacon.com 
  RFC3730          ||      S. Hollenbeck         ||       shollenbeck@verisign.com
  RFC3731          ||      S. Hollenbeck         ||       shollenbeck@verisign.com
  RFC3732          ||      S. Hollenbeck         ||       shollenbeck@verisign.com
  RFC3733          ||      S. Hollenbeck         ||       shollenbeck@verisign.com
  RFC3734          ||      S. Hollenbeck         ||       shollenbeck@verisign.com
  RFC3735          ||       S. Hollenbeck         ||        shollenbeck@verisign.com 
  RFC3736          ||       R. Droms         ||        rdroms@cisco.com 
  RFC3737          ||       B. Wijnen, A. Bierman         ||        bwijnen@lucent.com, andy@yumaworks.com
  RFC3738          ||       M. Luby, V. Goyal         ||        luby@digitalfountain.com, v.goyal@ieee.org 
  RFC3739          ||       S. Santesson, M. Nystrom, T. Polk         ||        stefans@microsoft.com, wpolk@nist.gov, magnus@rsasecurity.com 
  RFC3740          ||       T. Hardjono, B. Weis         ||        thardjono@verisign.com, bew@cisco.com 
  RFC3741          ||       J. Boyer, D. Eastlake 3rd, J. Reagle         ||        jboyer@PureEdge.com, Donald.Eastlake@motorola.com, reagle@mit.edu 
  RFC3742          ||       S. Floyd         ||        floyd@icir.org 
  RFC3743          ||       K. Konishi, K. Huang, H. Qian, Y. Ko         ||        konishi@jp.apan.net, huangk@alum.sinica.edu, Hlqian@cnnic.net.cn, yw@mrko.pe.kr, jseng@pobox.org.sg, rickard@rickardgroup.com 
  RFC3744          ||       G. Clemm, J. Reschke, E. Sedlar, J. Whitehead         ||        geoffrey.clemm@us.ibm.com, julian.reschke@greenbytes.de, eric.sedlar@oracle.com, ejw@cse.ucsc.edu 
  RFC3745          ||       D. Singer, R. Clark, D. Lee         ||        singer@apple.com, richard@elysium.ltd.uk, dlee@yahoo-inc.com 
  RFC3746          ||       L. Yang, R. Dantu, T. Anderson, R. Gopal         ||        lily.l.yang@intel.com, rdantu@unt.edu, todd.a.anderson@intel.com, ram.gopal@nokia.com 
  RFC3747          ||       H. Hazewinkel, Ed., D. Partain, Ed.         ||         
  RFC3748          ||      B. Aboba, L. Blunk, J. Vollbrecht, J. Carlson, H. Levkowetz, Ed.         ||       bernarda@microsoft.com, ljb@merit.edu, jrv@umich.edu, james.d.carlson@sun.com, henrik@levkowetz.com
  RFC3749          ||      S. Hollenbeck         ||       shollenbeck@verisign.com
  RFC3750          ||       C. Huitema, R. Austein, S. Satapati, R. van der Pol         ||        huitema@microsoft.com, sra@isc.org, satapati@cisco.com, Ronald.vanderPol@nlnetlabs.nl 
  RFC3751          ||      S. Bradner         ||       sob@harvard.edu
  RFC3752          ||       A. Barbir, E. Burger, R. Chen, S. McHenry, H. Orman, R. Penno         ||        abbieb@nortelnetworks.com, e.burger@ieee.org, chen@research.att.com, stephen@mchenry.net, ho@alum.mit.edu, rpenno@nortelnetworks.com 
  RFC3753          ||       J. Manner, Ed., M. Kojo, Ed.         ||        jmanner@cs.helsinki.fi, kojo@cs.helsinki.fi 
  RFC3754          ||       R. Bless, K. Wehrle         ||        bless@tm.uka.de, Klaus.Wehrle@uni-tuebingen.de 
  RFC3755          ||      S. Weiler         ||       weiler@tislabs.com
  RFC3756          ||       P. Nikander, Ed., J. Kempf, E. Nordmark         ||        pekka.nikander@nomadiclab.com, kempf@docomolabs-usa.com, erik.nordmark@sun.com 
  RFC3757          ||       O. Kolkman, J. Schlyter, E. Lewis         ||        olaf@ripe.net, jakob@nic.se, edlewis@arin.net 
  RFC3758          ||       R. Stewart, M. Ramalho, Q. Xie, M. Tuexen, P. Conrad         ||       randall@lakerest.net, mramalho@cisco.com, qxie1@email.mot.com, tuexen@fh-muenster.de, conrad@acm.org
  RFC3759          ||      L-E. Jonsson         ||       lars-erik.jonsson@ericsson.com
  RFC3760          ||      D. Gustafson, M. Just, M. Nystrom         ||       degustafson@comcast.net, Just.Mike@tbs-sct.gc.ca, magnus@rsasecurity.com
  RFC3761          ||      P. Faltstrom, M. Mealling         ||       paf@cisco.com
  RFC3762          ||      O. Levin         ||       oritl@microsoft.com
  RFC3763          ||       S. Shalunov, B. Teitelbaum         ||        shalunov@internet2.edu, ben@internet2.edu 
  RFC3764          ||      J. Peterson         ||       jon.peterson@neustar.biz
  RFC3765          ||       G. Huston         ||        gih@telstra.net 
  RFC3766          ||       H. Orman, P. Hoffman         ||        hilarie@purplestreak.com, paul.hoffman@vpnc.org 
  RFC3767          ||       S. Farrell, Ed.         ||         
  RFC3768          ||      R. Hinden, Ed.         ||       bob.hinden@gmail.com
  RFC3769          ||       S. Miyakawa, R. Droms         ||        miyakawa@nttv6.jp, rdroms@cisco.com 
  RFC3770          ||       R. Housley, T. Moore         ||        housley@vigilsec.com, timmoore@microsoft.com 
  RFC3771          ||       R. Harrison, K. Zeilenga         ||        roger_harrison@novell.com, Kurt@OpenLDAP.org 
  RFC3772          ||       J. Carlson, R. Winslow         ||         
  RFC3773          ||       E. Candell         ||        emily.candell@comverse.com 
  RFC3774          ||       E. Davies, Ed.         ||         
  RFC3775          ||      D. Johnson, C. Perkins, J. Arkko         ||       dbj@cs.rice.edu, charliep@iprg.nokia.com, jari.arkko@ericsson.com
  RFC3776          ||       J. Arkko, V. Devarapalli, F. Dupont         ||        jari.arkko@ericsson.com, vijayd@iprg.nokia.com, Francis.Dupont@enst-bretagne.fr 
  RFC3777          ||      J. Galvin, Ed.         ||       galvin+ietf@elistx.com
  RFC3778          ||      E. Taft, J. Pravetz, S. Zilles, L. Masinter         ||       taft@adobe.com, jpravetz@adobe.com, szilles@adobe.com, LMM@acm.org
  RFC3779          ||       C. Lynn, S. Kent, K. Seo         ||        CLynn@BBN.Com, Kent@BBN.Com, KSeo@BBN.Com 
  RFC3780          ||       F. Strauss, J. Schoenwaelder         ||        strauss@ibr.cs.tu-bs.de, j.schoenwaelder@iu-bremen.de 
  RFC3781          ||       F. Strauss, J. Schoenwaelder         ||        strauss@ibr.cs.tu-bs.de, j.schoenwaelder@iu-bremen.de 
  RFC3782          ||      S. Floyd, T. Henderson, A. Gurtov         ||       floyd@acm.org, thomas.r.henderson@boeing.com, andrei.gurtov@teliasonera.com
  RFC3783          ||       M. Chadalapaka, R. Elliott         ||        cbm@rose.hp.com, elliott@hp.com 
  RFC3784          ||      H. Smit, T. Li         ||       hhwsmit@xs4all.nl, tony.li@tony.li
  RFC3785          ||       F. Le Faucheur, R. Uppili, A. Vedrenne, P. Merckx, T. Telkamp         ||        flefauch@cisco.com, alain.vedrenne@equant.com, pierre.merckx@equant.com, telkamp@gblx.net 
  RFC3786          ||      A. Hermelin, S. Previdi, M. Shand         ||       amir@montilio.com, sprevidi@cisco.com, mshand@cisco.com
  RFC3787          ||       J. Parker, Ed.         ||        jparker@axiowave.com 
  RFC3788          ||       J. Loughney, M. Tuexen, Ed., J. Pastor-Balbas         ||        john.loughney@nokia.com, tuexen@fh-muenster.de, j.javier.pastor@ericsson.com 
  RFC3789          ||       P. Nesser, II, A. Bergstrom, Ed.         ||        phil@nesser.com, andreas.bergstrom@hiof.no 
  RFC3790          ||       C. Mickles, Ed., P. Nesser, II         ||        cmickles.ee88@gtalumni.org, phil@nesser.com 
  RFC3791          ||       C. Olvera, P. Nesser, II         ||        cesar.olvera@consulintel.es, phil@nesser.com 
  RFC3792          ||       P. Nesser, II, A. Bergstrom, Ed.         ||        phil@nesser.com, andreas.bergstrom@hiof.no 
  RFC3793          ||       P. Nesser, II, A. Bergstrom, Ed.         ||        phil@nesser.com, andreas.bergstrom@hiof.no 
  RFC3794          ||       P. Nesser, II, A. Bergstrom, Ed.         ||        phil@nesser.com, andreas.bergstrom@hiof.no 
  RFC3795          ||       R. Sofia, P. Nesser, II         ||        rsofia@zmail.pt, phil@nesser.com 
  RFC3796          ||       P. Nesser, II, A. Bergstrom, Ed.         ||        phil@nesser.com, andreas.bergstrom@hiof.no 
  RFC3797          ||      D. Eastlake 3rd         ||       Donald.Eastlake@motorola.com
  RFC3798          ||      T. Hansen, Ed., G. Vaudreuil, Ed.         ||       GregV@ieee.org
  RFC3801          ||       G. Vaudreuil, G. Parsons         ||        gregv@ieee.org, GParsons@NortelNetworks.com 
  RFC3802          ||       G. Vaudreuil, G. Parsons         ||        gregv@ieee.org, gparsons@nortelnetworks.com 
  RFC3803          ||       G. Vaudreuil, G. Parsons         ||        gregv@ieee.org, gparsons@nortelnetworks.com 
  RFC3804          ||       G. Parsons         ||        gparsons@nortelnetworks.com 
  RFC3805          ||      R. Bergman, H. Lewis, I. McDonald         ||       Ron.Bergman@hitachi-ps.us, harryl@us.ibm.com, imcdonald@sharplabs.com
  RFC3806          ||       R. Bergman, H. Lewis, I. McDonald         ||        Ron.Bergman@hitachi-ps.us, harryl@us.ibm.com, imcdonald@sharplabs.com 
  RFC3807          ||       E. Weilandt, N. Khanchandani, S. Rao         ||        eva.weilandt@temic.com, rsanjay@nortelnetworks.com, neerajk@nortelnetworks.com 
  RFC3808          ||       I. McDonald         ||        imcdonald@sharplabs.com, iana@iana.org 
  RFC3809          ||       A. Nagarajan, Ed.         ||         
  RFC3810          ||       R. Vida, Ed., L. Costa, Ed.         ||        Rolland.Vida@lip6.fr, Luis.Costa@lip6.fr, Serge.Fdida@lip6.fr, deering@cisco.com, fenner@research.att.com, kouvelas@cisco.com, brian@innovationslab.net 
  RFC3811          ||      T. Nadeau, Ed., J. Cucchiara, Ed.         ||       tnadeau@cisco.com, jcucchiara@mindspring.com
  RFC3812          ||       C. Srinivasan, A. Viswanathan, T. Nadeau         ||        cheenu@bloomberg.net, arunv@force10networks.com, tnadeau@cisco.com 
  RFC3813          ||       C. Srinivasan, A. Viswanathan, T. Nadeau         ||        cheenu@bloomberg.net, arunv@force10networks.com, tnadeau@cisco.com 
  RFC3814          ||       T. Nadeau, C. Srinivasan, A. Viswanathan         ||        tnadeau@cisco.com, cheenu@bloomberg.net, arunv@force10networks.com 
  RFC3815          ||       J. Cucchiara, H. Sjostrand, J. Luciani         ||        james_luciani@mindspring.com, hans@ipunplugged.com, jcucchiara@mindspring.com 
  RFC3816          ||       J. Quittek, M. Stiemerling, H. Hartenstein         ||        quittek@netlab.nec.de, stiemerling@netlab.nec.de, hartenstein@rz.uni-karlsruhe.de 
  RFC3817          ||       W. Townsley, R. da Silva         ||        mark@townsley.net, rdasilva@va.rr.com 
  RFC3818          ||       V. Schryver         ||        vjs@rhyolite.com 
  RFC3819          ||       P. Karn, Ed., C. Bormann, G. Fairhurst, D. Grossman, R. Ludwig, J. Mahdavi, G. Montenegro, J. Touch, L. Wood         ||        karn@qualcomm.com, cabo@tzi.org, gorry@erg.abdn.ac.uk, Dan.Grossman@motorola.com, Reiner.Ludwig@ericsson.com, jmahdavi@earthlink.net, gab@sun.com, touch@isi.edu, lwood@cisco.com 
  RFC3820          ||       S. Tuecke, V. Welch, D. Engert, L. Pearlman, M. Thompson         ||        tuecke@mcs.anl.gov, vwelch@ncsa.uiuc.edu, deengert@anl.gov, laura@isi.edu, mrthompson@lbl.gov 
  RFC3821          ||      M. Rajagopal, E. Rodriguez, R. Weber         ||       
  RFC3822          ||      D. Peterson         ||       dap@cnt.com
  RFC3823          ||       B. Kovitz         ||        bkovitz@caltech.edu 
  RFC3824          ||       J. Peterson, H. Liu, J. Yu, B. Campbell         ||        jon.peterson@neustar.biz, hong.liu@neustar.biz, james.yu@neustar.biz, bcampbell@dynamicsoft.com 
  RFC3825          ||      J. Polk, J. Schnizlein, M. Linsner         ||       jmpolk@cisco.com, john.schnizlein@cisco.com, marc.linsner@cisco.com
  RFC3826          ||       U. Blumenthal, F. Maino, K. McCloghrie         ||        uri@bell-labs.com, fmaino@andiamo.com, kzm@cisco.com 
  RFC3827          ||       K. Sarcar         ||        kanoj.sarcar@sun.com 
  RFC3828          ||      L-A. Larzon, M. Degermark, S. Pink, L-E. Jonsson, Ed., G. Fairhurst, Ed.         ||       lln@csee.ltu.se, micke@cs.arizona.edu, steve@cs.arizona.edu, lars-erik.jonsson@ericsson.com, gorry@erg.abdn.ac.uk
  RFC3829          ||       R. Weltman, M. Smith, M. Wahl         ||        robw@worldspot.com, mcs@pearlcrescent.com 
  RFC3830          ||      J. Arkko, E. Carrara, F. Lindholm, M. Naslund, K. Norrman         ||       jari.arkko@ericsson.com, elisabetta.carrara@ericsson.com, fredrik.lindholm@ericsson.com, mats.naslund@ericsson.com, karl.norrman@ericsson.com
  RFC3831          ||      C. DeSanti         ||       cds@cisco.com
  RFC3832          ||       W. Zhao, H. Schulzrinne, E. Guttman, C. Bisdikian, W. Jerome         ||        zwb@cs.columbia.edu, hgs@cs.columbia.edu, Erik.Guttman@sun.com, bisdik@us.ibm.com, wfj@us.ibm.com 
  RFC3833          ||       D. Atkins, R. Austein         ||        derek@ihtfp.com, sra@isc.org 
  RFC3834          ||      K. Moore         ||       moore@cs.utk.edu
  RFC3835          ||       A. Barbir, R. Penno, R. Chen, M. Hofmann, H. Orman         ||        abbieb@nortelnetworks.com, chen@research.att.com, hofmann@bell-labs.com, ho@alum.mit.edu, rpenno@nortelnetworks.com 
  RFC3836          ||       A. Beck, M. Hofmann, H. Orman, R. Penno, A. Terzis         ||        abeck@bell-labs.com, hofmann@bell-labs.com, ho@alum.mit.edu, rpenno@nortelnetworks.com, terzis@cs.jhu.edu 
  RFC3837          ||       A. Barbir, O. Batuner, B. Srinivas, M. Hofmann, H. Orman         ||        abbieb@nortelnetworks.com, batuner@attbi.com, bindignavile.srinivas@nokia.com, hofmann@bell-labs.com, ho@alum.mit.edu 
  RFC3838          ||       A. Barbir, O. Batuner, A. Beck, T. Chan, H. Orman         ||        abbieb@nortelnetworks.com, batuner@attbi.com, abeck@bell-labs.com, Tat.Chan@nokia.com, ho@alum.mit.edu 
  RFC3839          ||      R. Castagno, D. Singer         ||       
  RFC3840          ||       J. Rosenberg, H. Schulzrinne, P. Kyzivat         ||        jdrosen@dynamicsoft.com, schulzrinne@cs.columbia.edu, pkyzivat@cisco.com 
  RFC3841          ||       J. Rosenberg, H. Schulzrinne, P. Kyzivat         ||        jdrosen@dynamicsoft.com, schulzrinne@cs.columbia.edu, pkyzivat@cisco.com 
  RFC3842          ||       R. Mahy         ||        rohan@cisco.com 
  RFC3843          ||       L-E. Jonsson, G. Pelletier         ||        lars-erik.jonsson@ericsson.com, ghyslain.pelletier@ericsson.com 
  RFC3844          ||      E. Davies, Ed., J. Hofmann, Ed.         ||       elwynd@nortelnetworks.com, jeanette@wz-berlin.de
  RFC3845          ||       J. Schlyter, Ed.         ||        jakob@nic.se 
  RFC3846          ||      F. Johansson, T. Johansson         ||       fredrik@ipunplugged.com, tony.johansson@bytemobile.com
  RFC3847          ||      M. Shand, L. Ginsberg         ||       mshand@cisco.com, ginsberg@cisco.com
  RFC3848          ||      C. Newman         ||       chris.newman@sun.com
  RFC3849          ||      G. Huston, A. Lord, P. Smith         ||       gih@apnic.net, anne@apnic.net, pfs@cisco.com
  RFC3850          ||      B. Ramsdell, Ed.         ||       
  RFC3851          ||      B. Ramsdell, Ed.         ||       
  RFC3852          ||      R. Housley         ||       housley@vigilsec.com
  RFC3853          ||       J. Peterson         ||        jon.peterson@neustar.biz 
  RFC3854          ||       P. Hoffman, C. Bonatti, A. Eggen         ||         
  RFC3855          ||       P. Hoffman, C. Bonatti         ||        phoffman@imc.org, bonattic@ieca.com 
  RFC3856          ||       J. Rosenberg         ||        jdrosen@dynamicsoft.com 
  RFC3857          ||       J. Rosenberg         ||        jdrosen@dynamicsoft.com 
  RFC3858          ||       J. Rosenberg         ||        jdrosen@dynamicsoft.com 
  RFC3859          ||       J. Peterson         ||        jon.peterson@neustar.biz 
  RFC3860          ||       J. Peterson         ||        jon.peterson@neustar.biz 
  RFC3861          ||       J. Peterson         ||        jon.peterson@neustar.biz 
  RFC3862          ||       G. Klyne, D. Atkins         ||        GK-IETF@ninebynine.org, derek@ihtfp.com 
  RFC3863          ||       H. Sugano, S. Fujimoto, G. Klyne, A. Bateman, W. Carr, J. Peterson         ||        sugano.h@jp.fujitsu.com, shingo_fujimoto@jp.fujitsu.com, GK@ninebynine.org, bateman@acm.org, wayne.carr@intel.com, jon.peterson@neustar.biz 
  RFC3864          ||       G. Klyne, M. Nottingham, J. Mogul         ||        GK-IETF@ninebynine.org, mnot@pobox.com, JeffMogul@acm.org 
  RFC3865          ||       C. Malamud         ||        carl@media.org 
  RFC3866          ||       K. Zeilenga, Ed.         ||         
  RFC3867          ||       Y. Kawatsura, M. Hiroya, H. Beykirch         ||        ykawatsu@itg.hitachi.co.jp, hiroya@st.rim.or.jp, hbbeykirch@web.de 
  RFC3868          ||       J. Loughney, Ed., G. Sidebottom, L. Coene, G. Verwimp, J. Keller, B. Bidulock         ||        john.Loughney@nokia.com, greg@signatustechnologies.com, lode.coene@siemens.com, gery.verwimp@siemens.com, joe.keller@tekelec.com, bidulock@openss7.org 
  RFC3869          ||       R. Atkinson, Ed., S. Floyd, Ed., Internet Architecture Board         ||        iab@iab.org, iab@iab.org, iab@iab.org 
  RFC3870          ||       A. Swartz         ||        me@aaronsw.com 
  RFC3871          ||       G. Jones, Ed.         ||        gmj3871@pobox.com 
  RFC3872          ||       D. Zinman, D. Walker, J. Jiang         ||        dzinman@rogers.com, david.walker@sedna-wireless.com, jjiang@syndesis.com 
  RFC3873          ||       J. Pastor, M. Belinchon         ||        J.Javier.Pastor@ericsson.com, maria.carmen.belinchon@ericsson.com 
  RFC3874          ||       R. Housley         ||        housley@vigilsec.com 
  RFC3875          ||       D. Robinson, K. Coar         ||        drtr@apache.org, coar@apache.org 
  RFC3876          ||       D. Chadwick, S. Mullan         ||        d.w.chadwick@salford.ac.uk, sean.mullan@sun.com 
  RFC3877          ||       S. Chisholm, D. Romascanu         ||        schishol@nortelnetworks.com, dromasca@gmail.com  
  RFC3878          ||       H. Lam, A. Huynh, D. Perkins         ||        hklam@lucent.com, a_n_huynh@yahoo.com, dperkins@snmpinfo.com 
  RFC3879          ||       C. Huitema, B. Carpenter         ||        huitema@microsoft.com, brc@zurich.ibm.com 
  RFC3880          ||       J. Lennox, X. Wu, H. Schulzrinne         ||        lennox@cs.columbia.edu, xiaotaow@cs.columbia.edu, schulzrinne@cs.columbia.edu 
  RFC3881          ||       G. Marshall         ||        glen.f.marshall@siemens.com 
  RFC3882          ||       D. Turk         ||        doughan.turk@bell.ca 
  RFC3883          ||       S. Rao, A. Zinin, A. Roy         ||        siraprao@hotmail.com, zinin@psg.com, akr@cisco.com 
  RFC3884          ||      J. Touch, L. Eggert, Y. Wang         ||       touch@isi.edu, lars.eggert@netlab.nec.de, yushunwa@isi.edu
  RFC3885          ||       E. Allman, T. Hansen         ||        eric@Sendmail.COM, tony+msgtrk@maillennium.att.com 
  RFC3886          ||       E. Allman         ||        eric@Sendmail.COM 
  RFC3887          ||       T. Hansen         ||        tony+msgtrk@maillennium.att.com 
  RFC3888          ||       T. Hansen         ||        tony+msgtrk@maillennium.att.com 
  RFC3889          ||               ||       
  RFC3890          ||       M. Westerlund         ||        Magnus.Westerlund@ericsson.com 
  RFC3891          ||       R. Mahy, B. Biggs, R. Dean         ||        rohan@cisco.com, bbiggs@dumbterm.net, rfc@fdd.com 
  RFC3892          ||       R. Sparks         ||        RjS@xten.com 
  RFC3893          ||       J. Peterson         ||        jon.peterson@neustar.biz 
  RFC3894          ||       J. Degener         ||        jutta@sendmail.com 
  RFC3895          ||      O. Nicklass, Ed.         ||       orly_n@rad.com
  RFC3896          ||       O. Nicklass, Ed.         ||        orly_n@rad.com 
  RFC3897          ||       A. Barbir         ||        abbieb@nortelnetworks.com 
  RFC3898          ||       V. Kalusivalingam         ||        vibhaska@cisco.com 
  RFC3901          ||       A. Durand, J. Ihren         ||        Alain.Durand@sun.com, johani@autonomica.se 
  RFC3902          ||       M. Baker, M. Nottingham         ||        distobj@acm.org, mnot@pobox.com 
  RFC3903          ||       A. Niemi, Ed.         ||        aki.niemi@nokia.com 
  RFC3904          ||       C. Huitema, R. Austein, S. Satapati, R. van der Pol         ||        huitema@microsoft.com, sra@isc.org, satapati@cisco.com, Ronald.vanderPol@nlnetlabs.nl 
  RFC3905          ||       V. See, Ed.         ||        vsee@microsoft.com 
  RFC3906          ||       N. Shen, H. Smit         ||        naiming@redback.com, hhwsmit@xs4all.nl 
  RFC3909          ||       K. Zeilenga         ||        Kurt@OpenLDAP.org 
  RFC3910          ||      V. Gurbani, Ed., A. Brusilovsky, I. Faynberg, J. Gato, H. Lu, M. Unmehopa         ||       vkg@lucent.com, abrusilovsky@lucent.com, faynberg@lucent.com, jorge.gato@vodafone.com, huilanlu@lucent.com, unmehopa@lucent.com
  RFC3911          ||       R. Mahy, D. Petrie         ||        rohan@airespace.com, dpetrie@pingtel.com 
  RFC3912          ||       L. Daigle         ||        leslie@verisignlabs.com 
  RFC3913          ||      D. Thaler         ||       dthaler@microsoft.com
  RFC3914          ||       A. Barbir, A. Rousskov         ||        abbieb@nortelnetworks.com, rousskov@measurement-factory.com 
  RFC3915          ||       S. Hollenbeck         ||        shollenbeck@verisign.com 
  RFC3916          ||       X. Xiao, Ed., D. McPherson, Ed., P. Pate, Ed.         ||        xxiao@riverstonenet.com, danny@arbor.net, prayson.pate@overturenetworks.com 
  RFC3917          ||       J. Quittek, T. Zseby, B. Claise, S. Zander         ||        quittek@netlab.nec.de, zseby@fokus.fhg.de, bclaise@cisco.com, szander@swin.edu.au 
  RFC3918          ||       D. Stopp, B. Hickman         ||        debby@ixiacom.com, brooks.hickman@spirentcom.com 
  RFC3919          ||       E. Stephan, J. Palet         ||        emile.stephan@francetelecom.com, jordi.palet@consulintel.es 
  RFC3920          ||      P. Saint-Andre, Ed.         ||       ietf@stpeter.im
  RFC3921          ||      P. Saint-Andre, Ed.         ||       ietf@stpeter.im
  RFC3922          ||      P. Saint-Andre         ||       ietf@stpeter.im
  RFC3923          ||       P. Saint-Andre         ||       ietf@stpeter.im
  RFC3924          ||       F. Baker, B. Foster, C. Sharp         ||        fred@cisco.com, bfoster@cisco.com, chsharp@cisco.com 
  RFC3925          ||       J. Littlefield         ||        joshl@cisco.com 
  RFC3926          ||      T. Paila, M. Luby, R. Lehtonen, V. Roca, R. Walsh         ||       toni.paila@nokia.com, luby@digitalfountain.com, rami.lehtonen@teliasonera.com, vincent.roca@inrialpes.fr, rod.walsh@nokia.com
  RFC3927          ||      S. Cheshire, B. Aboba, E. Guttman         ||       rfc@stuartcheshire.org, bernarda@microsoft.com, erik@spybeam.org
  RFC3928          ||       R. Megginson, Ed., M. Smith, O. Natkovich, J. Parham         ||        rmegginson0224@aol.com, olgan@yahoo-inc.com, mcs@pearlcrescent.com, jeffparh@microsoft.com 
  RFC3929          ||       T. Hardie         ||        hardie@qualcomm.com 
  RFC3930          ||       D. Eastlake 3rd         ||        Donald.Eastlake@motorola.com 
  RFC3931          ||      J. Lau, Ed., M. Townsley, Ed., I. Goyret, Ed.         ||       jedlau@cisco.com, mark@townsley.net, igoyret@lucent.com
  RFC3932          ||      H. Alvestrand         ||       harald@alvestrand.no
  RFC3933          ||       J. Klensin, S. Dawkins         ||        john-ietf@jck.com, spencer@mcsr-labs.org 
  RFC3934          ||      M. Wasserman         ||       margaret@thingmagic.com
  RFC3935          ||       H. Alvestrand         ||        harald@alvestrand.no 
  RFC3936          ||       K. Kompella, J. Lang         ||        kireeti@juniper.net, jplang@ieee.org 
  RFC3937          ||       M. Steidl         ||        mdirector@iptc.org 
  RFC3938          ||       T. Hansen         ||        tony+msgctxt@maillennium.att.com 
  RFC3939          ||       G. Parsons, J. Maruszak         ||        gparsons@nortelnetworks.com, jjmaruszak@sympatico.ca 
  RFC3940          ||      B. Adamson, C. Bormann, M. Handley, J. Macker         ||       adamson@itd.nrl.navy.mil, cabo@tzi.org, M.Handley@cs.ucl.ac.uk, macker@itd.nrl.navy.mil
  RFC3941          ||      B. Adamson, C. Bormann, M. Handley, J. Macker         ||       adamson@itd.nrl.navy.mil, cabo@tzi.org, M.Handley@cs.ucl.ac.uk, macker@itd.nrl.navy.mil
  RFC3942          ||      B. Volz         ||       volz@cisco.com
  RFC3943          ||       R. Friend         ||        rfriend@hifn.com 
  RFC3944          ||       T. Johnson, S. Okubo, S. Campos         ||        Tyler_Johnson@unc.edu, sokubo@waseda.jp, simao.campos@itu.int 
  RFC3945          ||      E. Mannie, Ed.         ||       eric_mannie@hotmail.com
  RFC3946          ||       E. Mannie, D. Papadimitriou         ||        eric_mannie@hotmail.com, dimitri.papadimitriou@alcatel.be 
  RFC3947          ||       T. Kivinen, B. Swander, A. Huttunen, V. Volpe         ||        kivinen@safenet-inc.com, Ari.Huttunen@F-Secure.com, briansw@microsoft.com, vvolpe@cisco.com 
  RFC3948          ||       A. Huttunen, B. Swander, V. Volpe, L. DiBurro, M. Stenberg         ||        Ari.Huttunen@F-Secure.com, briansw@microsoft.com, vvolpe@cisco.com, ldiburro@nortelnetworks.com, markus.stenberg@iki.fi 
  RFC3949          ||      R. Buckley, D. Venable, L. McIntyre, G. Parsons, J. Rafferty         ||        rbuckley@crt.xerox.com, dvenable@crt.xerox.com, lloyd10328@pacbell.net, gparsons@nortel.com, jraff@brooktrout.com 
  RFC3950          ||      L. McIntyre, G. Parsons, J. Rafferty         ||        lloyd10328@pacbell.net, gparsons@nortel.com, jraff@brooktrout.com 
  RFC3951          ||       S. Andersen, A. Duric, H. Astrom, R. Hagen, W. Kleijn, J. Linden         ||        sva@kom.auc.dk, alan.duric@telio.no, henrik.astrom@globalipsound.com, roar.hagen@globalipsound.com, bastiaan.kleijn@globalipsound.com, jan.linden@globalipsound.com 
  RFC3952          ||       A. Duric, S. Andersen         ||        alan.duric@telio.no, sva@kom.auc.dk 
  RFC3953          ||      J. Peterson         ||       jon.peterson@neustar.biz
  RFC3954          ||      B. Claise, Ed.         ||       bclaise@cisco.com
  RFC3955          ||       S. Leinen         ||        simon@switch.ch 
  RFC3956          ||      P. Savola, B. Haberman         ||       psavola@funet.fi, brian@innovationslab.net
  RFC3957          ||       C. Perkins, P. Calhoun         ||        charles.perkins@nokia.com, pcalhoun@airespace.com 
  RFC3958          ||       L. Daigle, A. Newton         ||        leslie@thinkingcat.com, anewton@verisignlabs.com 
  RFC3959          ||       G. Camarillo         ||        Gonzalo.Camarillo@ericsson.com 
  RFC3960          ||       G. Camarillo, H. Schulzrinne         ||        Gonzalo.Camarillo@ericsson.com, schulzrinne@cs.columbia.edu 
  RFC3961          ||       K. Raeburn         ||        raeburn@mit.edu 
  RFC3962          ||       K. Raeburn         ||        raeburn@mit.edu 
  RFC3963          ||       V. Devarapalli, R. Wakikawa, A. Petrescu, P. Thubert         ||        vijay.devarapalli@nokia.com, ryuji@sfc.wide.ad.jp, Alexandru.Petrescu@motorola.com, pthubert@cisco.com 
  RFC3964          ||       P. Savola, C. Patel         ||        psavola@funet.fi, chirayu@chirayu.org 
  RFC3965          ||      K. Toyoda, H. Ohno, J. Murai, D. Wing         ||       toyoda.kiyoshi@jp.panasonic.com, hohno@ohnolab.org, jun@wide.ad.jp, dwing-ietf@fuggles.com
  RFC3966          ||      H. Schulzrinne         ||       hgs@cs.columbia.edu
  RFC3967          ||      R. Bush, T. Narten         ||       randy@psg.com, narten@us.ibm.com
  RFC3968          ||       G. Camarillo         ||        Gonzalo.Camarillo@ericsson.com 
  RFC3969          ||      G. Camarillo         ||       Gonzalo.Camarillo@ericsson.com
  RFC3970          ||      K. Kompella         ||       kireeti@juniper.net
  RFC3971          ||      J. Arkko, Ed., J. Kempf, B. Zill, P. Nikander         ||       jari.arkko@ericsson.com, kempf@docomolabs-usa.com, bzill@microsoft.com, Pekka.Nikander@nomadiclab.com
  RFC3972          ||      T. Aura         ||       tuomaura@microsoft.com
  RFC3973          ||       A. Adams, J. Nicholas, W. Siadak         ||        ala@nexthop.com, jonathan.nicholas@itt.com, wfs@nexthop.com 
  RFC3974          ||      M. Nakamura, J. Hagino         ||       motonori@media.kyoto-u.ac.jp, itojun@iijlab.net
  RFC3975          ||       G. Huston, Ed., I. Leuca, Ed.         ||        execd@iab.org, ileana.leuca@Cingular.com 
  RFC3976          ||       V. K. Gurbani, F. Haerens, V. Rastogi         ||        vkg@lucent.com, frans.haerens@alcatel.be, vidhi.rastogi@wipro.com 
  RFC3977          ||      C. Feather         ||       clive@davros.org
  RFC3978          ||       S. Bradner, Ed.         ||        sob@harvard.edu 
  RFC3979          ||      S. Bradner, Ed.         ||       sob@harvard.edu
  RFC3980          ||      M. Krueger, M. Chadalapaka, R. Elliott         ||       marjorie_krueger@hp.com, cbm@rose.hp.com, elliott@hp.com
  RFC3981          ||      A. Newton, M. Sanz         ||       anewton@verisignlabs.com, sanz@denic.de
  RFC3982          ||       A. Newton, M. Sanz         ||        anewton@verisignlabs.com, sanz@denic.de 
  RFC3983          ||       A. Newton, M. Sanz         ||        anewton@verisignlabs.com, sanz@denic.de 
  RFC3984          ||      S. Wenger, M.M. Hannuksela, T. Stockhammer, M. Westerlund, D. Singer         ||       stewe@stewe.org, miska.hannuksela@nokia.com, stockhammer@nomor.de, magnus.westerlund@ericsson.com, singer@apple.com
  RFC3985          ||      S. Bryant, Ed., P. Pate, Ed.         ||       stbryant@cisco.com, prayson.pate@overturenetworks.com
  RFC3986          ||      T. Berners-Lee, R. Fielding, L. Masinter         ||       timbl@w3.org, fielding@gbiv.com, LMM@acm.org
  RFC3987          ||      M. Duerst, M. Suignard         ||       duerst@w3.org, michelsu@microsoft.com
  RFC3988          ||       B. Black, K. Kompella         ||        ben@layer8.net, kireeti@juniper.net 
  RFC3989          ||      M. Stiemerling, J. Quittek, T. Taylor         ||       stiemerling@netlab.nec.de, quittek@netlab.nec.de, tom.taylor.stds@gmail.com
  RFC3990          ||       B. O'Hara, P. Calhoun, J. Kempf         ||        bob@airespace.com, pcalhoun@airespace.com, kempf@docomolabs-usa.com 
  RFC3991          ||       B. Foster, F. Andreasen         ||        bfoster@cisco.com, fandreas@cisco.com 
  RFC3992          ||       B. Foster, F. Andreasen         ||        bfoster@cisco.com, fandreas@cisco.com 
  RFC3993          ||       R. Johnson, T. Palaniappan, M. Stapp         ||        raj@cisco.com, athenmoz@cisco.com, mjs@cisco.com 
  RFC3994          ||       H. Schulzrinne         ||        hgs@cs.columbia.edu 
  RFC3995          ||       R. Herriot, T. Hastings         ||       bob@herriot.com, tom.hastings@alum.mit.edu
  RFC3996          ||      R. Herriot, T. Hastings, H. Lewis         ||       bob@herriot.com, tom.hastings@alum.mit.edu, harryl@us.ibm.com
  RFC3997          ||      T. Hastings, Ed., R. K. deBry, H. Lewis         ||       tom.hastings@alum.mit.edu, debryro@uvsc.edu, harryl@us.ibm.com
  RFC3998          ||      C. Kugler, H. Lewis, T. Hastings, Ed.         ||       kugler@us.ibm.com, harryl@us.ibm.com, tom.hastings@alum.mit.edu
  RFC4001          ||       M. Daniele, B. Haberman, S. Routhier, J. Schoenwaelder         ||       michael.daniele@syamsoftware.com, brian@innovationslab.net, shawn.routhier@windriver.com, j.schoenwaelder@iu-bremen.de
  RFC4002          ||      R. Brandner, L. Conroy, R. Stastny         ||       rudolf.brandner@siemens.com, lwc@roke.co.uk, richard.stastny@oefeg.at
  RFC4003          ||      L. Berger         ||       lberger@movaz.com
  RFC4004          ||      P. Calhoun, T. Johansson, C. Perkins, T. Hiller, Ed., P. McCann         ||       pcalhoun@cisco.com, tony.johansson@bytemobile.com, Charles.Perkins@nokia.com, tomhiller@lucent.com, mccap@lucent.com
  RFC4005          ||      P. Calhoun, G. Zorn, D. Spence, D. Mitton         ||       pcalhoun@cisco.com, gwz@cisco.com, dspence@computer.org, dmitton@circularnetworks.com
  RFC4006          ||      H. Hakala, L. Mattila, J-P. Koskinen, M. Stura, J. Loughney         ||       Harri.Hakala@ericsson.com, Leena.Mattila@ericsson.com, juha-pekka.koskinen@nokia.com, marco.stura@nokia.com, John.Loughney@nokia.com
  RFC4007          ||      S. Deering, B. Haberman, T. Jinmei, E. Nordmark, B. Zill         ||       none, brian@innovationslab.net, jinmei@isl.rdc.toshiba.co.jp, Erik.Nordmark@sun.com, bzill@microsoft.com
  RFC4008          ||      R. Rohit, P. Srisuresh, R. Raghunarayan, N. Pai, C. Wang         ||       rrohit74@hotmail.com, srisuresh@yahoo.com, raraghun@cisco.com, npai@cisco.com, cliffwang2000@yahoo.com
  RFC4009          ||       J. Park, S. Lee, J. Kim, J. Lee         ||       khopri@kisa.or.kr, sjlee@kisa.or.kr, jykim@kisa.or.kr, jilee@kisa.or.kr
  RFC4010          ||       J. Park, S. Lee, J. Kim, J. Lee         ||       khopri@kisa.or.kr, sjlee@kisa.or.kr, jykim@kisa.or.kr, jilee@kisa.or.kr
  RFC4011          ||      S. Waldbusser, J. Saperia, T. Hongal         ||       waldbusser@nextbeacon.com, saperia@jdscons.com, hongal@riverstonenet.com
  RFC4012          ||      L. Blunk, J. Damas, F. Parent, A. Robachevsky         ||       ljb@merit.edu, Joao_Damas@isc.org, Florent.Parent@hexago.com, andrei@ripe.net
  RFC4013          ||      K. Zeilenga         ||       Kurt@OpenLDAP.org
  RFC4014          ||      R. Droms, J. Schnizlein         ||       rdroms@cisco.com, jschnizl@cisco.com
  RFC4015          ||       R. Ludwig, A. Gurtov         ||       Reiner.Ludwig@ericsson.com, andrei.gurtov@cs.helsinki.fi
  RFC4016          ||      M. Parthasarathy         ||       mohanp@sbcglobal.net
  RFC4017          ||       D. Stanley, J. Walker, B. Aboba         ||       dstanley@agere.com, jesse.walker@intel.com, bernarda@microsoft.com
  RFC4018          ||      M. Bakke, J. Hufferd, K. Voruganti, M. Krueger, T. Sperry         ||       mbakke@cisco.com, jlhufferd@comcast.net, kaladhar@us.ibm.com, marjorie_krueger@hp.com, todd_sperry@adaptec.com
  RFC4019          ||      G. Pelletier         ||       ghyslain.pelletier@ericsson.com
  RFC4020          ||      K. Kompella, A. Zinin         ||       kireeti@juniper.net, zinin@psg.com
  RFC4021          ||      G. Klyne, J. Palme         ||       GK-IETF@ninebynine.org, jpalme@dsv.su.se
  RFC4022          ||       R. Raghunarayan, Ed.         ||       raraghun@cisco.com
  RFC4023          ||      T. Worster, Y. Rekhter, E. Rosen, Ed.         ||       tom.worster@motorola.com, yakov@juniper.net, erosen@cisco.com
  RFC4024          ||      G. Parsons, J. Maruszak         ||       gparsons@nortel.com, jjmaruszak@sympatico.ca
  RFC4025          ||      M. Richardson         ||       mcr@sandelman.ottawa.on.ca
  RFC4026          ||       L. Andersson, T. Madsen         ||       loa@pi.se, tove.madsen@acreo.se
  RFC4027          ||      S. Josefsson         ||       simon@josefsson.org
  RFC4028          ||      S. Donovan, J. Rosenberg         ||       srd@cisco.com, jdrosen@cisco.com
  RFC4029          ||      M. Lind, V. Ksinant, S. Park, A. Baudot, P. Savola         ||       mikael.lind@teliasonera.com, vladimir.ksinant@fr.thalesgroup.com, soohong.park@samsung.com, alain.baudot@francetelecom.com, psavola@funet.fi
  RFC4030          ||      M. Stapp, T. Lemon         ||       mjs@cisco.com, Ted.Lemon@nominum.com
  RFC4031          ||      M. Carugi, Ed., D. McDysan, Ed.         ||       marco.carugi@nortel.com, dave.mcdysan@mci.com
  RFC4032          ||       G. Camarillo, P. Kyzivat         ||       Gonzalo.Camarillo@ericsson.com, pkyzivat@cisco.com
  RFC4033          ||      R. Arends, R. Austein, M. Larson, D. Massey, S. Rose         ||       roy.arends@telin.nl, sra@isc.org, mlarson@verisign.com, massey@cs.colostate.edu, scott.rose@nist.gov
  RFC4034          ||      R. Arends, R. Austein, M. Larson, D. Massey, S. Rose         ||       roy.arends@telin.nl, sra@isc.org, mlarson@verisign.com, massey@cs.colostate.edu, scott.rose@nist.gov
  RFC4035          ||      R. Arends, R. Austein, M. Larson, D. Massey, S. Rose         ||       roy.arends@telin.nl, sra@isc.org, mlarson@verisign.com, massey@cs.colostate.edu, scott.rose@nist.gov
  RFC4036          ||      W. Sawyer         ||       wsawyer@ieee.org
  RFC4037          ||       A. Rousskov         ||       rousskov@measurement-factory.com
  RFC4038          ||       M-K. Shin, Ed., Y-G. Hong, J. Hagino, P. Savola, E. M. Castro         ||       mshin@nist.gov, yghong@pec.etri.re.kr, itojun@iijlab.net, psavola@funet.fi, eva@gsyc.escet.urjc.es
  RFC4039          ||       S. Park, P. Kim, B. Volz         ||       soohong.park@samsung.com, kimps@samsung.com, volz@cisco.com
  RFC4040          ||      R. Kreuter         ||       ruediger.kreuter@siemens.com
  RFC4041          ||      A. Farrel         ||       adrian@olddog.co.uk
  RFC4042          ||      M. Crispin         ||       UTF9@Lingling.Panda.COM
  RFC4043          ||      D. Pinkas, T. Gindin         ||       Denis.Pinkas@bull.net, tgindin@us.ibm.com
  RFC4044          ||      K. McCloghrie         ||       kzm@cisco.com
  RFC4045          ||      G. Bourdon         ||       gilles.bourdon@francetelecom.com
  RFC4046          ||      M. Baugher, R. Canetti, L. Dondeti, F. Lindholm         ||       mbaugher@cisco.com, canetti@watson.ibm.com, ldondeti@qualcomm.com, fredrik.lindholm@ericsson.com
  RFC4047          ||      S. Allen, D. Wells         ||       sla@ucolick.org, dwells@nrao.edu
  RFC4048          ||      B. Carpenter         ||       brc@zurich.ibm.com
  RFC4049          ||      R. Housley         ||       housley@vigilsec.com
  RFC4050          ||      S. Blake-Wilson, G. Karlinger, T. Kobayashi, Y. Wang         ||       sblakewilson@bcisse.com, gregor.karlinger@cio.gv.at, kotetsu@isl.ntt.co.jp, yonwang@uncc.edu
  RFC4051          ||      D. Eastlake 3rd         ||       Donald.Eastlake@motorola.com
  RFC4052          ||      L. Daigle, Ed., Internet Architecture Board         ||       iab@iab.org, iab@iab.org
  RFC4053          ||      S. Trowbridge, S. Bradner, F. Baker         ||       sjtrowbridge@lucent.com, sob@harvard.edu, fred@cisco.com
  RFC4054          ||      J. Strand, Ed.,  A. Chiu, Ed.         ||       jls@research.att.com, chiu@research.att.com
  RFC4055          ||      J. Schaad, B. Kaliski, R. Housley         ||       jimsch@exmsft.com, bkaliski@rsasecurity.com, housley@vigilsec.com
  RFC4056          ||      J. Schaad         ||       jimsch@exmsft.com
  RFC4057          ||      J. Bound, Ed.         ||       jim.bound@hp.com
  RFC4058          ||      A. Yegin, Ed., Y. Ohba, R. Penno, G. Tsirtsis, C. Wang         ||       alper.yegin@samsung.com, yohba@tari.toshiba.com, rpenno@juniper.net, G.Tsirtsis@Flarion.com, cliffwangmail@yahoo.com
  RFC4059          ||      D. Linsenbardt, S. Pontius, A. Sturgeon         ||       dlinsenbardt@spyrus.com, spontius@spyrus.com, asturgeon@spyrus.com
  RFC4060          ||      Q. Xie, D. Pearce         ||       qxie1@email.mot.com, bdp003@motorola.com
  RFC4061          ||      V. Manral, R. White, A. Shaikh         ||       vishwas@sinett.com, riw@cisco.com, ashaikh@research.att.com
  RFC4062          ||      V. Manral, R. White, A. Shaikh         ||       vishwas@sinett.com, riw@cisco.com, ashaikh@research.att.com
  RFC4063          ||      V. Manral, R. White, A. Shaikh         ||       vishwas@sinett.com, riw@cisco.com, ashaikh@research.att.com
  RFC4064          ||      A. Patel, K. Leung         ||       alpesh@cisco.com, kleung@cisco.com
  RFC4065          ||      J. Kempf         ||       kempf@docomolabs-usa.com
  RFC4066          ||      M. Liebsch, Ed., A. Singh, Ed., H. Chaskar, D. Funato, E. Shim         ||       marco.liebsch@netlab.nec.de, asingh1@email.mot.com, hemant.chaskar@airtightnetworks.net, funato@mlab.yrp.nttdocomo.co.jp, eunsoo@research.panasonic.com
  RFC4067          ||      J. Loughney, Ed., M. Nakhjiri, C. Perkins, R. Koodli         ||       john.loughney@nokia.com, madjid.nakhjiri@motorola.com, charles.perkins@.nokia.com, rajeev.koodli@nokia.com
  RFC4068          ||      R. Koodli, Ed.         ||       Rajeev.Koodli@nokia.com
  RFC4069          ||      M. Dodge, B. Ray         ||       mbdodge@ieee.org, rray@pesa.com
  RFC4070          ||      M. Dodge, B. Ray         ||       mbdodge@ieee.org, rray@pesa.com
  RFC4071          ||      R. Austein, Ed., B. Wijnen, Ed.         ||       sra@isc.org, bwijnen@lucent.com
  RFC4072          ||      P. Eronen, Ed., T. Hiller, G. Zorn         ||       pe@iki.fi, tomhiller@lucent.com, gwz@cisco.com
  RFC4073          ||      R. Housley         ||       housley@vigilsec.com
  RFC4074          ||      Y. Morishita, T. Jinmei         ||       yasuhiro@jprs.co.jp, jinmei@isl.rdc.toshiba.co.jp
  RFC4075          ||      V. Kalusivalingam         ||       vibhaska@cisco.com
  RFC4076          ||      T. Chown, S. Venaas, A. Vijayabhaskar         ||       tjc@ecs.soton.ac.uk, venaas@uninett.no, vibhaska@cisco.com
  RFC4077          ||      A.B. Roach         ||       adam@estacado.net
  RFC4078          ||      N. Earnshaw, S. Aoki, A. Ashley, W. Kameyama         ||       nigel.earnshaw@rd.bbc.co.uk, shig@center.jfn.co.jp, aashley@ndsuk.com, wataru@waseda.jp
  RFC4079          ||      J. Peterson         ||       jon.peterson@neustar.biz
  RFC4080          ||      R. Hancock, G. Karagiannis, J. Loughney, S. Van den Bosch         ||       robert.hancock@roke.co.uk, g.karagiannis@ewi.utwente.nl, john.loughney@nokia.com, sven.van_den_bosch@alcatel.be
  RFC4081          ||      H. Tschofenig, D. Kroeselberg         ||       Hannes.Tschofenig@siemens.com, Dirk.Kroeselberg@siemens.com
  RFC4082          ||      A. Perrig, D. Song, R. Canetti, J. D. Tygar, B. Briscoe         ||       perrig@cmu.edu, dawnsong@cmu.edu, canetti@watson.ibm.com, doug.tygar@gmail.com, bob.briscoe@bt.com
  RFC4083          ||      M. Garcia-Martin         ||       miguel.an.garcia@nokia.com
  RFC4084          ||      J. Klensin         ||       john-ietf@jck.com
  RFC4085          ||      D. Plonka         ||       plonka@doit.wisc.edu
  RFC4086          ||      D. Eastlake 3rd, J. Schiller, S. Crocker         ||       Donald.Eastlake@motorola.com, jis@mit.edu, steve@stevecrocker.com
  RFC4087          ||      D. Thaler         ||       dthaler@microsoft.com
  RFC4088          ||      D. Black, K. McCloghrie, J. Schoenwaelder         ||       black_david@emc.com, kzm@cisco.com, j.schoenwaelder@iu-bremen.de
  RFC4089          ||      S. Hollenbeck, Ed., IAB and IESG         ||       sah@428cobrajet.net, none, none
  RFC4090          ||      P. Pan, Ed., G. Swallow, Ed., A. Atlas, Ed.         ||       ppan@hammerheadsystems.com, swallow@cisco.com, aatlas@avici.com
  RFC4091          ||      G. Camarillo, J. Rosenberg         ||       Gonzalo.Camarillo@ericsson.com, jdrosen@cisco.com
  RFC4092          ||      G. Camarillo, J. Rosenberg         ||       Gonzalo.Camarillo@ericsson.com, jdrosen@cisco.com
  RFC4093          ||      F. Adrangi, Ed., H. Levkowetz, Ed.         ||       farid.adrangi@intel.com, henrik@levkowetz.com
  RFC4094          ||      J. Manner, X. Fu         ||       jmanner@cs.helsinki.fi, fu@cs.uni-goettingen.de
  RFC4095          ||      C. Malamud         ||       carl@media.org
  RFC4096          ||      C. Malamud         ||       carl@media.org
  RFC4097          ||      M. Barnes, Ed.         ||       mary.barnes@nortel.com
  RFC4098          ||      H. Berkowitz, E. Davies, Ed., S. Hares, P. Krishnaswamy, M. Lepp         ||       hcb@gettcomm.com, elwynd@dial.pipex.com, skh@nexthop.com, padma.krishnaswamy@saic.com, mlepp@lepp.com
  RFC4101          ||      E. Rescorla, IAB         ||       ekr@rtfm.com, iab@iab.org
  RFC4102          ||      P. Jones         ||       paulej@packetizer.com
  RFC4103          ||      G. Hellstrom, P. Jones         ||       gunnar.hellstrom@omnitor.se, paulej@packetizer.com
  RFC4104          ||      M. Pana, Ed., A. Reyes, A. Barba, D. Moron, M. Brunner         ||       mpana@metasolv.com, mreyes@ac.upc.edu, telabm@mat.upc.es, dmor4477@hotmail.com, brunner@netlab.nec.de
  RFC4105          ||      J.-L. Le Roux, Ed., J.-P. Vasseur, Ed., J. Boyle, Ed.         ||       jeanlouis.leroux@francetelecom.com, jpv@cisco.com, jboyle@pdnets.com
  RFC4106          ||      J. Viega, D. McGrew         ||       viega@securesoftware.com, mcgrew@cisco.com
  RFC4107          ||      S. Bellovin, R. Housley         ||       bellovin@acm.org, housley@vigilsec.com
  RFC4108          ||      R. Housley         ||       housley@vigilsec.com
  RFC4109          ||      P. Hoffman         ||       paul.hoffman@vpnc.org
  RFC4110          ||      R. Callon, M. Suzuki         ||       rcallon@juniper.net, suzuki.muneyoshi@lab.ntt.co.jp
  RFC4111          ||      L. Fang, Ed.         ||       luyuanfang@att.com
  RFC4112          ||      D. Eastlake 3rd         ||       Donald.Eastlake@motorola.com
  RFC4113          ||      B. Fenner, J. Flick         ||       fenner@research.att.com, john.flick@hp.com
  RFC4114          ||      S. Hollenbeck         ||       shollenbeck@verisign.com
  RFC4115          ||      O. Aboul-Magd, S. Rabie         ||       osama@nortel.com, rabie@nortel.com
  RFC4116          ||      J. Abley, K. Lindqvist, E. Davies, B. Black, V. Gill         ||       jabley@isc.org, kurtis@kurtis.pp.se, elwynd@dial.pipex.com, ben@layer8.net, vgill@vijaygill.com
  RFC4117          ||      G. Camarillo, E. Burger, H. Schulzrinne, A. van Wijk         ||       Gonzalo.Camarillo@ericsson.com, eburger@brooktrout.com, schulzrinne@cs.columbia.edu, a.vwijk@viataal.nl
  RFC4118          ||      L. Yang, P. Zerfos, E. Sadot         ||       lily.l.yang@intel.com, pzerfos@cs.ucla.edu, esadot@avaya.com
  RFC4119          ||      J. Peterson         ||       jon.peterson@neustar.biz
  RFC4120          ||      C. Neuman, T. Yu, S. Hartman, K. Raeburn         ||       bcn@isi.edu, tlyu@mit.edu, hartmans-ietf@mit.edu, raeburn@mit.edu
  RFC4121          ||      L. Zhu, K. Jaganathan, S. Hartman         ||       LZhu@microsoft.com, karthikj@microsoft.com, hartmans-ietf@mit.edu
  RFC4122          ||      P. Leach, M. Mealling, R. Salz         ||       paulle@microsoft.com, michael@refactored-networks.com, rsalz@datapower.com
  RFC4123          ||      H. Schulzrinne, C. Agboh         ||       hgs@cs.columbia.edu, charles.agboh@packetizer.com
  RFC4124          ||      F. Le Faucheur, Ed.         ||       flefauch@cisco.com
  RFC4125          ||      F. Le Faucheur, W. Lai         ||       flefauch@cisco.com, wlai@att.com
  RFC4126          ||      J. Ash         ||       gash@att.com
  RFC4127          ||      F. Le Faucheur, Ed.         ||       flefauch@cisco.com
  RFC4128          ||      W. Lai         ||       wlai@att.com
  RFC4129          ||      R. Mukundan, K. Morneault, N. Mangalpally         ||       ranjith.mukundan@wipro.com, kmorneau@cisco.com, narsim@nortelnetworks.com
  RFC4130          ||      D. Moberg, R. Drummond         ||       dmoberg@cyclonecommerce.com, rvd2@drummondgroup.com
  RFC4131          ||      S. Green, K. Ozawa, E. Cardona, Ed., A. Katsnelson         ||       rubbersoul3@yahoo.com, Kazuyoshi.Ozawa@toshiba.co.jp, katsnelson6@peoplepc.com, e.cardona@cablelabs.com
  RFC4132          ||      S. Moriai, A. Kato, M. Kanda         ||       shiho@rd.scei.sony.co.jp, akato@po.ntts.co.jp, kanda.masayuki@lab.ntt.co.jp
  RFC4133          ||      A. Bierman, K. McCloghrie         ||       andy@yumaworks.com, kzm@cisco.com
  RFC4134          ||      P. Hoffman, Ed.         ||       phoffman@imc.org
  RFC4135          ||      JH. Choi, G. Daley         ||       jinchoe@samsung.com, greg.daley@eng.monash.edu.au
  RFC4136          ||      P. Pillay-Esnault         ||       ppe@cisco.com
  RFC4137          ||      J. Vollbrecht, P. Eronen, N. Petroni, Y. Ohba         ||       jrv@mtghouse.com, pe@iki.fi, npetroni@cs.umd.edu, yohba@tari.toshiba.com
  RFC4138          ||      P. Sarolahti, M. Kojo         ||       pasi.sarolahti@nokia.com, kojo@cs.helsinki.fi
  RFC4139          ||      D. Papadimitriou, J. Drake, J. Ash, A. Farrel, L. Ong         ||       dimitri.papadimitriou@alcatel.be, John.E.Drake2@boeing.com, gash@att.com, adrian@olddog.co.uk, lyong@ciena.com
  RFC4140          ||      H. Soliman, C. Castelluccia, K. El Malki, L. Bellier         ||       h.soliman@flarion.com, claude.castelluccia@inria.fr, karim@elmalki.homeip.net, ludovic.bellier@inria.fr
  RFC4141          ||      K. Toyoda, D. Crocker         ||       toyoda.kiyoshi@jp.panasonic.com, dcrocker@bbiw.net
  RFC4142          ||      D. Crocker, G. Klyne         ||       dcrocker@bbiw.net, GK-IETF@ninebynine.org
  RFC4143          ||      K. Toyoda, D. Crocker         ||       toyoda.kiyoshi@jp.panasonic.com, dcrocker@bbiw.net
  RFC4144          ||      D. Eastlake 3rd         ||       Donald.Eastlake@motorola.com
  RFC4145          ||      D. Yon, G. Camarillo         ||       yon-comedia@rfdsoftware.com, Gonzalo.Camarillo@ericsson.com
  RFC4146          ||      R. Gellens         ||       randy@qualcomm.com
  RFC4147          ||      G. Huston         ||       gih@apnic.net
  RFC4148          ||      E. Stephan         ||       emile.stephan@francetelecom.com
  RFC4149          ||      C. Kalbfleisch, R. Cole, D. Romascanu         ||       ietf@kalbfleisch.us, robert.cole@jhuapl.edu, dromasca@gmail.com 
  RFC4150          ||      R. Dietz, R. Cole         ||       rdietz@hifn.com, robert.cole@jhuapl.edu
  RFC4151          ||      T. Kindberg, S. Hawke         ||       timothy@hpl.hp.com, sandro@w3.org
  RFC4152          ||      K. Tesink, R. Fox         ||       kaj@research.telcordia.com, rfox@telcordia.com
  RFC4153          ||      K. Fujimura, M. Terada, D. Eastlake 3rd         ||       fujimura.ko@lab.ntt.co.jp, te@rex.yrp.nttdocomo.co.jp, Donald.Eastlake@motorola.com
  RFC4154          ||      M. Terada, K. Fujimura         ||       te@rex.yrp.nttdocomo.co.jp, fujimura.ko@lab.ntt.co.jp
  RFC4155          ||      E. Hall         ||       ehall@ntrg.com
  RFC4156          ||      P. Hoffman         ||       paul.hoffman@vpnc.org
  RFC4157          ||      P. Hoffman         ||       paul.hoffman@vpnc.org
  RFC4158          ||      M. Cooper, Y. Dzambasow, P. Hesse, S. Joseph, R. Nicholas         ||       mcooper@orionsec.com, yuriy@anassoc.com, pmhesse@geminisecurity.com, susan.joseph@vdtg.com, richard.nicholas@it.baesystems.com
  RFC4159          ||      G. Huston         ||       gih@apnic.net
  RFC4160          ||      K. Mimura, K. Yokoyama, T. Satoh, C. Kanaide, C. Allocchio         ||       mimu@miyabi-labo.net, keiyoko@msn.com, zsatou@t-ns.co.jp, icemilk77@yahoo.co.jp, Claudio.Allocchio@garr.it
  RFC4161          ||      K. Mimura, K. Yokoyama, T. Satoh, K. Watanabe, C. Kanaide         ||       mimu@miyabi-labo.net, keiyoko@msn.com, zsatou@t-ns.co.jp, knabe@ad.cyberhome.ne.jp, icemilk77@yahoo.co.jp
  RFC4162          ||      H.J. Lee, J.H. Yoon, J.I. Lee         ||       jiinii@kisa.or.kr, jhyoon@kisa.or.kr, jilee@kisa.or.kr
  RFC4163          ||      L-E. Jonsson         ||       lars-erik.jonsson@ericsson.com
  RFC4164          ||      G. Pelletier         ||       ghyslain.pelletier@ericsson.com
  RFC4165          ||      T. George, B. Bidulock, R. Dantu, H. Schwarzbauer, K. Morneault         ||       tgeorge_tx@verizon.net, bidulock@openss7.org, rdantu@unt.edu, HannsJuergen.Schwarzbauer@Siemens.com, kmorneau@cisco.com
  RFC4166          ||      L. Coene, J. Pastor-Balbas         ||       lode.coene@siemens.com, J.Javier.Pastor@ericsson.com
  RFC4167          ||      A. Lindem         ||       acee@cisco.com
  RFC4168          ||      J. Rosenberg, H. Schulzrinne, G. Camarillo         ||       jdrosen@cisco.com, schulzrinne@cs.columbia.edu, Gonzalo.Camarillo@ericsson.com
  RFC4169          ||      V. Torvinen, J. Arkko, M. Naslund         ||       vesa.torvinen@turkuamk.fi, jari.arkko@ericsson.com, mats.naslund@ericsson.com
  RFC4170          ||      B. Thompson, T. Koren, D. Wing         ||       brucet@cisco.com, tmima@cisco.com, dwing-ietf@fuggles.com
  RFC4171          ||      J. Tseng, K. Gibbons, F. Travostino, C. Du Laney, J. Souza         ||       joshtseng@yahoo.com, kevin.gibbons@mcdata.com, travos@nortel.com, cdl@rincon.com, joes@exmsft.com
  RFC4172          ||      C. Monia, R. Mullendore, F. Travostino, W. Jeong, M. Edwards         ||       charles_monia@yahoo.com, Rod.Mullendore@MCDATA.com, travos@nortel.com, wayland@TroikaNetworks.com, mark_edwards@adaptec.com
  RFC4173          ||      P. Sarkar, D. Missimer, C. Sapuntzakis         ||       psarkar@almaden.ibm.com, duncan.missimer@ieee.org, csapuntz@alum.mit.edu
  RFC4174          ||      C. Monia, J. Tseng, K. Gibbons         ||       charles_monia@yahoo.com, joshtseng@yahoo.com, kevin.gibbons@mcdata.com
  RFC4175          ||      L. Gharai, C. Perkins         ||       ladan@isi.edu, csp@csperkins.org
  RFC4176          ||      Y. El Mghazli, Ed., T. Nadeau, M. Boucadair, K. Chan, A. Gonguet         ||       yacine.el_mghazli@alcatel.fr, tnadeau@cisco.com, mohamed.boucadair@francetelecom.com, khchan@nortel.com, arnaud.gonguet@alcatel.fr
  RFC4177          ||      G. Huston         ||       gih@apnic.net
  RFC4178          ||      L. Zhu, P. Leach, K. Jaganathan, W. Ingersoll         ||       lzhu@microsoft.com, paulle@microsoft.com, karthikj@microsoft.com, wyllys.ingersoll@sun.com
  RFC4179          ||      S. Kang         ||       sukang@nca.or.kr
  RFC4180          ||      Y. Shafranovich         ||       ietf@shaftek.org
  RFC4181          ||      C. Heard, Ed.         ||       heard@pobox.com
  RFC4182          ||      E. Rosen         ||       erosen@cisco.com
  RFC4183          ||      E. Warnicke         ||       eaw@cisco.com
  RFC4184          ||      B. Link, T. Hager, J. Flaks         ||       bdl@dolby.com, thh@dolby.com, jasonfl@microsoft.com
  RFC4185          ||      J. Klensin         ||       john-ietf@jck.com
  RFC4186          ||      H. Haverinen, Ed., J. Salowey, Ed.         ||       henry.haverinen@nokia.com, jsalowey@cisco.com
  RFC4187          ||      J. Arkko, H. Haverinen         ||       jari.Arkko@ericsson.com, henry.haverinen@nokia.com
  RFC4188          ||      K. Norseth, Ed., E. Bell, Ed.         ||       kenyon.c.norseth@L-3com.com, elbell@ntlworld.com
  RFC4189          ||      K. Ono, S. Tachimoto         ||       ono.kumiko@lab.ntt.co.jp, kumiko@cs.columbia.edu, tachimoto.shinya@lab.ntt.co.jp
  RFC4190          ||      K. Carlberg, I. Brown, C. Beard         ||       k.carlberg@cs.ucl.ac.uk, I.Brown@cs.ucl.ac.uk, BeardC@umkc.edu
  RFC4191          ||      R. Draves, D. Thaler         ||       richdr@microsoft.com, dthaler@microsoft.com
  RFC4192          ||      F. Baker, E. Lear, R. Droms         ||       fred@cisco.com, lear@cisco.com, rdroms@cisco.com
  RFC4193          ||      R. Hinden, B. Haberman         ||       bob.hinden@gmail.com, brian@innovationslab.net
  RFC4194          ||      J. Strombergson, L. Walleij, P. Faltstrom         ||       Joachim.Strombergson@InformAsic.com, triad@df.lth.se, paf@cisco.com
  RFC4195          ||      W. Kameyama         ||       wataru@waseda.jp
  RFC4196          ||      H.J. Lee, J.H. Yoon, S.L. Lee, J.I. Lee         ||       jiinii@kisa.or.kr, jhyoon@kisa.or.kr, sllee@kisa.or.kr, jilee@kisa.or.kr
  RFC4197          ||      M. Riegel, Ed.         ||       maximilian.riegel@siemens.com
  RFC4198          ||      D. Tessman         ||       dtessman@zelestra.com
  RFC4201          ||      K. Kompella, Y. Rekhter, L. Berger         ||       kireeti@juniper.net, yakov@juniper.net, lberger@movaz.com
  RFC4202          ||      K. Kompella, Ed., Y. Rekhter, Ed.         ||       kireeti@juniper.net, yakov@juniper.net
  RFC4203          ||      K. Kompella, Ed., Y. Rekhter, Ed.         ||       kireeti@juniper.net, yakov@juniper.net
  RFC4204          ||      J. Lang, Ed.         ||       jplang@ieee.org
  RFC4205          ||      K. Kompella, Ed., Y. Rekhter, Ed.         ||       kireeti@juniper.net, yakov@juniper.net
  RFC4206          ||      K. Kompella, Y. Rekhter         ||       kireeti@juniper.net, yakov@juniper.net
  RFC4207          ||      J. Lang, D. Papadimitriou         ||       jplang@ieee.org, dimitri.papadimitriou@alcatel.be
  RFC4208          ||      G. Swallow, J. Drake, H. Ishimatsu, Y. Rekhter         ||       swallow@cisco.com, John.E.Drake2@boeing.com, hirokazu.ishimatsu@g1m.jp, yakov@juniper.net
  RFC4209          ||      A. Fredette, Ed., J. Lang, Ed.         ||       Afredette@HatterasNetworks.com, jplang@ieee.org
  RFC4210          ||      C. Adams, S. Farrell, T. Kause, T. Mononen         ||       cadams@site.uottawa.ca, stephen.farrell@cs.tcd.ie, toka@ssh.com, tmononen@safenet-inc.com
  RFC4211          ||      J. Schaad         ||       jimsch@exmsft.com
  RFC4212          ||      M. Blinov, C. Adams         ||       mikblinov@online.ie, cadams@site.uottawa.ca
  RFC4213          ||      E. Nordmark, R. Gilligan         ||       erik.nordmark@sun.com, bob.gilligan@acm.org
  RFC4214          ||      F. Templin, T. Gleeson, M. Talwar, D. Thaler         ||       fltemplin@acm.org, tgleeson@cisco.com, mohitt@microsoft.com, dthaler@microsoft.com
  RFC4215          ||      J. Wiljakka, Ed.         ||       juha.wiljakka@nokia.com
  RFC4216          ||      R. Zhang, Ed., J.-P. Vasseur, Ed.         ||       raymond_zhang@infonet.com, jpv@cisco.com
  RFC4217          ||      P. Ford-Hutchinson         ||       rfc4217@ford-hutchinson.com
  RFC4218          ||      E. Nordmark, T. Li         ||       erik.nordmark@sun.com, Tony.Li@tony.li
  RFC4219          ||      E. Lear         ||       lear@cisco.com
  RFC4220          ||      M. Dubuc, T. Nadeau, J. Lang         ||       mdubuc@ncf.ca, tnadeau@cisco.com, jplang@ieee.org
  RFC4221          ||      T. Nadeau, C. Srinivasan, A. Farrel         ||       tnadeau@cisco.com, cheenu@bloomberg.net, adrian@olddog.co.uk
  RFC4222          ||      G. Choudhury, Ed.         ||       gchoudhury@att.com
  RFC4223          ||      P. Savola         ||       psavola@funet.fi
  RFC4224          ||      G. Pelletier, L-E. Jonsson, K. Sandlund         ||       ghyslain.pelletier@ericsson.com, lars-erik.jonsson@ericsson.com, kristofer.sandlund@ericsson.com
  RFC4225          ||      P. Nikander, J. Arkko, T. Aura, G. Montenegro, E. Nordmark         ||       pekka.nikander@nomadiclab.com, jari.arkko@ericsson.com, Tuomaura@microsoft.com, gabriel_montenegro_2000@yahoo.com, erik.nordmark@sun.com
  RFC4226          ||      D. M'Raihi, M. Bellare, F. Hoornaert, D. Naccache, O. Ranen         ||       davidietf@gmail.com, mihir@cs.ucsd.edu, frh@vasco.com, david.naccache@gemplus.com, Ohad.Ranen@ealaddin.com
  RFC4227          ||      E. O'Tuathail, M. Rose         ||       eamon.otuathail@clipcode.com, mrose17@gmail.com
  RFC4228          ||      A. Rousskov         ||       rousskov@measurement-factory.com
  RFC4229          ||      M. Nottingham, J. Mogul         ||       mnot@pobox.com, JeffMogul@acm.org
  RFC4230          ||      H. Tschofenig, R. Graveman         ||       Hannes.Tschofenig@siemens.com, rfg@acm.org
  RFC4231          ||      M. Nystrom         ||       magnus@rsasecurity.com
  RFC4233          ||      K. Morneault, S. Rengasami, M. Kalla, G. Sidebottom         ||       kmorneau@cisco.com, mkalla@telcordia.com, selvam@trideaworks.com, greg@signatustechnologies.com
  RFC4234          ||      D. Crocker, Ed., P. Overell         ||       dcrocker@bbiw.net, paul@bayleaf.org.uk
  RFC4235          ||      J. Rosenberg, H. Schulzrinne, R. Mahy, Ed.         ||       jdrosen@cisco.com, schulzrinne@cs.columbia.edu, rohan@ekabal.com
  RFC4236          ||      A. Rousskov, M. Stecher         ||       rousskov@measurement-factory.com, martin.stecher@webwasher.com
  RFC4237          ||      G. Vaudreuil         ||       GregV@ieee.org
  RFC4238          ||      G. Vaudreuil         ||       GregV@ieee.org
  RFC4239          ||      S. McRae, G. Parsons         ||       stuart.mcrae@uk.ibm.com, gparsons@nortel.com
  RFC4240          ||      E. Burger, Ed., J. Van Dyke, A. Spitzer         ||       eburger@brooktrout.com, jvandyke@brooktrout.com, woof@brooktrout.com
  RFC4241          ||      Y. Shirasaki, S. Miyakawa, T. Yamasaki, A. Takenouchi         ||       yasuhiro@nttv6.jp, miyakawa@nttv6.jp, t.yamasaki@ntt.com, takenouchi.ayako@lab.ntt.co.jp
  RFC4242          ||      S. Venaas, T. Chown, B. Volz         ||       venaas@uninett.no, tjc@ecs.soton.ac.uk, volz@cisco.com
  RFC4243          ||      M. Stapp, R. Johnson, T. Palaniappan         ||       mjs@cisco.com, raj@cisco.com, athenmoz@cisco.com
  RFC4244          ||      M. Barnes, Ed.         ||       mary.barnes@nortel.com
  RFC4245          ||      O. Levin, R. Even         ||       oritl@microsoft.com, roni.even@polycom.co.il
  RFC4246          ||      M. Dolan         ||       md.1@newtbt.com
  RFC4247          ||      J. Ash, B. Goode, J. Hand, R. Zhang         ||       gash@att.com, bgoode@att.com, jameshand@att.com, raymond.zhang@bt.infonet.com
  RFC4248          ||      P. Hoffman         ||       paul.hoffman@vpnc.org
  RFC4249          ||      B. Lilly         ||       blilly@erols.com
  RFC4250          ||      S. Lehtinen, C. Lonvick, Ed.         ||       sjl@ssh.com, clonvick@cisco.com
  RFC4251          ||      T. Ylonen, C. Lonvick, Ed.         ||       ylo@ssh.com, clonvick@cisco.com
  RFC4252          ||      T. Ylonen, C. Lonvick, Ed.         ||       ylo@ssh.com, clonvick@cisco.com
  RFC4253          ||      T. Ylonen, C. Lonvick, Ed.         ||       ylo@ssh.com, clonvick@cisco.com
  RFC4254          ||      T. Ylonen, C. Lonvick, Ed.         ||       ylo@ssh.com, clonvick@cisco.com
  RFC4255          ||      J. Schlyter, W. Griffin         ||       jakob@openssh.com, wgriffin@sparta.com
  RFC4256          ||      F. Cusack, M. Forssen         ||       frank@savecore.net, maf@appgate.com
  RFC4257          ||      G. Bernstein, E. Mannie, V. Sharma, E. Gray         ||       gregb@grotto-networking.com, eric.mannie@perceval.net, v.sharma@ieee.org, Eric.Gray@Marconi.com
  RFC4258          ||      D. Brungard, Ed.         ||       dbrungard@att.com
  RFC4259          ||      M.-J. Montpetit, G. Fairhurst, H. Clausen, B. Collini-Nocker, H. Linder         ||       mmontpetit@motorola.com, gorry@erg.abdn.ac.uk, h.d.clausen@ieee.org, bnocker@cosy.sbg.ac.at, hlinder@cosy.sbg.ac.at
  RFC4260          ||      P. McCann         ||       mccap@lucent.com
  RFC4261          ||      J. Walker, A. Kulkarni, Ed.         ||       jesse.walker@intel.com, amol.kulkarni@intel.com
  RFC4262          ||      S. Santesson         ||       stefans@microsoft.com
  RFC4263          ||      B. Lilly         ||       blilly@erols.com
  RFC4264          ||      T. Griffin, G. Huston         ||       Timothy.Griffin@cl.cam.ac.uk, gih@apnic.net
  RFC4265          ||      B. Schliesser, T. Nadeau         ||       bensons@savvis.net, tnadeau@cisco.com
  RFC4266          ||      P. Hoffman         ||       paul.hoffman@vpnc.org
  RFC4267          ||      M. Froumentin         ||       mf@w3.org
  RFC4268          ||      S. Chisholm, D. Perkins         ||       schishol@nortel.com, dperkins@snmpinfo.com
  RFC4269          ||      H.J. Lee, S.J. Lee, J.H. Yoon, D.H. Cheon, J.I. Lee         ||       jiinii@kisa.or.kr, sjlee@kisa.or.kr, jhyoon@kisa.or.kr, dhcheon@mmaa.or.kr, jilee@kisa.or.kr
  RFC4270          ||      P. Hoffman, B. Schneier         ||       paul.hoffman@vpnc.org, schneier@counterpane.com
  RFC4271          ||      Y. Rekhter, Ed., T. Li, Ed., S. Hares, Ed.         ||       yakov@juniper.net, tony.li@tony.li, skh@nexthop.com
  RFC4272          ||      S. Murphy         ||       Sandy@tislabs.com
  RFC4273          ||      J. Haas, Ed., S. Hares, Ed.         ||       jhaas@nexthop.com, skh@nexthop.com
  RFC4274          ||      D. Meyer, K. Patel         ||       dmm@1-4-5.net, keyupate@cisco.com
  RFC4275          ||      S. Hares, D. Hares         ||       skh@nexthop.com, dhares@hickoryhill-consulting.com
  RFC4276          ||      S. Hares, A. Retana         ||       skh@nexthop.com, aretana@cisco.com
  RFC4277          ||      D. McPherson, K. Patel         ||       danny@arbor.net, keyupate@cisco.com
  RFC4278          ||      S. Bellovin, A. Zinin         ||       bellovin@acm.org, zinin@psg.com
  RFC4279          ||      P. Eronen, Ed., H. Tschofenig, Ed.         ||       pe@iki.fi, Hannes.Tschofenig@siemens.com
  RFC4280          ||      K. Chowdhury, P. Yegani, L. Madour         ||       kchowdhury@starentnetworks.com, pyegani@cisco.com, Lila.Madour@ericsson.com
  RFC4281          ||      R. Gellens, D. Singer, P. Frojdh         ||       randy@qualcomm.com, singer@apple.com, Per.Frojdh@ericsson.com
  RFC4282          ||      B. Aboba, M. Beadles, J. Arkko, P. Eronen         ||       bernarda@microsoft.com, mbeadles@endforce.com, jari.arkko@ericsson.com, pe@iki.fi
  RFC4283          ||      A. Patel, K. Leung, M. Khalil, H. Akhtar, K. Chowdhury         ||       alpesh@cisco.com, kleung@cisco.com, mkhalil@nortel.com, haseebak@nortel.com, kchowdhury@starentnetworks.com
  RFC4284          ||      F. Adrangi, V. Lortz, F. Bari, P. Eronen         ||       farid.adrangi@intel.com, victor.lortz@intel.com, farooq.bari@cingular.com, pe@iki.fi
  RFC4285          ||      A. Patel, K. Leung, M. Khalil, H. Akhtar, K. Chowdhury         ||       alpesh@cisco.com, kleung@cisco.com, mkhalil@nortel.com, haseebak@nortel.com, kchowdhury@starentnetworks.com
  RFC4286          ||      B. Haberman, J. Martin         ||       brian@innovationslab.net, jim@netzwert.ag
  RFC4287          ||      M. Nottingham, Ed., R. Sayre, Ed.         ||       mnot@pobox.com, rfsayre@boswijck.com
  RFC4288          ||      N. Freed, J. Klensin         ||       ned.freed@mrochek.com, klensin+ietf@jck.com
  RFC4289          ||      N. Freed, J. Klensin         ||       ned.freed@mrochek.com, klensin+ietf@jck.com
  RFC4290          ||      J. Klensin         ||       john-ietf@jck.com
  RFC4291          ||      R. Hinden, S. Deering         ||       bob.hinden@gmail.com
  RFC4292          ||      B. Haberman         ||       brian@innovationslab.net
  RFC4293          ||      S. Routhier, Ed.         ||       sar@iwl.com
  RFC4294          ||      J. Loughney, Ed.         ||       john.loughney@nokia.com
  RFC4295          ||      G. Keeni, K. Koide, K. Nagami, S. Gundavelli         ||       glenn@cysols.com, koide@shiratori.riec.tohoku.ac.jp, nagami@inetcore.com, sgundave@cisco.com
  RFC4296          ||      S. Bailey, T. Talpey         ||       steph@sandburst.com, thomas.talpey@netapp.com
  RFC4297          ||      A. Romanow, J. Mogul, T. Talpey, S. Bailey         ||       allyn@cisco.com, JeffMogul@acm.org, thomas.talpey@netapp.com, steph@sandburst.com
  RFC4298          ||      J.-H. Chen, W. Lee, J. Thyssen         ||       rchen@broadcom.com, wlee@broadcom.com, jthyssen@broadcom.com
  RFC4301          ||      S. Kent, K. Seo         ||       kent@bbn.com, kseo@bbn.com
  RFC4302          ||      S. Kent         ||       kent@bbn.com
  RFC4303          ||      S. Kent         ||       kent@bbn.com
  RFC4304          ||      S. Kent         ||       kent@bbn.com
  RFC4305          ||      D. Eastlake 3rd         ||       Donald.Eastlake@Motorola.com
  RFC4306          ||      C. Kaufman, Ed.         ||       charliek@microsoft.com
  RFC4307          ||      J. Schiller         ||       jis@mit.edu
  RFC4308          ||      P. Hoffman         ||       paul.hoffman@vpnc.org
  RFC4309          ||      R. Housley         ||       housley@vigilsec.com
  RFC4310          ||      S. Hollenbeck         ||       shollenbeck@verisign.com
  RFC4311          ||      R. Hinden, D. Thaler         ||       bob.hinden@gmail.com, dthaler@microsoft.com
  RFC4312          ||      A. Kato, S. Moriai, M. Kanda         ||       akato@po.ntts.co.jp, shiho@rd.scei.sony.co.jp, kanda@isl.ntt.co.jp
  RFC4313          ||      D. Oran         ||       oran@cisco.com
  RFC4314          ||      A. Melnikov         ||       alexey.melnikov@isode.com
  RFC4315          ||       M. Crispin         ||       MRC@CAC.Washington.EDU
  RFC4316          ||      J. Reschke         ||       julian.reschke@greenbytes.de
  RFC4317          ||      A. Johnston, R. Sparks         ||       ajohnston@tello.com, rjsparks@estacado.net
  RFC4318          ||      D. Levi, D. Harrington         ||       dlevi@nortel.com, ietfdbh@comcast.net
  RFC4319          ||      C. Sikes, B. Ray, R. Abbi         ||       csikes@zhone.com, rray@pesa.com, Rajesh.Abbi@alcatel.com
  RFC4320          ||      R. Sparks         ||       rjsparks@estacado.net
  RFC4321          ||      R. Sparks         ||       rjsparks@estacado.net
  RFC4322          ||      M. Richardson, D.H. Redelmeier         ||       mcr@sandelman.ottawa.on.ca, hugh@mimosa.com
  RFC4323          ||      M. Patrick, W. Murwin         ||       michael.patrick@motorola.com, w.murwin@motorola.com
  RFC4324          ||      D. Royer, G. Babics, S. Mansour         ||       Doug@IntelliCal.com, george.babics@oracle.com, smansour@ebay.com
  RFC4325          ||      S. Santesson, R. Housley         ||       stefans@microsoft.com, housley@vigilsec.com
  RFC4326          ||      G. Fairhurst, B. Collini-Nocker         ||       gorry@erg.abdn.ac.uk, bnocker@cosy.sbg.ac.at
  RFC4327          ||      M. Dubuc, T. Nadeau, J. Lang, E. McGinnis         ||       dubuc.consulting@sympatico.ca, tnadeau@cisco.com, jplang@ieee.org, emcginnis@hammerheadsystems.com
  RFC4328          ||      D. Papadimitriou, Ed.         ||       dimitri.papadimitriou@alcatel.be
  RFC4329          ||      B. Hoehrmann         ||       bjoern@hoehrmann.de
  RFC4330          ||      D. Mills         ||       mills@udel.edu
  RFC4331          ||      B. Korver, L. Dusseault         ||       briank@networkresonance.com, lisa.dusseault@gmail.com
  RFC4332          ||      K. Leung, A. Patel, G. Tsirtsis, E. Klovning         ||       kleung@cisco.com, alpesh@cisco.com, g.tsirtsis@flarion.com, espen@birdstep.com
  RFC4333          ||      G. Huston, Ed., B. Wijnen, Ed.         ||       gih@apnic.net, bwijnen@lucent.com
  RFC4334          ||      R. Housley, T. Moore         ||       housley@vigilsec.com, timmoore@microsoft.com
  RFC4335          ||      J. Galbraith, P. Remaker         ||       galb-list@vandyke.com, remaker@cisco.com
  RFC4336          ||      S. Floyd, M. Handley, E. Kohler         ||       floyd@icir.org, M.Handley@cs.ucl.ac.uk, kohler@cs.ucla.edu
  RFC4337          ||      Y Lim, D. Singer         ||       young@netntv.co.kr, singer@apple.com
  RFC4338          ||      C. DeSanti, C. Carlson, R. Nixon         ||       cds@cisco.com, craig.carlson@qlogic.com, bob.nixon@emulex.com
  RFC4339          ||      J. Jeong, Ed.         ||       jjeong@cs.umn.edu
  RFC4340          ||      E. Kohler, M. Handley, S. Floyd         ||       kohler@cs.ucla.edu, M.Handley@cs.ucl.ac.uk, floyd@icir.org
  RFC4341          ||      S. Floyd, E. Kohler         ||       floyd@icir.org, kohler@cs.ucla.edu
  RFC4342          ||      S. Floyd, E. Kohler, J. Padhye         ||       floyd@icir.org, kohler@cs.ucla.edu, padhye@microsoft.com
  RFC4343          ||      D. Eastlake 3rd         ||       Donald.Eastlake@motorola.com
  RFC4344          ||      M. Bellare, T. Kohno, C. Namprempre         ||       mihir@cs.ucsd.edu, tkohno@cs.ucsd.edu, meaw@alum.mit.edu
  RFC4345          ||      B. Harris         ||       bjh21@bjh21.me.uk
  RFC4346          ||      T. Dierks, E. Rescorla         ||       tim@dierks.org, ekr@rtfm.com
  RFC4347          ||      E. Rescorla, N. Modadugu         ||       ekr@rtfm.com, nagendra@cs.stanford.edu
  RFC4348          ||      S. Ahmadi         ||       sassan.ahmadi@ieee.org
  RFC4349          ||      C. Pignataro, M. Townsley         ||       cpignata@cisco.com, mark@townsley.net
  RFC4350          ||      F. Hendrikx, C. Wallis         ||       ferry.hendrikx@ssc.govt.nz, colin.wallis@ssc.govt.nz
  RFC4351          ||      G. Hellstrom, P. Jones         ||       gunnar.hellstrom@omnitor.se, paulej@packetizer.com
  RFC4352          ||      J. Sjoberg, M. Westerlund, A. Lakaniemi, S. Wenger         ||       Johan.Sjoberg@ericsson.com, Magnus.Westerlund@ericsson.com, ari.lakaniemi@nokia.com, Stephan.Wenger@nokia.com
  RFC4353          ||      J. Rosenberg         ||       jdrosen@cisco.com
  RFC4354          ||      M. Garcia-Martin         ||       miguel.an.garcia@nokia.com
  RFC4355          ||      R. Brandner, L. Conroy, R. Stastny         ||       rudolf.brandner@siemens.com, lwc@roke.co.uk, Richard.stastny@oefeg.at
  RFC4356          ||      R. Gellens         ||       randy@qualcomm.com
  RFC4357          ||      V. Popov, I. Kurepkin, S. Leontiev         ||       vpopov@cryptopro.ru, kure@cryptopro.ru, lse@cryptopro.ru
  RFC4358          ||      D. Smith         ||       dwight.smith@motorola.com
  RFC4359          ||      B. Weis         ||       bew@cisco.com
  RFC4360          ||      S. Sangli, D. Tappan, Y. Rekhter         ||       rsrihari@cisco.com, tappan@cisco.com, yakov@juniper.net
  RFC4361          ||      T. Lemon, B. Sommerfeld         ||       mellon@nominum.com, sommerfeld@sun.com
  RFC4362          ||      L-E. Jonsson, G. Pelletier, K. Sandlund         ||       lars-erik.jonsson@ericsson.com, ghyslain.pelletier@ericsson.com, kristofer.sandlund@ericsson.com
  RFC4363          ||      D. Levi, D. Harrington         ||       dlevi@nortel.com, ietfdbh@comcast.net
  RFC4364          ||      E. Rosen, Y. Rekhter         ||       erosen@cisco.com, yakov@juniper.net
  RFC4365          ||      E. Rosen         ||       erosen@cisco.com
  RFC4366          ||      S. Blake-Wilson, M. Nystrom, D. Hopwood, J. Mikkelsen, T. Wright         ||       sblakewilson@bcisse.com, magnus@rsasecurity.com, david.hopwood@blueyonder.co.uk, janm@transactionware.com, timothy.wright@vodafone.com
  RFC4367          ||      J. Rosenberg, Ed., IAB         ||       jdrosen@cisco.com
  RFC4368          ||      T. Nadeau, S. Hegde         ||       tnadeau@cisco.com, subrah@cisco.com
  RFC4369          ||      K. Gibbons, C. Monia, J. Tseng, F. Travostino         ||       kevin.gibbons@mcdata.com, charles_monia@yahoo.com, joshtseng@yahoo.com, travos@nortel.com
  RFC4370          ||      R. Weltman         ||       robw@worldspot.com
  RFC4371          ||      B. Carpenter, Ed., L. Lynch, Ed.         ||       brc@zurich.ibm.com, llynch@darkwing.uoregon.edu
  RFC4372          ||      F. Adrangi, A. Lior, J. Korhonen, J. Loughney         ||       farid.adrangi@intel.com, avi@bridgewatersystems.com, jouni.korhonen@teliasonera.com, john.loughney@nokia.com
  RFC4373          ||      R. Harrison, J. Sermersheim, Y. Dong         ||       rharrison@novell.com, jimse@novell.com, yulindong@gmail.com
  RFC4374          ||      G. McCobb         ||       mccobb@us.ibm.com
  RFC4375          ||      K. Carlberg         ||       carlberg@g11.org.uk
  RFC4376          ||      P. Koskelainen, J. Ott, H. Schulzrinne, X. Wu         ||       petri.koskelainen@nokia.com, jo@netlab.hut.fi, hgs@cs.columbia.edu, xiaotaow@cs.columbia.edu
  RFC4377          ||      T. Nadeau, M. Morrow, G. Swallow, D. Allan, S. Matsushima         ||       tnadeau@cisco.com, mmorrow@cisco.com, swallow@cisco.com, dallan@nortel.com, satoru@ft.solteria.net
  RFC4378          ||      D. Allan, Ed., T. Nadeau, Ed.         ||       dallan@nortel.com, tnadeau@cisco.com
  RFC4379          ||      K. Kompella, G. Swallow         ||       kireeti@juniper.net, swallow@cisco.com
  RFC4380          ||      C. Huitema         ||       huitema@microsoft.com
  RFC4381          ||      M. Behringer         ||       mbehring@cisco.com
  RFC4382          ||      T. Nadeau, Ed., H. van der Linde, Ed.         ||       tnadeau@cisco.com, havander@cisco.com
  RFC4383          ||      M. Baugher, E. Carrara         ||       mbaugher@cisco.com, carrara@kth.se
  RFC4384          ||      D. Meyer         ||       dmm@1-4-5.net
  RFC4385          ||      S. Bryant, G. Swallow, L. Martini, D. McPherson         ||       stbryant@cisco.com, swallow@cisco.com, lmartini@cisco.com, danny@arbor.net
  RFC4386          ||      S. Boeyen, P. Hallam-Baker         ||       sharon.boeyen@entrust.com, pbaker@VeriSign.com
  RFC4387          ||      P. Gutmann, Ed.         ||       pgut001@cs.auckland.ac.nz
  RFC4388          ||      R. Woundy, K. Kinnear         ||       richard_woundy@cable.comcast.com, kkinnear@cisco.com
  RFC4389          ||      D. Thaler, M. Talwar, C. Patel         ||       dthaler@microsoft.com, mohitt@microsoft.com, chirayu@chirayu.org
  RFC4390          ||      V. Kashyap         ||       vivk@us.ibm.com
  RFC4391          ||      J. Chu, V. Kashyap         ||       jerry.chu@sun.com, vivk@us.ibm.com
  RFC4392          ||      V. Kashyap         ||       vivk@us.ibm.com
  RFC4393          ||      H. Garudadri         ||       hgarudadri@qualcomm.com
  RFC4394          ||      D. Fedyk, O. Aboul-Magd, D. Brungard, J. Lang, D. Papadimitriou         ||       dwfedyk@nortel.com, osama@nortel.com, dbrungard@att.com, jplang@ieee.org, dimitri.papadimitriou@alcatel.be
  RFC4395          ||      T. Hansen, T. Hardie, L. Masinter         ||       tony+urireg@maillennium.att.com, hardie@qualcomm.com, LMM@acm.org
  RFC4396          ||      J. Rey, Y. Matsui         ||       jose.rey@eu.panasonic.com, matsui.yoshinori@jp.panasonic.com
  RFC4397          ||      I. Bryskin, A. Farrel         ||       i_bryskin@yahoo.com, adrian@olddog.co.uk
  RFC4398          ||      S. Josefsson         ||       simon@josefsson.org
  RFC4401          ||      N. Williams         ||       Nicolas.Williams@sun.com
  RFC4402          ||      N. Williams         ||       Nicolas.Williams@sun.com
  RFC4403          ||      B. Bergeson, K. Boogert, V. Nanjundaswamy         ||       bruce.bergeson@novell.com, kent.boogert@novell.com, vijay.nanjundaswamy@oracle.com
  RFC4404          ||      R. Natarajan, A. Rijhsinghani         ||       anil@charter.net, r.natarajan@f5.com
  RFC4405          ||      E. Allman, H. Katz         ||       eric@sendmail.com, hkatz@microsoft.com
  RFC4406          ||      J. Lyon, M. Wong         ||       jimlyon@microsoft.com, mengwong@dumbo.pobox.com
  RFC4407          ||      J. Lyon         ||       jimlyon@microsoft.com
  RFC4408          ||      M. Wong, W. Schlitt         ||       mengwong+spf@pobox.com, wayne@schlitt.net
  RFC4409          ||      R. Gellens, J. Klensin         ||       g+ietf@qualcomm.com, john+ietf@jck.com
  RFC4410          ||      M. Pullen, F. Zhao, D. Cohen         ||       mpullen@gmu.edu, fzhao@netlab.gmu.edu, danny.cohen@sun.com
  RFC4411          ||      J. Polk         ||       jmpolk@cisco.com
  RFC4412          ||      H. Schulzrinne, J. Polk         ||       hgs@cs.columbia.edu, jmpolk@cisco.com
  RFC4413          ||      M. West, S. McCann         ||       mark.a.west@roke.co.uk, stephen.mccann@roke.co.uk
  RFC4414          ||       A. Newton         ||       andy@hxr.us
  RFC4415          ||      R. Brandner, L. Conroy, R. Stastny         ||       rudolf.brandner@siemens.com, lwc@roke.co.uk, Richard.stastny@oefeg.at
  RFC4416          ||      J. Wong, Ed.         ||       j.k.wong@sympatico.ca
  RFC4417          ||      P. Resnick, Ed., P. Saint-Andre, Ed.         ||       presnick@qti.qualcomm.com, ietf@stpeter.im
  RFC4418          ||      T. Krovetz, Ed.         ||       tdk@acm.org
  RFC4419          ||      M. Friedl, N. Provos, W. Simpson         ||       markus@openbsd.org, provos@citi.umich.edu, wsimpson@greendragon.com
  RFC4420          ||      A. Farrel, Ed., D. Papadimitriou, J.-P. Vasseur, A. Ayyangar         ||       adrian@olddog.co.uk, dimitri.papadimitriou@alcatel.be, jpv@cisco.com, arthi@juniper.net
  RFC4421          ||      C. Perkins         ||       csp@csperkins.org
  RFC4422          ||      A. Melnikov, Ed.,  K. Zeilenga, Ed.         ||       Alexey.Melnikov@isode.com, Kurt@OpenLDAP.org
  RFC4423          ||      R. Moskowitz, P. Nikander         ||       rgm@icsalabs.com, pekka.nikander@nomadiclab.com
  RFC4424          ||      S. Ahmadi         ||       sassan.ahmadi@ieee.org
  RFC4425          ||      A. Klemets         ||       Anders.Klemets@microsoft.com
  RFC4426          ||      J. Lang, Ed., B. Rajagopalan, Ed., D. Papadimitriou, Ed.         ||       jplang@ieee.org, balar@microsoft.com, dimitri.papadimitriou@alcatel.be
  RFC4427          ||      E. Mannie, Ed., D. Papadimitriou, Ed.         ||       eric.mannie@perceval.net, dimitri.papadimitriou@alcatel.be
  RFC4428          ||      D. Papadimitriou, Ed., E. Mannie, Ed.         ||       dimitri.papadimitriou@alcatel.be, eric.mannie@perceval.net
  RFC4429          ||      N. Moore         ||       sharkey@zoic.org
  RFC4430          ||      S. Sakane, K. Kamada, M. Thomas, J. Vilhuber         ||       Shouichi.Sakane@jp.yokogawa.com, Ken-ichi.Kamada@jp.yokogawa.com, mat@cisco.com, vilhuber@cisco.com
  RFC4431          ||      M. Andrews, S. Weiler         ||       Mark_Andrews@isc.org,  weiler@tislabs.com
  RFC4432          ||      B. Harris         ||       bjh21@bjh21.me.uk
  RFC4433          ||      M. Kulkarni, A. Patel, K. Leung         ||       mkulkarn@cisco.com, alpesh@cisco.com, kleung@cisco.com
  RFC4434          ||      P. Hoffman         ||       paul.hoffman@vpnc.org
  RFC4435          ||      Y. Nomura, R. Walsh, J-P. Luoma, H. Asaeda, H. Schulzrinne         ||       nom@flab.fujitsu.co.jp, rod.walsh@nokia.com, juha-pekka.luoma@nokia.com, asaeda@wide.ad.jp, schulzrinne@cs.columbia.edu
  RFC4436          ||      B. Aboba, J. Carlson, S. Cheshire         ||       bernarda@microsoft.com, james.d.carlson@sun.com, rfc@stuartcheshire.org
  RFC4437          ||      J. Whitehead, G. Clemm, J. Reschke, Ed.         ||       ejw@cse.ucsc.edu, julian.reschke@greenbytes.degeoffrey.clemm@us.ibm.com, 
  RFC4438          ||      C. DeSanti, V. Gaonkar, H.K. Vivek, K. McCloghrie, S. Gai         ||       cds@cisco.com, vgaonkar@cisco.com, hvivek@cisco.com, kzm@cisco.com, none
  RFC4439          ||      C. DeSanti, V. Gaonkar, K. McCloghrie, S. Gai         ||       cds@cisco.com, vgaonkar@cisco.com, kzm@cisco.com, none
  RFC4440          ||      S. Floyd, Ed., V. Paxson, Ed., A. Falk, Ed., IAB         ||       floyd@acm.org, vern@icir.org, falk@isi.edu
  RFC4441          ||      B. Aboba, Ed.         ||       bernarda@microsoft.com
  RFC4442          ||      S. Fries, H. Tschofenig         ||       steffen.fries@siemens.com, Hannes.Tschofenig@siemens.com
  RFC4443          ||      A. Conta, S. Deering, M. Gupta, Ed.         ||       aconta@txc.com, none, mukesh.gupta@tropos.com
  RFC4444          ||      J. Parker, Ed.         ||       jeffp@middlebury.edu
  RFC4445          ||      J. Welch, J. Clark         ||       Jim.Welch@ineoquest.com, jiclark@cisco.com
  RFC4446          ||      L. Martini         ||       lmartini@cisco.com
  RFC4447          ||      L. Martini, Ed., E. Rosen, N. El-Aawar, T. Smith, G. Heron         ||       lmartini@cisco.com, nna@level3.net, giles.heron@tellabs.com, erosen@cisco.com, tob@netapp.com
  RFC4448          ||      L. Martini, Ed., E. Rosen, N. El-Aawar, G. Heron         ||       lmartini@cisco.com, nna@level3.net, giles.heron@tellabs.com, erosen@cisco.com
  RFC4449          ||      C. Perkins         ||       charles.perkins@nokia.com
  RFC4450          ||      E. Lear, H. Alvestrand         ||       lear@cisco.com, harald@alvestrand.no
  RFC4451          ||      D. McPherson, V. Gill         ||       danny@arbor.net, VijayGill9@aol.com
  RFC4452          ||      H. Van de Sompel, T. Hammond, E. Neylon, S. Weibel         ||       herbertv@lanl.gov, t.hammond@nature.com, eneylon@manifestsolutions.com, weibel@oclc.org
  RFC4453          ||      J. Rosenberg, G. Camarillo, Ed., D. Willis         ||       jdrosen@cisco.com, Gonzalo.Camarillo@ericsson.com, dean.willis@softarmor.com
  RFC4454          ||      S. Singh, M. Townsley, C. Pignataro         ||       sanjeevs@cisco.com, mark@townsley.net, cpignata@cisco.com
  RFC4455          ||      M. Hallak-Stamler, M. Bakke, Y. Lederman, M. Krueger, K. McCloghrie         ||       michele@sanrad.com, mbakke@cisco.com, yaronled@bezeqint.net, marjorie_krueger@hp.com, kzm@cisco.com
  RFC4456          ||      T. Bates, E. Chen, R. Chandra         ||       tbates@cisco.com, enkechen@cisco.com, rchandra@sonoasystems.com
  RFC4457          ||      G. Camarillo, G. Blanco         ||       Gonzalo.Camarillo@ericsson.com, german.blanco@ericsson.com
  RFC4458          ||      C. Jennings, F. Audet, J. Elwell         ||       fluffy@cisco.com, audet@nortel.com, john.elwell@siemens.com
  RFC4459          ||      P. Savola         ||       psavola@funet.fi
  RFC4460          ||      R. Stewart, I. Arias-Rodriguez, K. Poon, A. Caro, M. Tuexen         ||       randall@lakerest.net, ivan.arias-rodriguez@nokia.com, kacheong.poon@sun.com, acaro@bbn.com, tuexen@fh-muenster.de
  RFC4461          ||      S. Yasukawa, Ed.         ||       yasukawa.seisho@lab.ntt.co.jp
  RFC4462          ||      J. Hutzelman, J. Salowey, J. Galbraith, V. Welch         ||       jhutz+@cmu.edu, jsalowey@cisco.com, galb@vandyke.com, welch@mcs.anl.gov
  RFC4463          ||      S. Shanmugham, P. Monaco, B. Eberman         ||       sarvi@cisco.com, peter.monaco@nuasis.com, brian.eberman@speechworks.com
  RFC4464          ||      A. Surtees, M. West         ||       abigail.surtees@roke.co.uk, mark.a.west@roke.co.uk
  RFC4465          ||      A. Surtees, M. West         ||       abigail.surtees@roke.co.uk, mark.a.west@roke.co.uk
  RFC4466          ||      A. Melnikov, C. Daboo         ||       Alexey.Melnikov@isode.com, cyrus@daboo.name
  RFC4467          ||      M. Crispin         ||       MRC@CAC.Washington.EDU
  RFC4468          ||      C. Newman         ||       chris.newman@sun.com
  RFC4469          ||      P. Resnick         ||       presnick@qti.qualcomm.com
  RFC4470          ||      S. Weiler, J. Ihren         ||       weiler@tislabs.com, johani@autonomica.se
  RFC4471          ||      G. Sisson, B. Laurie         ||       geoff@nominet.org.uk, ben@algroup.co.uk
  RFC4472          ||      A. Durand, J. Ihren, P. Savola         ||       Alain_Durand@cable.comcast.com, johani@autonomica.se, psavola@funet.fi
  RFC4473          ||      Y. Nomura, R. Walsh, J-P. Luoma, J. Ott, H. Schulzrinne         ||       nom@flab.fujitsu.co.jp, rod.walsh@nokia.com, juha-pekka.luoma@nokia.com, jo@netlab.tkk.fi, schulzrinne@cs.columbia.edu
  RFC4474          ||      J. Peterson,  C. Jennings         ||       jon.peterson@neustar.biz, fluffy@cisco.com
  RFC4475          ||      R. Sparks, Ed., A. Hawrylyshen, A. Johnston, J. Rosenberg, H. Schulzrinne         ||       RjS@estacado.net, ahawrylyshen@ditechnetworks.com, alan@sipstation.com, jdrosen@cisco.com, hgs@cs.columbia.edu
  RFC4476          ||      C. Francis, D. Pinkas         ||       Chris_S_Francis@Raytheon.com, Denis.Pinkas@bull.net
  RFC4477          ||      T. Chown, S. Venaas, C. Strauf         ||       tjc@ecs.soton.ac.uk, venaas@uninett.no, strauf@rz.tu-clausthal.de
  RFC4478          ||      Y. Nir         ||       ynir@checkpoint.com
  RFC4479          ||      J. Rosenberg         ||       jdrosen@cisco.com
  RFC4480          ||      H. Schulzrinne, V. Gurbani, P. Kyzivat, J. Rosenberg         ||       hgs+simple@cs.columbia.edu, vkg@lucent.com, pkyzivat@cisco.com, jdrosen@cisco.com
  RFC4481          ||      H. Schulzrinne         ||       hgs+simple@cs.columbia.edu
  RFC4482          ||      H. Schulzrinne         ||       hgs+simple@cs.columbia.edu
  RFC4483          ||      E. Burger, Ed.         ||       eburger@cantata.com
  RFC4484          ||      J. Peterson, J. Polk, D. Sicker, H. Tschofenig         ||       jon.peterson@neustar.biz, jmpolk@cisco.com, douglas.sicker@colorado.edu, Hannes.Tschofenig@siemens.com
  RFC4485          ||      J. Rosenberg, H. Schulzrinne         ||       jdrosen@cisco.com, schulzrinne@cs.columbia.edu
  RFC4486          ||      E. Chen, V. Gillet         ||       enkechen@cisco.com, vgi@opentransit.net
  RFC4487          ||      F. Le, S. Faccin, B. Patil, H. Tschofenig         ||       franckle@cmu.edu, sfaccinstd@gmail.com, Basavaraj.Patil@nokia.com, Hannes.Tschofenig@siemens.com
  RFC4488          ||      O. Levin         ||       oritl@microsoft.com
  RFC4489          ||      J-S. Park, M-K. Shin, H-J. Kim         ||       pjs@etri.re.kr, myungki.shin@gmail.com, khj@etri.re.kr
  RFC4490          ||      S. Leontiev, Ed., G. Chudov, Ed.         ||       lse@cryptopro.ru, chudov@cryptopro.ru
  RFC4491          ||      S. Leontiev, Ed., D. Shefanovski, Ed.         ||       lse@cryptopro.ru, dbs@mts.ru
  RFC4492          ||      S. Blake-Wilson, N. Bolyard, V. Gupta, C. Hawk, B. Moeller         ||       sblakewilson@safenet-inc.com, nelson@bolyard.com, vipul.gupta@sun.com, chris@corriente.net, bodo@openssl.org
  RFC4493          ||      JH. Song, R. Poovendran, J. Lee, T. Iwata         ||       songlee@ee.washington.edu, radha@ee.washington.edu, icheol.lee@samsung.com, iwata@cse.nagoya-u.ac.jp
  RFC4494          ||      JH. Song, R. Poovendran, J. Lee         ||       songlee@ee.washington.edu, radha@ee.washington.edu, jicheol.lee@samsung.com
  RFC4495          ||      J. Polk, S. Dhesikan         ||       jmpolk@cisco.com, sdhesika@cisco.com
  RFC4496          ||      M. Stecher, A. Barbir         ||       martin.stecher@webwasher.com, abbieb@nortel.com
  RFC4497          ||      J. Elwell, F. Derks, P. Mourot, O. Rousseau         ||       john.elwell@siemens.com, frank.derks@nec-philips.com, Patrick.Mourot@alcatel.fr, Olivier.Rousseau@alcatel.fr 
  RFC4498          ||      G. Keeni         ||       glenn@cysols.com
  RFC4501          ||      S. Josefsson         ||       simon@josefsson.org
  RFC4502          ||      S. Waldbusser         ||       waldbusser@nextbeacon.com
  RFC4503          ||      M. Boesgaard, M. Vesterager, E. Zenner         ||       mab@cryptico.com, mvp@cryptico.com, ez@cryptico.com
  RFC4504          ||      H. Sinnreich, Ed.,  S. Lass, C. Stredicke         ||       henry@pulver.com, steven.lass@verizonbusiness.com, cs@snom.de
  RFC4505          ||      K. Zeilenga         ||       Kurt@OpenLDAP.org
  RFC4506          ||      M. Eisler, Ed.         ||       email2mre-rfc4506@yahoo.com
  RFC4507          ||      J. Salowey, H. Zhou, P. Eronen, H. Tschofenig         ||       jsalowey@cisco.com, hzhou@cisco.com, pe@iki.fi, Hannes.Tschofenig@siemens.com
  RFC4508          ||      O. Levin, A. Johnston         ||       oritl@microsoft.com, ajohnston@ipstation.com
  RFC4509          ||      W. Hardaker         ||       hardaker@tislabs.com
  RFC4510          ||      K. Zeilenga, Ed.         ||       Kurt@OpenLDAP.org
  RFC4511          ||      J. Sermersheim, Ed.         ||       jimse@novell.com
  RFC4512          ||      K. Zeilenga, Ed.         ||       Kurt@OpenLDAP.org
  RFC4513          ||      R. Harrison, Ed.         ||       roger_harrison@novell.com
  RFC4514          ||      K. Zeilenga, Ed.         ||       Kurt@OpenLDAP.org
  RFC4515          ||      M. Smith, Ed., T. Howes         ||       mcs@pearlcrescent.com, howes@opsware.com
  RFC4516          ||      M. Smith, Ed., T. Howes         ||       mcs@pearlcrescent.com, howes@opsware.com
  RFC4517          ||      S. Legg, Ed.         ||       steven.legg@eb2bcom.com
  RFC4518          ||      K. Zeilenga         ||       Kurt@OpenLDAP.org
  RFC4519          ||      A. Sciberras, Ed.         ||       andrew.sciberras@eb2bcom.com
  RFC4520          ||      K. Zeilenga         ||       Kurt@OpenLDAP.org
  RFC4521          ||      K. Zeilenga         ||       Kurt@OpenLDAP.org
  RFC4522          ||      S. Legg         ||       steven.legg@eb2bcom.com
  RFC4523          ||      K. Zeilenga         ||       Kurt@OpenLDAP.org
  RFC4524          ||      K. Zeilenga, Ed.         ||       Kurt@OpenLDAP.org
  RFC4525          ||      K. Zeilenga         ||       Kurt@OpenLDAP.org
  RFC4526          ||      K. Zeilenga         ||       Kurt@OpenLDAP.org
  RFC4527          ||      K. Zeilenga         ||       Kurt@OpenLDAP.org
  RFC4528          ||      K. Zeilenga         ||       Kurt@OpenLDAP.org
  RFC4529          ||      K. Zeilenga         ||       Kurt@OpenLDAP.org
  RFC4530          ||      K. Zeilenga         ||       Kurt@OpenLDAP.org
  RFC4531          ||      K. Zeilenga         ||       Kurt@OpenLDAP.org
  RFC4532          ||      K. Zeilenga         ||       Kurt@OpenLDAP.org
  RFC4533          ||      K. Zeilenga, J.H. Choi         ||       Kurt@OpenLDAP.org, jongchoi@us.ibm.com
  RFC4534          ||      A Colegrove, H Harney         ||       acc@sparta.com, hh@sparta.com
  RFC4535          ||      H. Harney, U. Meth, A. Colegrove, G. Gross         ||       hh@sparta.com, umeth@sparta.com, acc@sparta.com, gmgross@identaware.com
  RFC4536          ||      P. Hoschka         ||       ph@w3.org
  RFC4537          ||      L. Zhu, P. Leach, K. Jaganathan         ||       lzhu@microsoft.com, paulle@microsoft.com, karthikj@microsoft.com
  RFC4538          ||      J. Rosenberg         ||       jdrosen@cisco.com
  RFC4539          ||      T. Edwards         ||       tedwards@pbs.org
  RFC4540          ||      M. Stiemerling, J. Quittek, C. Cadar         ||       stiemerling@netlab.nec.de, quittek@netlab.nec.de, ccadar2@yahoo.com
  RFC4541          ||      M. Christensen, K. Kimball, F. Solensky         ||       mjc@tt.dk, karen.kimball@hp.com, frank.solensky@calix.com
  RFC4542          ||      F. Baker, J. Polk         ||       fred@cisco.com, jmpolk@cisco.com
  RFC4543          ||      D. McGrew, J. Viega         ||       mcgrew@cisco.com, viega@list.org
  RFC4544          ||      M. Bakke, M. Krueger, T. McSweeney, J. Muchow         ||       mbakke@cisco.com, marjorie_krueger@hp.com, tommcs@us.ibm.com, james.muchow@qlogic.com
  RFC4545          ||      M. Bakke, J. Muchow         ||       mbakke@cisco.com, james.muchow@qlogic.com
  RFC4546          ||      D. Raftus, E. Cardona         ||       david.raftus@ati.com, e.cardona@cablelabs.com
  RFC4547          ||      A. Ahmad, G. Nakanishi         ||       azlina@cisco.com, gnakanishi@motorola.com
  RFC4548          ||      E. Gray, J. Rutemiller, G. Swallow         ||       Eric.Gray@Marconi.com, John.Rutemiller@Marconi.com, swallow@cisco.com
  RFC4549          ||      A. Melnikov, Ed.         ||       alexey.melnikov@isode.com
  RFC4550          ||      S. Maes, A. Melnikov         ||       stephane.maes@oracle.com, Alexey.melnikov@isode.com
  RFC4551          ||      A. Melnikov, S. Hole         ||       Alexey.Melnikov@isode.com, Steve.Hole@messagingdirect.com
  RFC4552          ||      M. Gupta, N. Melam         ||       mukesh.gupta@tropos.com, nmelam@juniper.net
  RFC4553          ||      A. Vainshtein, Ed., YJ. Stein, Ed.         ||       sasha@axerra.com, yaakov_s@rad.com
  RFC4554          ||      T. Chown         ||       tjc@ecs.soton.ac.uk
  RFC4555          ||      P. Eronen         ||       pe@iki.fi
  RFC4556          ||      L. Zhu, B. Tung         ||       lzhu@microsoft.com, brian@aero.org
  RFC4557          ||      L. Zhu, K. Jaganathan, N. Williams         ||       lzhu@microsoft.com, karthikj@microsoft.com, Nicolas.Williams@sun.com
  RFC4558          ||      Z. Ali, R. Rahman, D. Prairie, D. Papadimitriou         ||       zali@cisco.com, rrahman@cisco.com, dprairie@cisco.com, dimitri.papadimitriou@alcatel.be
  RFC4559          ||      K. Jaganathan, L. Zhu, J. Brezak         ||       karthikj@microsoft.com, lzhu@microsoft.com, jbrezak@microsoft.com
  RFC4560          ||      J. Quittek, Ed., K. White, Ed.         ||       quittek@netlab.nec.de, wkenneth@us.ibm.com
  RFC4561          ||      J.-P. Vasseur, Ed., Z. Ali, S. Sivabalan         ||       jpv@cisco.com, zali@cisco.com, msiva@cisco.com
  RFC4562          ||      T. Melsen, S. Blake         ||       Torben.Melsen@ericsson.com, steven.blake@ericsson.com
  RFC4563          ||      E. Carrara, V. Lehtovirta, K. Norrman         ||       carrara@kth.se, vesa.lehtovirta@ericsson.com, karl.norrman@ericsson.com
  RFC4564          ||      S. Govindan, Ed., H. Cheng, ZH. Yao, WH. Zhou, L. Yang         ||       saravanan.govindan@sg.panasonic.com, hong.cheng@sg.panasonic.com, yaoth@huawei.com, zhouwenhui@chinamobile.com, lily.l.yang@intel.com
  RFC4565          ||      D. Loher, D. Nelson, O. Volinsky, B. Sarikaya         ||       dplore@gmail.com, dnelson@enterasys.com, ovolinsky@colubris.com, sarikaya@ieee.org
  RFC4566          ||      M. Handley, V. Jacobson, C. Perkins         ||       M.Handley@cs.ucl.ac.uk, van@packetdesign.com, csp@csperkins.org
  RFC4567          ||      J. Arkko, F. Lindholm, M. Naslund, K. Norrman, E. Carrara         ||       jari.arkko@ericsson.com, fredrik.lindholm@ericsson.com, mats.naslund@ericsson.com, karl.norrman@ericsson.com, carrara@kth.se
  RFC4568          ||      F. Andreasen, M. Baugher, D. Wing         ||       fandreas@cisco.com, mbaugher@cisco.com, dwing-ietf@fuggles.com
  RFC4569          ||      G. Camarillo         ||       Gonzalo.Camarillo@ericsson.com
  RFC4570          ||      B. Quinn, R. Finlayson         ||       rcq@boxnarrow.com, finlayson@live555.com
  RFC4571          ||      J. Lazzaro         ||       lazzaro@cs.berkeley.edu
  RFC4572          ||      J. Lennox         ||       lennox@cs.columbia.edu
  RFC4573          ||      R. Even, A. Lochbaum         ||        roni.even@polycom.co.il, alochbaum@polycom.com
  RFC4574          ||      O. Levin, G. Camarillo         ||       oritl@microsoft.com, Gonzalo.Camarillo@ericsson.com
  RFC4575          ||      J. Rosenberg, H. Schulzrinne, O. Levin, Ed.         ||       jdrosen@cisco.com, schulzrinne@cs.columbia.edu, oritl@microsoft.com
  RFC4576          ||      E. Rosen, P. Psenak, P. Pillay-Esnault         ||       erosen@cisco.com, ppsenak@cisco.com, ppe@cisco.com
  RFC4577          ||      E. Rosen, P. Psenak, P. Pillay-Esnault         ||       erosen@cisco.com, ppsenak@cisco.com, ppe@cisco.com
  RFC4578          ||      M. Johnston, S. Venaas, Ed.         ||       michael.johnston@intel.com, venaas@uninett.no
  RFC4579          ||      A. Johnston, O. Levin         ||       alan@sipstation.com, oritl@microsoft.com
  RFC4580          ||      B. Volz         ||       volz@cisco.com
  RFC4581          ||      M. Bagnulo, J. Arkko         ||       marcelo@it.uc3m.es, jari.arkko@ericsson.com
  RFC4582          ||      G. Camarillo, J. Ott, K. Drage         ||       Gonzalo.Camarillo@ericsson.com, jo@netlab.hut.fi, drage@lucent.com
  RFC4583          ||      G. Camarillo         ||       Gonzalo.Camarillo@ericsson.com
  RFC4584          ||      S. Chakrabarti, E. Nordmark         ||       samitac2@gmail.com, erik.nordmark@sun.com
  RFC4585          ||      J. Ott, S. Wenger, N. Sato, C. Burmeister, J. Rey         ||       jo@acm.org, stewe@stewe.org, sato652@oki.com, carsten.burmeister@eu.panasonic.com, jose.rey@eu.panasonic.com
  RFC4586          ||      C. Burmeister, R. Hakenberg, A. Miyazaki, J. Ott, N. Sato, S. Fukunaga         ||       carsten.burmeister@eu.panasonic.com, rolf.hakenberg@eu.panasonic.com, miyazaki.akihiro@jp.panasonic.com, jo@acm.org, sato652@oki.com, fukunaga444@oki.com
  RFC4587          ||      R. Even         ||       roni.even@polycom.co.il
  RFC4588          ||      J. Rey, D. Leon, A. Miyazaki, V. Varsa, R. Hakenberg         ||       jose.rey@eu.panasonic.com, davidleon123@yahoo.com, miyazaki.akihiro@jp.panasonic.com, viktor.varsa@nokia.com, rolf.hakenberg@eu.panasonic.com
  RFC4589          ||      H. Schulzrinne, H. Tschofenig         ||       schulzrinne@cs.columbia.edu, Hannes.Tschofenig@siemens.com
  RFC4590          ||      B. Sterman, D. Sadolevsky, D. Schwartz, D. Williams, W. Beck         ||       baruch@kayote.com, dscreat@dscreat.com, david@kayote.com, dwilli@cisco.com, beckw@t-systems.com
  RFC4591          ||      M. Townsley, G. Wilkie, S. Booth, S. Bryant, J. Lau         ||       mark@townsley.net, gwilkie@cisco.com, jebooth@cisco.com, stbryant@cisco.com, jedlau@gmail.com
  RFC4592          ||      E. Lewis         ||       ed.lewis@neustar.biz
  RFC4593          ||      A. Barbir, S. Murphy, Y. Yang         ||       abbieb@nortel.com, sandy@sparta.com, yiya@cisco.com
  RFC4594          ||      J. Babiarz, K. Chan, F. Baker         ||       babiarz@nortel.com, khchan@nortel.com, fred@cisco.com
  RFC4595          ||      F. Maino, D. Black         ||       fmaino@cisco.com, black_david@emc.com
  RFC4596          ||      J. Rosenberg, P. Kyzivat         ||       jdrosen@cisco.com, pkyzivat@cisco.com
  RFC4597          ||      R. Even, N. Ismail         ||       roni.even@polycom.co.il, nismail@cisco.com
  RFC4598          ||      B. Link         ||       bdl@dolby.com
  RFC4601          ||      B. Fenner, M. Handley, H. Holbrook, I. Kouvelas         ||       fenner@research.att.com, M.Handley@cs.ucl.ac.uk, holbrook@arastra.com, kouvelas@cisco.com
  RFC4602          ||      T. Pusateri         ||       pusateri@juniper.net
  RFC4603          ||      G. Zorn, G. Weber, R. Foltak         ||       gwz@cisco.com, gdweber@cisco.com, rfoltak@cisco.com
  RFC4604          ||      H. Holbrook, B. Cain, B. Haberman         ||       holbrook@cisco.com, bcain99@gmail.com, brian@innovationslab.net
  RFC4605          ||      B. Fenner, H. He, B. Haberman, H. Sandick         ||       fenner@research.att.com, haixiang@nortelnetworks.com, brian@innovationslab.net, sandick@nc.rr.com
  RFC4606          ||      E. Mannie, D. Papadimitriou         ||       eric.mannie@perceval.net, dimitri.papadimitriou@alcatel.be
  RFC4607          ||      H. Holbrook, B. Cain         ||       holbrook@arastra.com, bcain99@gmail.com
  RFC4608          ||      D. Meyer, R. Rockell, G. Shepherd         ||       dmm@1-4-5.net, rrockell@sprint.net, gjshep@gmail.com
  RFC4609          ||      P. Savola, R. Lehtonen, D. Meyer         ||       psavola@funet.fi, rami.lehtonen@teliasonera.com, dmm@1-4-5.net
  RFC4610          ||      D. Farinacci, Y. Cai         ||       dino@cisco.com, ycai@cisco.com
  RFC4611          ||      M. McBride, J. Meylor, D. Meyer         ||       mcbride@cisco.com, jmeylor@cisco.com, dmm@1-4-5.net
  RFC4612          ||      P. Jones, H. Tamura         ||       paulej@packetizer.com, tamura@cs.ricoh.co.jp
  RFC4613          ||      P. Frojdh, U. Lindgren, M. Westerlund         ||       per.frojdh@ericsson.com, ulf.a.lindgren@ericsson.com, magnus.westerlund@ericsson.com
  RFC4614          ||      M. Duke, R. Braden, W. Eddy, E. Blanton         ||       martin.duke@boeing.com, braden@isi.edu, weddy@grc.nasa.gov, eblanton@cs.purdue.edu
  RFC4615          ||      J. Song, R. Poovendran, J. Lee, T. Iwata         ||       junhyuk.song@gmail.com, radha@ee.washington.edu, jicheol.lee@samsung.com, iwata@cse.nagoya-u.ac.jp
  RFC4616          ||      K. Zeilenga, Ed.         ||       Kurt@OpenLDAP.org
  RFC4617          ||      J. Kornijenko         ||       j.kornienko@abcsoftware.lv
  RFC4618          ||      L. Martini, E. Rosen, G. Heron, A. Malis         ||       lmartini@cisco.com, erosen@cisco.com, giles.heron@tellabs.com, Andy.Malis@tellabs.com
  RFC4619          ||      L. Martini, Ed., C. Kawa, Ed., A. Malis, Ed.         ||       lmartini@cisco.com, claude.kawa@oz.com, Andy.Malis@tellabs.com
  RFC4620          ||      M. Crawford,  B. Haberman, Ed.         ||       crawdad@fnal.gov, brian@innovationslab.net
  RFC4621          ||      T. Kivinen, H. Tschofenig         ||       kivinen@safenet-inc.com, Hannes.Tschofenig@siemens.com
  RFC4622          ||      P. Saint-Andre         ||       ietf@stpeter.im
  RFC4623          ||      A. Malis, M. Townsley         ||       Andy.Malis@tellabs.com, mark@townsley.net
  RFC4624          ||      B. Fenner, D. Thaler         ||       fenner@research.att.com, dthaler@microsoft.com
  RFC4625          ||      C. DeSanti, K. McCloghrie, S. Kode, S. Gai         ||       cds@cisco.com, srinikode@yahoo.com, kzm@cisco.com, none
  RFC4626          ||      C. DeSanti, V. Gaonkar, K. McCloghrie, S. Gai         ||       cds@cisco.com, vgaonkar@cisco.com, kzm@cisco.com, none
  RFC4627          ||      D. Crockford         ||       douglas@crockford.com
  RFC4628          ||      R. Even         ||       roni.even@polycom.co.il
  RFC4629          ||      J. Ott, C. Bormann, G. Sullivan, S. Wenger, R. Even, Ed.         ||       jo@netlab.tkk.fi, cabo@tzi.org, garysull@microsoft.com, stewe@stewe.org, roni.even@polycom.co.il
  RFC4630          ||      R. Housley, S. Santesson         ||       housley@vigilsec.com, stefans@microsoft.com
  RFC4631          ||      M. Dubuc, T. Nadeau, J. Lang, E. McGinnis, A. Farrel         ||       dubuc.consulting@sympatico.ca, tnadeau@cisco.com, jplang@ieee.org, emcginnis@hammerheadsystems.com, adrian@olddog.co.uk
  RFC4632          ||      V. Fuller, T. Li         ||       vaf@cisco.com, tli@tropos.com
  RFC4633          ||      S. Hartman         ||       hartmans-ietf@mit.edu
  RFC4634          ||      D. Eastlake 3rd, T. Hansen         ||       donald.eastlake@motorola.com, tony+shs@maillennium.att.com
  RFC4635          ||      D. Eastlake 3rd         ||       Donald.Eastlake@motorola.com
  RFC4636          ||      C. Perkins         ||       charles.perkins@nokia.com
  RFC4637          ||               ||       
  RFC4638          ||      P. Arberg, D. Kourkouzelis, M. Duckett, T. Anschutz, J. Moisand         ||       parberg@redback.com, diamondk@redback.com, mike.duckett@bellsouth.com, tom.anschutz@bellsouth.com, jmoisand@juniper.net
  RFC4639          ||      R. Woundy, K. Marez         ||       richard_woundy@cable.comcast.com, kevin.marez@motorola.com
  RFC4640          ||      A. Patel, Ed., G. Giaretta, Ed.         ||       alpesh@cisco.com, gerardo.giaretta@telecomitalia.it
  RFC4641          ||      O. Kolkman, R. Gieben         ||       olaf@nlnetlabs.nl, miek@miek.nl
  RFC4642          ||      K. Murchison, J. Vinocur, C. Newman         ||       murch@andrew.cmu.edu, vinocur@cs.cornell.edu, Chris.Newman@sun.com
  RFC4643          ||      J. Vinocur, K. Murchison         ||       vinocur@cs.cornell.edu, murch@andrew.cmu.edu
  RFC4644          ||      J. Vinocur, K. Murchison         ||       vinocur@cs.cornell.edu, murch@andrew.cmu.edu
  RFC4645          ||      D. Ewell         ||       dewell@adelphia.net
  RFC4646          ||      A. Phillips, M. Davis         ||       addison@inter-locale.com, mark.davis@macchiato.com
  RFC4647          ||      A. Phillips, M. Davis         ||       addison@inter-locale.com, mark.davis@macchiato.com
  RFC4648          ||      S. Josefsson         ||       simon@josefsson.org
  RFC4649          ||      B. Volz         ||       volz@cisco.com
  RFC4650          ||      M. Euchner         ||       martin_euchner@hotmail.com
  RFC4651          ||      C. Vogt, J. Arkko         ||       chvogt@tm.uka.de, jari.arkko@ericsson.com
  RFC4652          ||      D. Papadimitriou, Ed., L.Ong, J. Sadler, S. Shew, D. Ward         ||       dimitri.papadimitriou@alcatel.be, lyong@ciena.com, jonathan.sadler@tellabs.com, sdshew@nortel.com, dward@cisco.com
  RFC4653          ||      S. Bhandarkar, A. L. N. Reddy, M. Allman, E. Blanton         ||       sumitha@tamu.edu, reddy@ee.tamu.edu, mallman@icir.org, eblanton@cs.purdue.edu
  RFC4654          ||      J. Widmer, M. Handley         ||       widmer@acm.org, m.handley@cs.ucl.ac.uk
  RFC4655          ||      A. Farrel, J.-P. Vasseur, J. Ash         ||       adrian@olddog.co.uk, jpv@cisco.com, gash@att.com
  RFC4656          ||      S. Shalunov, B. Teitelbaum, A. Karp, J. Boote, M. Zekauskas         ||       shalunov@internet2.edu, ben@internet2.edu, akarp@cs.wisc.edu, boote@internet2.edu, matt@internet2.edu
  RFC4657          ||      J. Ash, Ed., J.L. Le Roux, Ed.         ||       gash@att.com, jeanlouis.leroux@orange-ft.com
  RFC4659          ||      J. De Clercq, D. Ooms, M. Carugi, F. Le Faucheur         ||       jeremy.de_clercq@alcatel.be, dirk@onesparrow.com, marco.carugi@nortel.com, flefauch@cisco.com
  RFC4660          ||      H. Khartabil, E. Leppanen, M. Lonnfors, J. Costa-Requena         ||       hisham.khartabil@telio.no, eva-maria.leppanen@nokia.com, mikko.lonnfors@nokia.com, jose.costa-requena@nokia.com
  RFC4661          ||      H. Khartabil, E. Leppanen, M. Lonnfors, J. Costa-Requena         ||       hisham.khartabil@telio.no, eva-maria.leppanen@nokia.com, mikko.lonnfors@nokia.com, jose.costa-requena@nokia.com
  RFC4662          ||      A. B. Roach, B. Campbell, J. Rosenberg         ||       adam@estacado.net,  ben@estacado.net, jdrosen@cisco.com
  RFC4663          ||      D. Harrington         ||       dbharrington@comcast.net
  RFC4664          ||      L. Andersson, Ed., E. Rosen, Ed.         ||       loa@pi.se, erosen@cisco.com
  RFC4665          ||      W. Augustyn, Ed., Y. Serbest, Ed.         ||       waldemar@wdmsys.com, yetik_serbest@labs.att.com
  RFC4666          ||      K. Morneault, Ed., J. Pastor-Balbas, Ed.         ||       kmorneau@cisco.com, j.javier.pastor@ericsson.com
  RFC4667          ||      W. Luo         ||       luo@cisco.com
  RFC4668          ||      D. Nelson         ||       dnelson@enterasys.com
  RFC4669          ||      D. Nelson         ||       dnelson@enterasys.com
  RFC4670          ||      D. Nelson         ||       dnelson@enterasys.com
  RFC4671          ||      D. Nelson         ||       dnelson@enterasys.com
  RFC4672          ||      S. De Cnodder, N. Jonnala, M. Chiba         ||       stefaan.de_cnodder@alcatel.be, njonnala@cisco.com, mchiba@cisco.com
  RFC4673          ||      S. De Cnodder, N. Jonnala, M. Chiba         ||       stefaan.de_cnodder@alcatel.be, njonnala@cisco.com, mchiba@cisco.com
  RFC4674          ||      J.L. Le Roux, Ed.         ||       jeanlouis.leroux@francetelecom.com
  RFC4675          ||      P. Congdon, M. Sanchez, B. Aboba         ||       paul.congdon@hp.com, mauricio.sanchez@hp.com, bernarda@microsoft.com
  RFC4676          ||      H. Schulzrinne         ||       hgs+geopriv@cs.columbia.edu
  RFC4677          ||      P. Hoffman, S. Harris         ||       paul.hoffman@vpnc.org, srh@umich.edu
  RFC4678          ||      A. Bivens         ||       jbivens@us.ibm.com
  RFC4679          ||      V. Mammoliti, G. Zorn, P. Arberg, R. Rennison         ||       vince@cisco.com, gwz@cisco.com, parberg@redback.com, robert.rennison@ecitele.com
  RFC4680          ||      S. Santesson         ||       stefans@microsoft.com
  RFC4681          ||      S. Santesson, A. Medvinsky, J. Ball         ||       stefans@microsoft.com, arimed@microsoft.com, joshball@microsoft.com
  RFC4682          ||      E. Nechamkin, J-F. Mule         ||       enechamkin@broadcom.com, jf.mule@cablelabs.com
  RFC4683          ||      J. Park, J. Lee, H.. Lee, S. Park, T. Polk         ||       khopri@kisa.or.kr, jilee@kisa.or.kr, hslee@kisa.or.kr, sjpark@bcqre.com, tim.polk@nist.gov
  RFC4684          ||      P. Marques, R. Bonica, L. Fang, L. Martini, R. Raszuk, K. Patel, J. Guichard         ||       roque@juniper.net, rbonica@juniper.net, luyuanfang@att.com, lmartini@cisco.com, rraszuk@cisco.com, keyupate@cisco.com, jguichar@cisco.com
  RFC4685          ||      J. Snell         ||       jasnell@gmail.com
  RFC4686          ||      J. Fenton         ||       fenton@bluepopcorn.net
  RFC4687          ||      S. Yasukawa, A. Farrel, D. King, T. Nadeau         ||       s.yasukawa@hco.ntt.co.jp, adrian@olddog.co.uk, daniel.king@aria-networks.com, tnadeau@cisco.com
  RFC4688          ||      S. Rushing         ||       srushing@inmedius.com
  RFC4689          ||      S. Poretsky, J. Perser, S. Erramilli, S. Khurana         ||       sporetsky@reefpoint.com, jerry@perser.org, shobha@research.telcordia.com, skhurana@motorola.com
  RFC4690          ||      J. Klensin, P. Faltstrom, C. Karp, IAB         ||       john-ietf@jck.com, paf@cisco.com, ck@nic.museum, iab@iab.org
  RFC4691          ||      L. Andersson, Ed.         ||       loa@pi.se
  RFC4692          ||      G. Huston         ||       gih@apnic.net
  RFC4693          ||      H. Alvestrand         ||       harald@alvestrand.no
  RFC4694          ||      J. Yu         ||       james.yu@neustar.biz
  RFC4695          ||      J. Lazzaro, J. Wawrzynek         ||       lazzaro@cs.berkeley.edu, johnw@cs.berkeley.edu
  RFC4696          ||      J. Lazzaro, J. Wawrzynek         ||       lazzaro@cs.berkeley.edu, johnw@cs.berkeley.edu
  RFC4697          ||       M. Larson, P. Barber         ||       mlarson@verisign.com, pbarber@verisign.com
  RFC4698          ||      E. Gunduz, A. Newton, S. Kerr         ||       e.gunduz@computer.org, andy@hxr.us, shane@time-travellers.org
  RFC4701          ||      M. Stapp, T. Lemon, A. Gustafsson         ||       mjs@cisco.com, mellon@nominum.com, gson@araneus.fi
  RFC4702          ||      M. Stapp, B. Volz, Y. Rekhter         ||       mjs@cisco.com, volz@cisco.com, yakov@juniper.net
  RFC4703          ||      M. Stapp, B. Volz         ||       mjs@cisco.com, volz@cisco.com
  RFC4704          ||      B. Volz         ||       volz@cisco.com
  RFC4705          ||      R. Housley, A. Corry         ||       housley@vigilsec.com, publications@gigabeam.com
  RFC4706          ||      M. Morgenstern, M. Dodge, S. Baillie, U. Bonollo         ||       moti.Morgenstern@ecitele.com, mbdodge@ieee.org, scott.baillie@nec.com.au, umberto.bonollo@nec.com.au
  RFC4707          ||      P. Grau, V. Heinau, H. Schlichting, R. Schuettler         ||       nas@fu-berlin.de, nas@fu-berlin.de, nas@fu-berlin.de, nas@fu-berlin.de
  RFC4708          ||      A. Miller         ||       ak.miller@auckland.ac.nz
  RFC4709          ||      J. Reschke         ||       julian.reschke@greenbytes.de
  RFC4710          ||      A. Siddiqui, D. Romascanu, E. Golovinsky         ||       anwars@avaya.com, dromasca@gmail.com , gene@alertlogic.net
  RFC4711          ||      A. Siddiqui, D. Romascanu, E. Golovinsky         ||       anwars@avaya.com, dromasca@gmail.com , gene@alertlogic.net
  RFC4712          ||      A. Siddiqui, D. Romascanu, E. Golovinsky, M. Rahman,Y. Kim         ||       anwars@avaya.com, dromasca@gmail.com , gene@alertlogic.net, none, ybkim@broadcom.com
  RFC4713          ||      X. Lee, W. Mao, E. Chen, N. Hsu, J. Klensin         ||       lee@cnnic.cn, mao@cnnic.cn, erin@twnic.net.tw, snw@twnic.net.tw, john+ietf@jck.com
  RFC4714          ||      A. Mankin, S. Hayes         ||       mankin@psg.com, stephen.hayes@ericsson.com
  RFC4715          ||      M. Munakata, S. Schubert, T. Ohba         ||       munakata.mayumi@lab.ntt.co.jp, shida@ntt-at.com, ohba.takumi@lab.ntt.co.jp
  RFC4716          ||      J. Galbraith, R. Thayer         ||       galb@vandyke.com, rodney@canola-jones.com
  RFC4717          ||      L. Martini, J. Jayakumar, M. Bocci, N. El-Aawar, J. Brayley, G. Koleyni         ||       lmartini@cisco.com, jjayakum@cisco.com, matthew.bocci@alcatel.co.uk, nna@level3.net, jeremy.brayley@ecitele.com, ghassem@nortelnetworks.com
  RFC4718          ||      P. Eronen, P. Hoffman         ||       pe@iki.fi, paul.hoffman@vpnc.org
  RFC4719          ||      R. Aggarwal, Ed., M. Townsley, Ed., M. Dos Santos, Ed.         ||       rahul@juniper.net, mark@townsley.net, mariados@cisco.com
  RFC4720          ||      A. Malis, D. Allan, N. Del Regno         ||       Andy.Malis@tellabs.com, dallan@nortelnetworks.com, nick.delregno@mci.com
  RFC4721          ||      C. Perkins, P. Calhoun, J. Bharatia         ||       charles.perkins@nokia.com, pcalhoun@cisco.com, jayshree@nortel.com
  RFC4722          ||      J. Van Dyke, E. Burger, Ed., A. Spitzer         ||       jvandyke@cantata.com, eburger@cantata.com, woof@pingtel.com
  RFC4723          ||      T. Kosonen, T. White         ||       timo.kosonen@nokia.com, twhite@midi.org
  RFC4724          ||      S. Sangli, E. Chen, R. Fernando, J. Scudder, Y. Rekhter         ||       rsrihari@cisco.com, enkechen@cisco.com, rex@juniper.net, jgs@juniper.net, yakov@juniper.net
  RFC4725          ||      A. Mayrhofer, B. Hoeneisen         ||       alexander.mayrhofer@enum.at, b.hoeneisen@ieee.org
  RFC4726          ||      A. Farrel, J.-P. Vasseur, A. Ayyangar         ||       adrian@olddog.co.uk, jpv@cisco.com, arthi@nuovasystems.com
  RFC4727          ||      B. Fenner         ||       fenner@research.att.com
  RFC4728          ||      D. Johnson, Y. Hu, D. Maltz         ||       dbj@cs.rice.edu, yihchun@uiuc.edu, dmaltz@cs.cmu.edu
  RFC4729          ||      M. Abel         ||       TPM@nfc-forum.org
  RFC4730          ||      E. Burger, M. Dolly         ||       eburger@cantata.com, mdolly@att.com
  RFC4731          ||      A. Melnikov, D. Cridland         ||       Alexey.Melnikov@isode.com, dave.cridland@inventuresystems.co.uk
  RFC4732          ||      M. Handley, Ed., E. Rescorla, Ed., IAB         ||       M.Handley@cs.ucl.ac.uk, ekr@networkresonance.com, iab@ietf.org
  RFC4733          ||      H. Schulzrinne, T. Taylor         ||       schulzrinne@cs.columbia.edu, tom.taylor.stds@gmail.com
  RFC4734          ||      H. Schulzrinne, T. Taylor         ||       schulzrinne@cs.columbia.edu, tom.taylor.stds@gmail.com
  RFC4735          ||      T. Taylor         ||       tom.taylor.stds@gmail.com
  RFC4736          ||      JP. Vasseur, Ed., Y. Ikejiri, R. Zhang         ||       jpv@cisco.com, y.ikejiri@ntt.com, raymond_zhang@bt.infonet.com
  RFC4737          ||      A. Morton, L. Ciavattone, G. Ramachandran, S. Shalunov, J. Perser         ||       acmorton@att.com, lencia@att.com, gomathi@att.com, shalunov@internet2.edu, jperser@veriwave.com
  RFC4738          ||      D. Ignjatic, L. Dondeti, F. Audet, P. Lin         ||       dignjatic@polycom.com, dondeti@qualcomm.com,  audet@nortel.com, linping@nortel.com
  RFC4739          ||      P. Eronen, J. Korhonen         ||       pe@iki.fi, jouni.korhonen@teliasonera.com
  RFC4740          ||      M. Garcia-Martin, Ed., M. Belinchon, M. Pallares-Lopez, C. Canales-Valenzuela, K. Tammi         ||       miguel.an.garcia@nokia.com, maria.carmen.belinchon@ericsson.com, miguel-angel.pallares@ericsson.com, carolina.canales@ericsson.com, kalle.tammi@nokia.com
  RFC4741          ||      R. Enns, Ed.         ||       rpe@juniper.net
  RFC4742          ||      M. Wasserman, T. Goddard         ||       margaret@thingmagic.com, ted.goddard@icesoft.com
  RFC4743          ||      T. Goddard         ||       ted.goddard@icesoft.com
  RFC4744          ||      E. Lear, K. Crozier         ||       lear@cisco.com, ken.crozier@gmail.com
  RFC4745          ||      H. Schulzrinne, H. Tschofenig, J. Morris, J. Cuellar, J. Polk, J. Rosenberg         ||       schulzrinne@cs.columbia.edu, Hannes.Tschofenig@siemens.com, jmorris@cdt.org, Jorge.Cuellar@siemens.com, jmpolk@cisco.com, jdrosen@cisco.com
  RFC4746          ||      T. Clancy, W. Arbaugh         ||       clancy@ltsnet.net, waa@cs.umd.edu
  RFC4747          ||      S. Kipp, G. Ramkumar, K. McCloghrie         ||       scott.kipp@mcdata.com, gramkumar@stanfordalumni.org, kzm@cisco.com
  RFC4748          ||      S. Bradner, Ed.         ||       sob@harvard.edu
  RFC4749          ||      A. Sollaud         ||       aurelien.sollaud@orange-ft.com
  RFC4750          ||      D. Joyal, Ed., P. Galecki, Ed., S. Giacalone, Ed., R. Coltun, F. Baker         ||       djoyal@nortel.com, pgalecki@airvana.com, spencer.giacalone@gmail.com, fred@cisco.com
  RFC4752          ||      A. Melnikov, Ed.         ||       Alexey.Melnikov@isode.com
  RFC4753          ||      D. Fu, J. Solinas         ||       defu@orion.ncsc.mil, jasolin@orion.ncsc.mil
  RFC4754          ||      D. Fu, J. Solinas         ||       defu@orion.ncsc.mil, jasolin@orion.ncsc.mil
  RFC4755          ||      V. Kashyap         ||       vivk@us.ibm.com
  RFC4756          ||      A. Li         ||       adamli@hyervision.com
  RFC4757          ||      K. Jaganathan, L. Zhu, J. Brezak         ||       karthikj@microsoft.com, lzhu@microsoft.com, jbrezak@microsoft.com
  RFC4758          ||      M. Nystroem         ||       magnus@rsasecurity.com
  RFC4759          ||      R. Stastny, R. Shockey, L. Conroy         ||       Richard.stastny@oefeg.at, richard.shockey@neustar.biz, lconroy@insensate.co.uk
  RFC4760          ||      T. Bates, R. Chandra, D. Katz, Y. Rekhter         ||       tbates@cisco.com, rchandra@sonoasystems.com, dkatz@juniper.com, yakov@juniper.com
  RFC4761          ||      K. Kompella, Ed., Y. Rekhter, Ed.         ||       kireeti@juniper.net, yakov@juniper.net
  RFC4762          ||      M. Lasserre, Ed., V. Kompella, Ed.         ||       mlasserre@alcatel-lucent.com, vach.kompella@alcatel-lucent.com
  RFC4763          ||      M. Vanderveen, H. Soliman         ||       mvandervn@yahoo.com, solimanhs@gmail.com
  RFC4764          ||      F. Bersani, H. Tschofenig         ||       bersani_florent@yahoo.fr, Hannes.Tschofenig@siemens.com
  RFC4765          ||      H. Debar, D. Curry, B. Feinstein         ||       herve.debar@orange-ftgroup.com, david_a_curry@glic.com, feinstein@acm.org
  RFC4766          ||      M. Wood, M. Erlinger         ||       mark1@iss.net, mike@cs.hmc.edu
  RFC4767          ||      B. Feinstein, G. Matthews         ||       bfeinstein@acm.org, gmatthew@nas.nasa.gov
  RFC4768          ||      S. Hartman         ||       hartmans-ietf@mit.edu
  RFC4769          ||      J. Livingood, R. Shockey         ||       jason_livingood@cable.comcast.com, richard.shockey@neustar.biz
  RFC4770          ||      C. Jennings, J. Reschke, Ed.         ||       fluffy@cisco.com, julian.reschke@greenbytes.de
  RFC4771          ||      V. Lehtovirta, M. Naslund, K. Norrman         ||       vesa.lehtovirta@ericsson.com, mats.naslund@ericsson.com, karl.norrman@ericsson.com
  RFC4772          ||      S. Kelly         ||       scott@hyperthought.com
  RFC4773          ||      G. Huston         ||       gih@apnic.net
  RFC4774          ||      S. Floyd         ||       floyd@icir.org
  RFC4775          ||      S. Bradner, B. Carpenter, Ed., T. Narten         ||       sob@harvard.edu, brc@zurich.ibm.com, narten@us.ibm.com
  RFC4776          ||      H. Schulzrinne         ||       hgs+geopriv@cs.columbia.edu
  RFC4777          ||      T. Murphy Jr., P. Rieth, J. Stevens         ||       murphyte@us.ibm.com, rieth@us.ibm.com, jssteven@us.ibm.com
  RFC4778          ||      M. Kaeo         ||       merike@doubleshotsecurity.com
  RFC4779          ||      S. Asadullah, A. Ahmed, C. Popoviciu, P. Savola, J. Palet         ||       sasad@cisco.com, adahmed@cisco.com, cpopovic@cisco.com, psavola@funet.fi, jordi.palet@consulintel.es
  RFC4780          ||      K. Lingle, J-F. Mule, J. Maeng, D. Walker         ||       klingle@cisco.com, jf.mule@cablelabs.com, jmaeng@austin.rr.com, drwalker@rogers.com
  RFC4781          ||      Y. Rekhter, R. Aggarwal         ||        yakov@juniper.net, rahul@juniper.net
  RFC4782          ||      S. Floyd, M. Allman, A. Jain, P. Sarolahti         ||       floyd@icir.org, mallman@icir.org, a.jain@f5.com, pasi.sarolahti@iki.fi
  RFC4783          ||      L. Berger, Ed.         ||       lberger@labn.net
  RFC4784          ||      C. Carroll, F. Quick         ||       Christopher.Carroll@ropesgray.com, fquick@qualcomm.com
  RFC4785          ||      U. Blumenthal, P. Goel         ||       urimobile@optonline.net, Purushottam.Goel@intel.com
  RFC4786          ||      J. Abley, K. Lindqvist         ||       jabley@ca.afilias.info, kurtis@kurtis.pp.se
  RFC4787          ||      F. Audet, Ed., C. Jennings         ||       audet@nortel.com, fluffy@cisco.com
  RFC4788          ||      Q. Xie, R. Kapoor         ||       Qiaobing.Xie@Motorola.com, rkapoor@qualcomm.com
  RFC4789          ||      J. Schoenwaelder, T. Jeffree         ||       j.schoenwaelder@iu-bremen.de, tony@jeffree.co.uk
  RFC4790          ||      C. Newman, M. Duerst,  A. Gulbrandsen         ||       chris.newman@sun.com, duerst@it.aoyama.ac.jp, arnt@oryx.com
  RFC4791          ||      C. Daboo, B. Desruisseaux, L. Dusseault         ||       cyrus@daboo.name, bernard.desruisseaux@oracle.com, lisa.dusseault@gmail.com
  RFC4792          ||      S. Legg         ||       steven.legg@eb2bcom.com
  RFC4793          ||      M. Nystroem         ||       magnus@rsasecurity.com
  RFC4794          ||      B. Fenner         ||       fenner@research.att.com
  RFC4795          ||      B. Aboba, D. Thaler, L. Esibov         ||       bernarda@microsoft.com, dthaler@microsoft.com, levone@microsoft.com
  RFC4796          ||      J. Hautakorpi, G. Camarillo         ||       Jani.Hautakorpi@ericsson.com, Gonzalo.Camarillo@ericsson.com
  RFC4797          ||      Y. Rekhter, R. Bonica, E. Rosen         ||       yakov@juniper.net, rbonica@juniper.net, erosen@cisco.com
  RFC4798          ||      J. De Clercq, D. Ooms, S. Prevost, F. Le Faucheur         ||       jeremy.de_clercq@alcatel-lucent.be, dirk@onesparrow.com, stuart.prevost@bt.com, flefauch@cisco.com
  RFC4801          ||      T. Nadeau, Ed., A. Farrel, Ed.         ||       tnadeau@cisco.com, adrian@olddog.co.uk
  RFC4802          ||      T. Nadeau, Ed., A. Farrel,  Ed.         ||       tnadeau@cisco.com, adrian@olddog.co.uk
  RFC4803          ||      T. Nadeau, Ed., A. Farrel, Ed.         ||       tnadeau@cisco.com, adrian@olddog.co.uk
  RFC4804          ||      F. Le Faucheur, Ed.         ||       flefauch@cisco.com
  RFC4805          ||      O. Nicklass, Ed.         ||       orly_n@rad.com
  RFC4806          ||      M. Myers, H. Tschofenig         ||       mmyers@fastq.com, Hannes.Tschofenig@siemens.com
  RFC4807          ||      M. Baer, R. Charlet, W. Hardaker, R. Story, C. Wang         ||       baerm@tislabs.com, rcharlet@alumni.calpoly.edu, hardaker@tislabs.com, rstory@ipsp.revelstone.com, cliffwangmail@yahoo.com
  RFC4808          ||      S. Bellovin         ||       bellovin@acm.org
  RFC4809          ||      C. Bonatti, Ed., S. Turner, Ed., G. Lebovitz, Ed.         ||       Bonattic@ieca.com, Turners@ieca.com, gregory.ietf@gmail.com
  RFC4810          ||      C. Wallace, U. Pordesch, R. Brandner         ||       cwallace@cygnacom.com, ulrich.pordesch@zv.fraunhofer.de, ralf.brandner@intercomponentware.com
  RFC4811          ||      L. Nguyen, A. Roy, A. Zinin         ||       lhnguyen@cisco.com, akr@cisco.com, alex.zinin@alcatel-lucent.com
  RFC4812          ||      L. Nguyen, A. Roy, A. Zinin         ||       lhnguyen@cisco.com, akr@cisco.com, alex.zinin@alcatel-lucent.com
  RFC4813          ||      B. Friedman, L. Nguyen, A. Roy, D. Yeung, A. Zinin         ||       friedman@cisco.com, lhnguyen@cisco.com, akr@cisco.com, myeung@cisco.com, alex.zinin@alcatel-lucent.com
  RFC4814          ||      D. Newman, T. Player         ||       dnewman@networktest.com, timmons.player@spirent.com
  RFC4815          ||      L-E. Jonsson, K. Sandlund, G. Pelletier, P. Kremer         ||       lars-erik.jonsson@ericsson.com, kristofer.sandlund@ericsson.com, ghyslain.pelletier@ericsson.com, peter.kremer@ericsson.com
  RFC4816          ||      A. Malis, L. Martini, J. Brayley, T. Walsh         ||       andrew.g.malis@verizon.com, lmartini@cisco.com, jeremy.brayley@ecitele.com, twalsh@juniper.net
  RFC4817          ||      M. Townsley, C. Pignataro, S. Wainner, T. Seely, J. Young         ||       mark@townsley.net, cpignata@cisco.com, swainner@cisco.com, tseely@sprint.net, young@jsyoung.net
  RFC4818          ||      J. Salowey, R. Droms         ||       jsalowey@cisco.com, rdroms@cisco.com
  RFC4819          ||      J. Galbraith, J. Van Dyke, J. Bright         ||       galb@vandyke.com, jpv@vandyke.com, jon@siliconcircus.com
  RFC4820          ||      M. Tuexen, R. Stewart, P. Lei         ||       tuexen@fh-muenster.de, randall@lakerest.net, peterlei@cisco.com
  RFC4821          ||      M. Mathis, J. Heffner         ||       mathis@psc.edu, jheffner@psc.edu
  RFC4822          ||      R. Atkinson, M. Fanto         ||       rja@extremenetworks.com, mattjf@umd.edu
  RFC4823          ||      T. Harding, R. Scott         ||       tharding@us.axway.com, rscott@us.axway.com
  RFC4824          ||      J. Hofmueller, Ed., A. Bachmann, Ed., IO. zmoelnig, Ed.         ||       ip-sfs@mur.at, ip-sfs@mur.at, ip-sfs@mur.at
  RFC4825          ||      J. Rosenberg         ||       jdrosen@cisco.com
  RFC4826          ||      J. Rosenberg         ||       jdrosen@cisco.com
  RFC4827          ||      M. Isomaki, E. Leppanen         ||       markus.isomaki@nokia.com, eva-maria.leppanen@nokia.com
  RFC4828          ||      S. Floyd, E. Kohler         ||       floyd@icir.org, kohler@cs.ucla.edu
  RFC4829          ||      J. de Oliveira, Ed., JP. Vasseur, Ed., L. Chen, C. Scoglio         ||       jau@ece.drexel.edu, jpv@cisco.com, leonardo.c.chen@verizon.com, caterina@eece.ksu.edu
  RFC4830          ||      J. Kempf, Ed.         ||       kempf@docomolabs-usa.com
  RFC4831          ||      J. Kempf, Ed.         ||       kempf@docomolabs-usa.com
  RFC4832          ||      C. Vogt, J. Kempf         ||       chvogt@tm.uka.de, kempf@docomolabs-usa.com
  RFC4833          ||      E. Lear, P. Eggert         ||       lear@cisco.com, eggert@cs.ucla.edu
  RFC4834          ||      T. Morin, Ed.         ||       thomas.morin@orange-ftgroup.com
  RFC4835          ||      V. Manral         ||       vishwas@ipinfusion.com
  RFC4836          ||      E. Beili         ||       edward.beili@actelis.com
  RFC4837          ||      L. Khermosh         ||       lior_khermosh@pmc-sierra.com
  RFC4838          ||      V. Cerf, S. Burleigh, A. Hooke, L. Torgerson, R. Durst, K. Scott, K. Fall, H. Weiss         ||       vint@google.com, Scott.Burleigh@jpl.nasa.gov, Adrian.Hooke@jpl.nasa.gov, ltorgerson@jpl.nasa.gov, durst@mitre.org, kscott@mitre.org, kfall@intel.com, howard.weiss@sparta.com
  RFC4839          ||      G. Conboy, J. Rivlin, J. Ferraiolo         ||       gc@ebooktechnologies.com, john@ebooktechnologies.com, jferrai@us.ibm.com
  RFC4840          ||      B. Aboba, Ed., E. Davies, D. Thaler         ||       bernarda@microsoft.com, elwynd@dial.pipex.com, dthaler@microsoft.com
  RFC4841          ||      C. Heard, Ed.         ||       heard@pobox.com
  RFC4842          ||      A. Malis, P. Pate, R. Cohen, Ed., D. Zelig         ||       andrew.g.malis@verizon.com, prayson.pate@overturenetworks.com, ronc@resolutenetworks.com, davidz@corrigent.com
  RFC4843          ||      P. Nikander, J. Laganier, F. Dupont         ||       pekka.nikander@nomadiclab.com, julien.ietf@laposte.net, Francis.Dupont@fdupont.fr
  RFC4844          ||      L. Daigle, Ed., Internet Architecture Board         ||       leslie@thinkingcat.com, iab@iab.org
  RFC4845          ||      L. Daigle, Ed., Internet Architecture Board         ||       leslie@thinkingcat.com, iab@iab.org
  RFC4846          ||      J. Klensin, Ed., D. Thaler, Ed.         ||       john-ietf@jck.com, dthaler@microsoft.com
  RFC4847          ||      T. Takeda, Ed.         ||       takeda.tomonori@lab.ntt.co.jp
  RFC4848          ||      L. Daigle         ||       leslie@thinkingcat.com
  RFC4849          ||      P. Congdon, M. Sanchez, B. Aboba         ||       paul.congdon@hp.com, mauricio.sanchez@hp.com, bernarda@microsoft.com
  RFC4850          ||      D. Wysochanski         ||       wysochanski@pobox.com
  RFC4851          ||      N. Cam-Winget, D. McGrew, J. Salowey, H. Zhou         ||       ncamwing@cisco.com, mcgrew@cisco.com, jsalowey@cisco.com, hzhou@cisco.com
  RFC4852          ||      J. Bound, Y. Pouffary, S. Klynsma, T. Chown, D. Green         ||       jim.bound@hp.com, Yanick.pouffary@hp.com, tjc@ecs.soton.ac.uk, green@commandinformation.com, sklynsma@mitre.org
  RFC4853          ||      R. Housley         ||       housley@vigilsec.com
  RFC4854          ||      P. Saint-Andre         ||       ietf@stpeter.im
  RFC4855          ||      S. Casner         ||       casner@acm.org
  RFC4856          ||      S. Casner         ||       casner@acm.org
  RFC4857          ||      E. Fogelstroem, A. Jonsson, C. Perkins         ||       eva.fogelstrom@ericsson.com, annika.jonsson@ericsson.com, charles.perkins@nsn.com
  RFC4858          ||      H. Levkowetz, D. Meyer, L. Eggert, A. Mankin         ||       henrik@levkowetz.com, dmm@1-4-5.net, lars.eggert@nokia.com, mankin@psg.com
  RFC4859          ||      A. Farrel         ||       adrian@olddog.co.uk
  RFC4860          ||      F. Le Faucheur, B. Davie, P. Bose, C. Christou, M. Davenport         ||       flefauch@cisco.com, bds@cisco.com, pratik.bose@lmco.com, christou_chris@bah.com, davenport_michael@bah.com
  RFC4861          ||      T. Narten, E. Nordmark, W. Simpson, H. Soliman         ||       narten@us.ibm.com, erik.nordmark@sun.com, william.allen.simpson@gmail.com, hesham@elevatemobile.com
  RFC4862          ||      S. Thomson, T. Narten, T. Jinmei         ||       sethomso@cisco.com, narten@us.ibm.com, jinmei@isl.rdc.toshiba.co.jp
  RFC4863          ||      L. Martini, G. Swallow         ||       lmartini@cisco.com, swallow@cisco.com
  RFC4864          ||      G. Van de Velde, T. Hain, R. Droms, B. Carpenter, E. Klein         ||       gunter@cisco.com, alh-ietf@tndh.net, rdroms@cisco.com, brc@zurich.ibm.com, ericlklein.ipv6@gmail.com
  RFC4865          ||      G. White, G. Vaudreuil         ||       g.a.white@comcast.net, GregV@ieee.org
  RFC4866          ||      J. Arkko, C. Vogt, W. Haddad         ||       jari.arkko@ericsson.com, chvogt@tm.uka.de, wassim.haddad@ericsson.com
  RFC4867          ||      J. Sjoberg, M. Westerlund, A. Lakaniemi, Q. Xie         ||       Johan.Sjoberg@ericsson.com, Magnus.Westerlund@ericsson.com, ari.lakaniemi@nokia.com, Qiaobing.Xie@motorola.com
  RFC4868          ||      S. Kelly, S. Frankel         ||       scott@hyperthought.com, sheila.frankel@nist.gov
  RFC4869          ||      L. Law, J. Solinas         ||       lelaw@orion.ncsc.mil, jasolin@orion.ncsc.mil
  RFC4870          ||      M. Delany         ||       markd+domainkeys@yahoo-inc.com
  RFC4871          ||      E. Allman, J. Callas, M. Delany, M. Libbey, J. Fenton, M. Thomas         ||       eric+dkim@sendmail.org, jon@pgp.com, markd+dkim@yahoo-inc.com, mlibbeymail-mailsig@yahoo.com, fenton@bluepopcorn.net, mat@cisco.com
  RFC4872          ||      J.P. Lang, Ed., Y. Rekhter, Ed., D. Papadimitriou, Ed.         ||       jplang@ieee.org, yakov@juniper.net, dimitri.papadimitriou@alcatel-lucent.be
  RFC4873          ||      L. Berger, I. Bryskin, D. Papadimitriou, A. Farrel         ||       lberger@labn.net, IBryskin@advaoptical.com, dimitri.papadimitriou@alcatel-lucent.be, adrian@olddog.co.uk
  RFC4874          ||      CY. Lee, A. Farrel, S. De Cnodder         ||       c.yin.lee@gmail.com, adrian@olddog.co.uk, stefaan.de_cnodder@alcatel-lucent.be
  RFC4875          ||      R. Aggarwal, Ed., D. Papadimitriou, Ed., S. Yasukawa, Ed.         ||       rahul@juniper.net, yasukawa.seisho@lab.ntt.co.jp, Dimitri.Papadimitriou@alcatel-lucent.be
  RFC4876          ||      B. Neal-Joslin, Ed., L. Howard, M. Ansari         ||       bob_joslin@hp.com, lukeh@padl.com, morteza@infoblox.com
  RFC4877          ||      V. Devarapalli, F. Dupont         ||       vijay.devarapalli@azairenet.com, Francis.Dupont@fdupont.fr
  RFC4878          ||      M. Squire         ||       msquire@hatterasnetworks.com
  RFC4879          ||      T. Narten         ||       narten@us.ibm.com
  RFC4880          ||      J. Callas, L. Donnerhacke, H. Finney, D. Shaw, R. Thayer         ||       jon@callas.org, lutz@iks-jena.de, hal@finney.org, dshaw@jabberwocky.com, rodney@canola-jones.com
  RFC4881          ||      K. El Malki, Ed.         ||       karim@athonet.com
  RFC4882          ||      R. Koodli         ||       rajeev.koodli@nokia.com
  RFC4883          ||      G. Feher, K. Nemeth, A. Korn, I. Cselenyi         ||       Gabor.Feher@tmit.bme.hu, Krisztian.Nemeth@tmit.bme.hu, Andras.Korn@tmit.bme.hu, Istvan.Cselenyi@teliasonera.com
  RFC4884          ||      R. Bonica, D. Gan, D. Tappan, C. Pignataro         ||       rbonica@juniper.net, derhwagan@yahoo.com, Dan.Tappan@gmail.com, cpignata@cisco.com
  RFC4885          ||      T. Ernst, H-Y. Lach         ||       thierry.ernst@inria.fr, hong-yon.lach@motorola.com
  RFC4886          ||      T. Ernst         ||       thierry.ernst@inria.fr
  RFC4887          ||      P. Thubert, R. Wakikawa, V. Devarapalli         ||       pthubert@cisco.com, ryuji@sfc.wide.ad.jp, vijay.devarapalli@azairenet.com
  RFC4888          ||      C. Ng, P. Thubert, M. Watari, F. Zhao         ||       chanwah.ng@sg.panasonic.com, pthubert@cisco.com, watari@kddilabs.jp, fanzhao@ucdavis.edu
  RFC4889          ||      C. Ng, F. Zhao, M. Watari, P. Thubert         ||       chanwah.ng@sg.panasonic.com, fanzhao@ucdavis.edu, watari@kddilabs.jp, pthubert@cisco.com
  RFC4890          ||      E. Davies, J. Mohacsi         ||       elwynd@dial.pipex.com, mohacsi@niif.hu
  RFC4891          ||      R. Graveman, M. Parthasarathy, P. Savola, H. Tschofenig         ||       rfg@acm.org, mohanp@sbcglobal.net, psavola@funet.fi, Hannes.Tschofenig@nsn.com
  RFC4892          ||      S. Woolf, D. Conrad         ||       woolf@isc.org, david.conrad@icann.org
  RFC4893          ||      Q. Vohra, E. Chen         ||       quaizar.vohra@gmail.com, enkechen@cisco.com
  RFC4894          ||      P. Hoffman         ||       paul.hoffman@vpnc.org
  RFC4895          ||      M. Tuexen, R. Stewart, P. Lei, E. Rescorla         ||       tuexen@fh-muenster.de, randall@lakerest.net, peterlei@cisco.com, ekr@rtfm.com
  RFC4896          ||      A. Surtees, M. West, A.B. Roach         ||       abigail.surtees@roke.co.uk, mark.a.west@roke.co.uk, adam@estacado.net
  RFC4897          ||      J. Klensin, S. Hartman         ||       john-ietf@jck.com, hartmans-ietf@mit.edu
  RFC4898          ||      M. Mathis, J. Heffner, R. Raghunarayan         ||       mathis@psc.edu, jheffner@psc.edu, raraghun@cisco.com
  RFC4901          ||      J. Ash, Ed., J. Hand, Ed., A. Malis, Ed.         ||       gash5107@yahoo.com, jameshand@att.com, andrew.g.malis@verizon.com
  RFC4902          ||      M. Stecher         ||        martin.stecher@webwasher.com
  RFC4903          ||      D. Thaler         ||       dthaler@microsoft.com
  RFC4904          ||      V. Gurbani, C. Jennings         ||       vkg@alcatel-lucent.com, fluffy@cisco.com
  RFC4905          ||      L. Martini, Ed., E. Rosen, Ed., N. El-Aawar, Ed.         ||       lmartini@cisco.com, erosen@cisco.com, nna@level3.net
  RFC4906          ||      L. Martini, Ed., E. Rosen, Ed., N. El-Aawar, Ed.         ||       lmartini@cisco.com, erosen@cisco.com, nna@level3.net
  RFC4907          ||      B. Aboba, Ed.         ||       bernarda@microsoft.com
  RFC4908          ||      K. Nagami, S. Uda, N. Ogashiwa, H. Esaki, R. Wakikawa, H. Ohnishi         ||       nagami@inetcore.com, zin@jaist.ac.jp, ogashiwa@wide.ad.jp, hiroshi@wide.ad.jp, ryuji@sfc.wide.ad.jp, ohnishi.hiroyuki@lab.ntt.co.jp
  RFC4909          ||      L. Dondeti, Ed., D. Castleford, F. Hartung         ||       ldondeti@qualcomm.com, david.castleford@orange-ftgroup.com, frank.hartung@ericsson.com
  RFC4910          ||      S. Legg, D. Prager         ||       steven.legg@eb2bcom.com, dap@austhink.com
  RFC4911          ||      S. Legg         ||       steven.legg@eb2bcom.com
  RFC4912          ||      S. Legg         ||       steven.legg@eb2bcom.com
  RFC4913          ||      S. Legg         ||       steven.legg@eb2bcom.com
  RFC4914          ||      S. Legg         ||       steven.legg@eb2bcom.com
  RFC4915          ||      P. Psenak, S. Mirtorabi, A. Roy, L. Nguyen, P. Pillay-Esnault         ||       ppsenak@cisco.com, sina@force10networks.com, akr@cisco.com, lhnguyen@cisco.com, ppe@cisco.com
  RFC4916          ||      J. Elwell         ||       john.elwell@siemens.com
  RFC4917          ||      V. Sastry, K. Leung, A. Patel         ||       venkat.s@samsung.com, kleung@cisco.com, alpesh@cisco.com
  RFC4918          ||      L. Dusseault, Ed.         ||       lisa.dusseault@gmail.com
  RFC4919          ||      N. Kushalnagar, G. Montenegro, C. Schumacher         ||       nandakishore.kushalnagar@intel.com, gabriel.montenegro@microsoft.com, schumacher@danfoss.com
  RFC4920          ||      A. Farrel, Ed., A. Satyanarayana, A. Iwata, N. Fujita, G. Ash         ||       adrian@olddog.co.uk, asatyana@cisco.com, a-iwata@ah.jp.nec.com, n-fujita@bk.jp.nec.com, gash5107@yahoo.com
  RFC4923          ||      F. Baker, P. Bose         ||       fred@cisco.com, pratik.bose@lmco.com
  RFC4924          ||      B. Aboba, Ed., E. Davies         ||       bernarda@microsoft.com, elwynd@dial.pipex.com
  RFC4925          ||      X. Li, Ed., S. Dawkins, Ed., D. Ward, Ed., A. Durand, Ed.         ||       xing@cernet.edu.cn, spencer@mcsr-labs.org, dward@cisco.com, alain_durand@cable.comcast.com
  RFC4926          ||      T.Kalin, M.Molina         ||       tomaz.kalin@dante.org.uk, maurizio.molina@dante.org.uk
  RFC4927          ||      J.-L. Le Roux, Ed.         ||       jeanlouis.leroux@orange-ftgroup.com
  RFC4928          ||      G. Swallow, S. Bryant, L. Andersson         ||       stbryant@cisco.com, swallow@cisco.com, loa@pi.se
  RFC4929          ||      L. Andersson, Ed., A. Farrel, Ed.         ||       loa@pi.se, adrian@olddog.co.uk
  RFC4930          ||      S. Hollenbeck         ||       shollenbeck@verisign.com
  RFC4931          ||      S. Hollenbeck         ||       shollenbeck@verisign.com
  RFC4932          ||      S. Hollenbeck         ||       shollenbeck@verisign.com
  RFC4933          ||      S. Hollenbeck         ||       shollenbeck@verisign.com
  RFC4934          ||      S. Hollenbeck         ||       shollenbeck@verisign.com
  RFC4935          ||      C. DeSanti, H.K. Vivek, K. McCloghrie, S. Gai         ||       cds@cisco.com, hvivek@cisco.com, kzm@cisco.com, sgai@nuovasystems.com
  RFC4936          ||      C. DeSanti, H.K. Vivek, K. McCloghrie, S. Gai         ||       cds@cisco.com, hvivek@cisco.com, kzm@cisco.com, sgai@nuovasystems.com
  RFC4937          ||      P. Arberg, V. Mammoliti         ||       parberg@redback.com, vince@cisco.com
  RFC4938          ||      B. Berry, H. Holgate         ||       bberry@cisco.com, hholgate@cisco.com
  RFC4939          ||      K. Gibbons, G. Ramkumar, S. Kipp         ||       kgibbons@yahoo.com, gramkumar@stanfordalumni.org, skipp@brocade.com
  RFC4940          ||      K. Kompella, B. Fenner         ||       kireeti@juniper.net, fenner@research.att.com
  RFC4941          ||      T. Narten, R. Draves, S. Krishnan         ||       narten@us.ibm.com, richdr@microsoft.com, suresh.krishnan@ericsson.com
  RFC4942          ||      E. Davies, S. Krishnan, P. Savola         ||       elwynd@dial.pipex.com, suresh.krishnan@ericsson.com, psavola@funet.fi
  RFC4943          ||      S. Roy, A. Durand, J. Paugh         ||       sebastien.roy@sun.com, alain_durand@cable.comcast.com, jim.paugh@nominum.com
  RFC4944          ||      G. Montenegro, N. Kushalnagar, J. Hui, D. Culler         ||       gabriel.montenegro@microsoft.com, nandakishore.kushalnagar@intel.com, jhui@archrock.com, dculler@archrock.com
  RFC4945          ||      B. Korver         ||       briank@networkresonance.com
  RFC4946          ||      J. Snell         ||       jasnell@gmail.com
  RFC4947          ||      G. Fairhurst, M. Montpetit         ||       gorry@erg.abdn.ac.uk, mmontpetit@motorola.com
  RFC4948          ||      L. Andersson, E. Davies, L. Zhang         ||       loa@pi.se, elwynd@dial.pipex.com, lixia@cs.ucla.edu
  RFC4949          ||      R. Shirey         ||       rwshirey4949@verizon.net
  RFC4950          ||      R. Bonica, D. Gan, D. Tappan, C. Pignataro         ||       rbonica@juniper.net, derhwagan@yahoo.com, dan.tappan@gmail.com, cpignata@cisco.com
  RFC4951          ||      V. Jain, Ed.         ||       vipinietf@yahoo.com
  RFC4952          ||      J. Klensin, Y. Ko         ||       john-ietf@jck.com, yw@mrko.pe.kr
  RFC4953          ||      J. Touch         ||       touch@isi.edu
  RFC4954          ||      R. Siemborski, Ed., A. Melnikov, Ed.         ||       robsiemb@google.com, Alexey.Melnikov@isode.com
  RFC4955          ||      D. Blacka         ||       davidb@verisign.com
  RFC4956          ||      R. Arends, M. Kosters, D. Blacka         ||       roy@nominet.org.uk, markk@verisign.com, davidb@verisign.com
  RFC4957          ||      S. Krishnan, Ed., N. Montavont, E. Njedjou, S. Veerepalli, A. Yegin, Ed.         ||       suresh.krishnan@ericsson.com, nicolas.montavont@enst-bretagne.fr, eric.njedjou@orange-ftgroup.com, sivav@qualcomm.com, a.yegin@partner.samsung.com
  RFC4958          ||      K. Carlberg         ||       carlberg@g11.org.uk
  RFC4959          ||      R. Siemborski, A. Gulbrandsen         ||       robsiemb@google.com, arnt@oryx.com
  RFC4960          ||      R. Stewart, Ed.         ||       randall@lakerest.net
  RFC4961          ||      D. Wing         ||       dwing-ietf@fuggles.com
  RFC4962          ||      R. Housley, B. Aboba         ||       housley@vigilsec.com, bernarda@microsoft.com
  RFC4963          ||      J. Heffner, M. Mathis, B. Chandler         ||       jheffner@psc.edu, mathis@psc.edu, bchandle@gmail.com
  RFC4964          ||      A. Allen, Ed., J. Holm, T. Hallin         ||       aallen@rim.com, Jan.Holm@ericsson.com, thallin@motorola.com
  RFC4965          ||      J-F. Mule, W. Townsley         ||       jf.mule@cablelabs.com, mark@townsley.net
  RFC4966          ||      C. Aoun, E. Davies         ||       ietf@energizeurnet.com, elwynd@dial.pipex.com
  RFC4967          ||      B. Rosen         ||       br@brianrosen.net
  RFC4968          ||      S. Madanapalli, Ed.         ||       smadanapalli@gmail.com
  RFC4969          ||      A. Mayrhofer         ||       alexander.mayrhofer@enum.at
  RFC4970          ||      A. Lindem, Ed., N. Shen, JP. Vasseur, R. Aggarwal, S. Shaffer         ||       acee@redback.com, naiming@cisco.com, jpv@cisco.com, rahul@juniper.net, sshaffer@bridgeport-networks.com
  RFC4971          ||      JP. Vasseur, Ed., N. Shen, Ed., R. Aggarwal, Ed.         ||       jpv@cisco.com, naiming@cisco.com, rahul@juniper.net
  RFC4972          ||      JP. Vasseur, Ed., JL. Leroux, Ed., S. Yasukawa, S. Previdi, P. Psenak, P. Mabbey         ||       jpv@cisco.com, jeanlouis.leroux@orange-ftgroup.com, s.yasukawa@hco.ntt.co.jp, sprevidi@cisco.com, ppsenak@cisco.com, Paul_Mabey@cable.comcast.com
  RFC4973          ||      P. Srisuresh, P. Joseph         ||       srisuresh@yahoo.com, paul_95014@yahoo.com
  RFC4974          ||      D. Papadimitriou, A. Farrel         ||       dimitri.papadimitriou@alcatel-lucent.be, adrian@olddog.co.uk
  RFC4975          ||      B. Campbell, Ed., R. Mahy, Ed., C. Jennings, Ed.         ||       ben@estacado.net, rohan@ekabal.com, fluffy@cisco.com
  RFC4976          ||      C. Jennings, R. Mahy, A. B. Roach         ||       fluffy@cisco.com, rohan@ekabal.com, adam@estacado.net
  RFC4977          ||      G. Tsirtsis, H. Soliman         ||       tsirtsis@qualcomm.com, hesham@elevatemobile.com
  RFC4978          ||      A. Gulbrandsen         ||       arnt@oryx.com
  RFC4979          ||      A. Mayrhofer         ||       alexander.mayrhofer@enum.at
  RFC4980          ||      C. Ng, T. Ernst, E. Paik, M. Bagnulo         ||       chanwah.ng@sg.panasonic.com, thierry.ernst@inria.fr, euna@kt.co.kr, marcelo@it.uc3m.es
  RFC4981          ||      J. Risson, T. Moors         ||       jr@tuffit.com, t.moors@unsw.edu.au
  RFC4982          ||      M. Bagnulo, J. Arkko         ||       marcelo@it.uc3m.es, jari.arkko@ericsson.com
  RFC4983          ||      C. DeSanti, H.K. Vivek, K. McCloghrie, S. Gai         ||       cds@cisco.com, hvivek@cisco.com, kzm@cisco.com, sgai@nuovasystems.com
  RFC4984          ||      D. Meyer, Ed., L. Zhang, Ed., K. Fall, Ed.         ||       dmm@1-4-5.net, lixia@cs.ucla.edu, kfall@intel.com
  RFC4985          ||      S. Santesson         ||       stefans@microsoft.com
  RFC4986          ||      H. Eland, R. Mundy, S. Crocker, S. Krishnaswamy         ||       heland@afilias.info, mundy@sparta.com, steve@shinkuro.com, suresh@sparta.com
  RFC4987          ||      W. Eddy         ||       weddy@grc.nasa.gov
  RFC4988          ||      R. Koodli, C. Perkins         ||       rajeev.koodli@nokia.com, charles.perkins@nokia.com
  RFC4990          ||      K. Shiomoto, R. Papneja, R. Rabbat         ||       shiomoto.kohei@lab.ntt.co.jp, rabbat@alum.mit.edu, rpapneja@isocore.com
  RFC4991          ||      A. Newton         ||       andy@hxr.us
  RFC4992          ||      A. Newton         ||       andy@hxr.us
  RFC4993          ||      A. Newton         ||       andy@hxr.us
  RFC4994          ||      S. Zeng, B. Volz, K. Kinnear, J. Brzozowski         ||       szeng@cisco.com, volz@cisco.com, kkinnear@cisco.com, john_brzozowski@cable.comcast.com
  RFC4995          ||      L-E. Jonsson, G. Pelletier, K. Sandlund         ||       lars-erik@lejonsson.com, ghyslain.pelletier@ericsson.com, kristofer.sandlund@ericsson.com
  RFC4996          ||      G. Pelletier, K. Sandlund, L-E. Jonsson, M. West         ||       ghyslain.pelletier@ericsson.com, kristofer.sandlund@ericsson.com, lars-erik@lejonsson.com, mark.a.west@roke.co.uk
  RFC4997          ||      R. Finking, G. Pelletier         ||       robert.finking@roke.co.uk, ghyslain.pelletier@ericsson.com
  RFC4998          ||      T. Gondrom, R. Brandner, U. Pordesch         ||       tobias.gondrom@opentext.com, ralf.brandner@intercomponentware.com, ulrich.pordesch@zv.fraunhofer.de
  RFC5000          ||      RFC Editor         ||       rfc-editor@rfc-editor.org
  RFC5001          ||      R. Austein         ||       sra@isc.org
  RFC5002          ||      G. Camarillo, G. Blanco         ||       Gonzalo.Camarillo@ericsson.com, German.Blanco@ericsson.com
  RFC5003          ||      C. Metz, L. Martini, F. Balus, J. Sugimoto         ||       chmetz@cisco.com, lmartini@cisco.com, florin.balus@alcatel-lucent.com, sugimoto@nortel.com
  RFC5004          ||      E. Chen, S. Sangli         ||       enkechen@cisco.com, rsrihari@cisco.com
  RFC5005          ||      M. Nottingham         ||       mnot@pobox.com
  RFC5006          ||      J. Jeong, Ed., S. Park, L. Beloeil, S. Madanapalli         ||       jjeong@cs.umn.edu, soohong.park@samsung.com, luc.beloeil@orange-ftgroup.com, smadanapalli@gmail.com
  RFC5007          ||      J. Brzozowski, K. Kinnear, B. Volz, S. Zeng         ||       john_brzozowski@cable.comcast.com, kkinnear@cisco.com, volz@cisco.com, szeng@cisco.com
  RFC5008          ||      R. Housley, J. Solinas         ||       housley@vigilsec.com, jasolin@orion.ncsc.mil
  RFC5009          ||      R. Ejza         ||       ejzak@alcatel-lucent.com
  RFC5010          ||      K. Kinnear, M. Normoyle, M. Stapp         ||       kkinnear@cisco.com, mnormoyle@cisco.com, mjs@cisco.com
  RFC5011          ||      M. StJohns         ||       mstjohns@comcast.net
  RFC5012          ||      H. Schulzrinne, R. Marshall, Ed.         ||       hgs+ecrit@cs.columbia.edu, rmarshall@telecomsys.com
  RFC5013          ||      J. Kunze, T. Baker         ||       jak@ucop.edu, tbaker@tbaker.de
  RFC5014          ||      E. Nordmark, S. Chakrabarti, J. Laganier         ||       Erik.Nordmark@Sun.com, samitac2@gmail.com, julien.IETF@laposte.net
  RFC5015          ||      M. Handley, I. Kouvelas, T. Speakman, L. Vicisano         ||       M.Handley@cs.ucl.ac.uk, kouvelas@cisco.com, speakman@cisco.com, lorenzo@digitalfountain.com
  RFC5016          ||      M. Thomas         ||       mat@cisco.com
  RFC5017          ||      D. McWalter, Ed.         ||       dmcw@dataconnection.com
  RFC5018          ||      G. Camarillo         ||       Gonzalo.Camarillo@ericsson.com
  RFC5019          ||      A. Deacon, R. Hurst         ||       alex@verisign.com, rmh@microsoft.com
  RFC5020          ||      K. Zeilenga         ||       Kurt.Zeilenga@Isode.COM
  RFC5021          ||      S. Josefsson         ||       simon@josefsson.org
  RFC5022          ||      J. Van Dyke, E. Burger, Ed., A. Spitzer         ||       jvandyke@cantata.com, eburger@standardstrack.com, woof@pingtel.com
  RFC5023          ||      J. Gregorio, Ed., B. de hOra, Ed.         ||       joe@bitworking.org, bill@dehora.net
  RFC5024          ||      I. Friend         ||       ieuan.friend@dip.co.uk
  RFC5025          ||      J. Rosenberg         ||       jdrosen@cisco.com
  RFC5026          ||      G. Giaretta, Ed., J. Kempf, V. Devarapalli, Ed.         ||       gerardog@qualcomm.com, kempf@docomolabs-usa.com, vijay.devarapalli@azairenet.com
  RFC5027          ||      F. Andreasen, D. Wing         ||       fandreas@cisco.com, dwing-ietf@fuggles.com
  RFC5028          ||      R. Mahy         ||       rohan@ekabal.com
  RFC5029          ||      JP. Vasseur, S. Previdi         ||       jpv@cisco.com, sprevidi@cisco.com
  RFC5030          ||      M. Nakhjiri, Ed., K. Chowdhury, A. Lior, K. Leung         ||       madjid.nakhjiri@motorola.com, kchowdhury@starentnetworks.com, avi@bridgewatersystems.com, kleung@cisco.com
  RFC5031          ||      H. Schulzrinne         ||       hgs+ecrit@cs.columbia.edu
  RFC5032          ||      E. Burger, Ed.         ||       eric.burger@bea.com
  RFC5033          ||      S. Floyd, M. Allman         ||       floyd@icir.org, mallman@icir.org
  RFC5034          ||      R. Siemborski, A. Menon-Sen         ||       robsiemb@google.com, ams@oryx.com
  RFC5035          ||      J. Schaad         ||       jimsch@exmsft.com
  RFC5036          ||      L. Andersson, Ed., I. Minei, Ed., B. Thomas, Ed.         ||       loa@pi.se, ina@juniper.net, rhthomas@cisco.com
  RFC5037          ||      L. Andersson, Ed., I. Minei, Ed., B. Thomas, Ed.         ||       loa@pi.se, ina@juniper.net, rhthomas@cisco.com
  RFC5038          ||      B. Thomas, L. Andersson         ||       loa@pi.se, rhthomas@cisco.com
  RFC5039          ||      J. Rosenberg, C. Jennings         ||       jdrosen@cisco.com, fluffy@cisco.com
  RFC5040          ||      R. Recio, B. Metzler, P. Culley, J. Hilland, D. Garcia         ||       recio@us.ibm.com, bmt@zurich.ibm.com, paul.culley@hp.com, jeff.hilland@hp.com, Dave.Garcia@StanfordAlumni.org
  RFC5041          ||      H. Shah, J. Pinkerton, R. Recio, P. Culley         ||       hemal@broadcom.com, jpink@microsoft.com, recio@us.ibm.com, paul.culley@hp.com
  RFC5042          ||      J. Pinkerton, E. Deleganes         ||       jpink@windows.microsoft.com, deleganes@yahoo.com
  RFC5043          ||      C. Bestler, Ed., R. Stewart, Ed.         ||       caitlin.bestler@neterion.com, randall@lakerest.net
  RFC5044          ||      P. Culley, U. Elzur, R. Recio, S. Bailey, J. Carrier         ||       paul.culley@hp.com, uri@broadcom.com, recio@us.ibm.com, steph@sandburst.com, carrier@cray.com
  RFC5045          ||      C. Bestler, Ed., L. Coene         ||       caitlin.bestler@neterion.com, lode.coene@nsn.com
  RFC5046          ||      M. Ko, M. Chadalapaka, J. Hufferd, U. Elzur, H. Shah, P. Thaler         ||       mako@us.ibm.com, cbm@rose.hp.com, jhufferd@brocade.com, Uri@Broadcom.com, hemal@broadcom.com, pthaler@broadcom.com
  RFC5047          ||      M. Chadalapaka, J. Hufferd, J. Satran, H. Shah         ||       cbm@rose.hp.com, jhufferd@brocade.com, Julian_Satran@il.ibm.com, hemal@broadcom.com
  RFC5048          ||      M. Chadalapaka, Ed.         ||       cbm@rose.hp.com
  RFC5049          ||      C. Bormann, Z. Liu, R. Price, G. Camarillo, Ed.         ||       cabo@tzi.org, zhigang.c.liu@nokia.com, richard.price@eads.com, Gonzalo.Camarillo@ericsson.com
  RFC5050          ||      K. Scott, S. Burleigh         ||       kscott@mitre.org, Scott.Burleigh@jpl.nasa.gov
  RFC5051          ||      M. Crispin         ||       MRC@CAC.Washington.EDU
  RFC5052          ||      M. Watson, M. Luby, L. Vicisano         ||       mark@digitalfountain.com, luby@digitalfountain.com, lorenzo@digitalfountain.com
  RFC5053          ||      M. Luby, A. Shokrollahi, M. Watson, T. Stockhammer         ||       luby@digitalfountain.com, amin.shokrollahi@epfl.ch, mark@digitalfountain.com, stockhammer@nomor.de
  RFC5054          ||      D. Taylor, T. Wu, N. Mavrogiannopoulos, T. Perrin         ||       dtaylor@gnutls.org, thomwu@cisco.com, nmav@gnutls.org, trevp@trevp.net
  RFC5055          ||      T. Freeman, R. Housley, A. Malpani, D. Cooper, W. Polk         ||       trevorf@microsoft.com, housley@vigilsec.com, ambarish@yahoo.com, david.cooper@nist.gov, wpolk@nist.gov
  RFC5056          ||      N. Williams         ||       Nicolas.Williams@sun.com
  RFC5057          ||      R. Sparks         ||       RjS@estacado.net
  RFC5058          ||      R. Boivie, N. Feldman, Y. Imai, W. Livens, D. Ooms         ||       rhboivie@us.ibm.com, nkfeldman@yahoo.com, ug@xcast.jp, wim@livens.net, dirk@onesparrow.com
  RFC5059          ||      N. Bhaskar, A. Gall, J. Lingard, S. Venaas         ||       nidhi@arastra.com, alexander.gall@switch.ch, jchl@arastra.com, venaas@uninett.no
  RFC5060          ||      R. Sivaramu, J. Lingard, D. McWalter, B. Joshi, A. Kessler         ||       raghava@cisco.com, jchl@arastra.com, dmcw@dataconnection.com, bharat_joshi@infosys.com, kessler@cisco.com
  RFC5061          ||      R. Stewart, Q. Xie, M. Tuexen, S. Maruyama, M. Kozuka         ||       randall@lakerest.net, Qiaobing.Xie@motorola.com, tuexen@fh-muenster.de, mail@marushin.gr.jp, ma-kun@kozuka.jp
  RFC5062          ||      R. Stewart, M. Tuexen, G. Camarillo         ||       randall@lakerest.net, tuexen@fh-muenster.de, Gonzalo.Camarillo@ericsson.com
  RFC5063          ||      A. Satyanarayana, Ed., R. Rahman, Ed.         ||       asatyana@cisco.com, rrahman@cisco.com
  RFC5064          ||      M. Duerst         ||       duerst@it.aoyama.ac.jp
  RFC5065          ||      P. Traina, D. McPherson, J. Scudder         ||       bgp-confederations@st04.pst.org, danny@arbor.net, jgs@juniper.net
  RFC5066          ||      E. Beili         ||       edward.beili@actelis.com
  RFC5067          ||      S. Lind, P. Pfautz         ||       sdlind@att.com, ppfautz@att.com
  RFC5068          ||      C. Hutzler, D. Crocker, P. Resnick, E. Allman, T. Finch         ||       cdhutzler@aol.com, dcrocker@bbiw.net, presnick@qti.qualcomm.com, eric+ietf-smtp@sendmail.org, dot@dotat.at
  RFC5069          ||      T. Taylor, Ed., H. Tschofenig, H. Schulzrinne, M. Shanmugam         ||       tom.taylor.stds@gmail.com, Hannes.Tschofenig@nsn.com, hgs+ecrit@cs.columbia.edu, murugaraj.shanmugam@detecon.com
  RFC5070          ||      R. Danyliw, J. Meijer, Y. Demchenko         ||       rdd@cert.org, jan@flyingcloggies.nl, demch@chello.nl
  RFC5071          ||      D. Hankins         ||       David_Hankins@isc.org
  RFC5072          ||      S. Varada, Ed., D. Haskins, E. Allen         ||       varada@txc.com
  RFC5073          ||      J.P. Vasseur, Ed., J.L. Le Roux, Ed.         ||       jpv@cisco.com, jeanlouis.leroux@orange-ftgroup.com
  RFC5074          ||      S. Weiler         ||       weiler@tislabs.com
  RFC5075          ||      B. Haberman, Ed., R. Hinden         ||       brian@innovationslab.net, bob.hinden@gmail.com
  RFC5076          ||      B. Hoeneisen         ||       hoeneisen@switch.ch
  RFC5077          ||      J. Salowey, H. Zhou, P. Eronen, H. Tschofenig         ||       jsalowey@cisco.com, hzhou@cisco.com, pe@iki.fi, Hannes.Tschofenig@nsn.com
  RFC5078          ||      S. Dawkins         ||       spencer@mcsr-labs.org
  RFC5079          ||      J. Rosenberg         ||       jdrosen@cisco.com
  RFC5080          ||      D. Nelson, A. DeKok         ||       dnelson@elbrysnetworks.com, aland@freeradius.org
  RFC5081          ||      N. Mavrogiannopoulos         ||       nmav@gnutls.org
  RFC5082          ||      V. Gill, J. Heasley, D. Meyer, P. Savola, Ed., C. Pignataro         ||       vijay@umbc.edu, heas@shrubbery.net, dmm@1-4-5.net, psavola@funet.fi, cpignata@cisco.com
  RFC5083          ||      R. Housley         ||       housley@vigilsec.com
  RFC5084          ||      R. Housley         ||       housley@vigilsec.com
  RFC5085          ||      T. Nadeau, Ed., C. Pignataro, Ed.         ||       tnadeau@lucidvision.com, cpignata@cisco.com
  RFC5086          ||      A. Vainshtein, Ed., I. Sasson, E. Metz, T. Frost, P. Pate         ||       sasha@axerra.com, israel@axerra.com, e.t.metz@telecom.tno.nl, tfrost@symmetricom.com, prayson.pate@overturenetworks.com
  RFC5087          ||      Y(J). Stein, R. Shashoua, R. Insler, M. Anavi         ||       yaakov_s@rad.com, ronen_s@rad.com, ron_i@rad.com, motty@radusa.com
  RFC5088          ||      JL. Le Roux, Ed., JP. Vasseur, Ed., Y. Ikejiri, R. Zhang         ||       jeanlouis.leroux@orange-ftgroup.com, jpv@cisco.com, y.ikejiri@ntt.com, raymond.zhang@bt.com
  RFC5089          ||      JL. Le Roux, Ed., JP. Vasseur, Ed., Y. Ikejiri, R. Zhang         ||       jeanlouis.leroux@orange-ftgroup.com, jpv@cisco.com, y.ikejiri@ntt.com, raymond.zhang@bt.com
  RFC5090          ||      B. Sterman, D. Sadolevsky, D. Schwartz, D. Williams, W. Beck         ||       baruch@kayote.com, dscreat@dscreat.com, david@kayote.com, dwilli@cisco.com, beckw@t-systems.com
  RFC5091          ||      X. Boyen, L. Martin         ||       xavier@voltage.com, martin@voltage.com
  RFC5092          ||      A. Melnikov, Ed., C. Newman         ||       Alexey.Melnikov@isode.com, chris.newman@sun.com
  RFC5093          ||      G. Hunt         ||       geoff.hunt@bt.com
  RFC5094          ||      V. Devarapalli, A. Patel, K. Leung         ||       vijay.devarapalli@azairenet.com, alpesh@cisco.com, kleung@cisco.com
  RFC5095          ||      J. Abley, P. Savola, G. Neville-Neil         ||       jabley@ca.afilias.info, psavola@funet.fi, gnn@neville-neil.com
  RFC5096          ||      V. Devarapalli         ||       vijay.devarapalli@azairenet.com
  RFC5097          ||      G. Renker, G. Fairhurst         ||       gerrit@erg.abdn.ac.uk, gorry@erg.abdn.ac.uk
  RFC5098          ||      G. Beacham, S. Kumar, S. Channabasappa         ||       gordon.beacham@motorola.com, satish.kumar@ti.com, Sumanth@cablelabs.com
  RFC5101          ||      B. Claise, Ed.         ||       bclaise@cisco.com
  RFC5102          ||      J. Quittek, S. Bryant, B. Claise, P. Aitken, J. Meyer         ||       quittek@netlab.nec.de, stbryant@cisco.com, bclaise@cisco.com, paitken@cisco.com, jemeyer@paypal.com
  RFC5103          ||      B. Trammell, E. Boschi         ||       bht@cert.org, elisa.boschi@hitachi-eu.com
  RFC5104          ||      S. Wenger, U. Chandra, M. Westerlund, B. Burman         ||       stewe@stewe.org, Umesh.1.Chandra@nokia.com, magnus.westerlund@ericsson.com, bo.burman@ericsson.com
  RFC5105          ||      O. Lendl         ||       otmar.lendl@enum.at
  RFC5106          ||      H. Tschofenig, D. Kroeselberg, A. Pashalidis, Y. Ohba, F. Bersani         ||       Hannes.Tschofenig@nsn.com, Dirk.Kroeselberg@nsn.com, pashalidis@nw.neclab.eu, yohba@tari.toshiba.com, florent.ftrd@gmail.com
  RFC5107          ||      R. Johnson, J. Kumarasamy, K. Kinnear, M. Stapp         ||       raj@cisco.com, jayk@cisco.com, kkinnear@cisco.com, mjs@cisco.com
  RFC5109          ||      A. Li, Ed.         ||       adamli@hyervision.com
  RFC5110          ||      P. Savola         ||       psavola@funet.fi
  RFC5111          ||      B. Aboba, L. Dondeti         ||       bernarda@microsoft.com, ldondeti@qualcomm.com
  RFC5112          ||      M. Garcia-Martin         ||       miguel.garcia@nsn.com
  RFC5113          ||      J. Arkko, B. Aboba, J. Korhonen, Ed., F. Bari         ||       jari.arkko@ericsson.com, bernarda@microsoft.com, jouni.korhonen@teliasonera.com, farooq.bari@att.com
  RFC5114          ||      M. Lepinski, S. Kent         ||       mlepinski@bbn.com, kent@bbn.com
  RFC5115          ||      K. Carlberg, P. O'Hanlon         ||       carlberg@g11.org.uk, p.ohanlon@cs.ucl.ac.uk
  RFC5116          ||      D. McGrew         ||       mcgrew@cisco.com
  RFC5117          ||      M. Westerlund, S. Wenger         ||       magnus.westerlund@ericsson.com, stewe@stewe.org
  RFC5118          ||      V. Gurbani, C. Boulton, R. Sparks         ||       vkg@alcatel-lucent.com, cboulton@ubiquitysoftware.com, RjS@estacado.net
  RFC5119          ||      T. Edwards         ||       thomas.edwards@fox.com
  RFC5120          ||      T. Przygienda, N. Shen, N. Sheth         ||       prz@net4u.ch, naiming@cisco.com, nsheth@juniper.net
  RFC5121          ||      B. Patil, F. Xia, B. Sarikaya, JH. Choi, S. Madanapalli         ||       basavaraj.patil@nsn.com, xiayangsong@huawei.com, sarikaya@ieee.org, jinchoe@samsung.com, smadanapalli@gmail.com
  RFC5122          ||      P. Saint-Andre         ||       ietf@stpeter.im
  RFC5123          ||      R. White, B. Akyol         ||       riw@cisco.com, bora@cisco.com
  RFC5124          ||      J. Ott, E. Carrara         ||       jo@comnet.tkk.fi, carrara@kth.se
  RFC5125          ||      T. Taylor         ||       tom.taylor.stds@gmail.com
  RFC5126          ||      D. Pinkas, N. Pope, J. Ross         ||       Denis.Pinkas@bull.net, nick.pope@thales-esecurity.com, ross@secstan.com
  RFC5127          ||      K. Chan, J. Babiarz, F. Baker         ||       khchan@nortel.com, babiarz@nortel.com, fred@cisco.com
  RFC5128          ||      P. Srisuresh, B. Ford, D. Kegel         ||       srisuresh@yahoo.com, baford@mit.edu, dank06@kegel.com
  RFC5129          ||      B. Davie, B. Briscoe, J. Tay         ||       bsd@cisco.com, bob.briscoe@bt.com, june.tay@bt.com
  RFC5130          ||      S. Previdi, M. Shand, Ed., C. Martin         ||       sprevidi@cisco.com, mshand@cisco.com, chris@ipath.net
  RFC5131          ||      D. McWalter, Ed.         ||       dmcw@dataconnection.com
  RFC5132          ||      D. McWalter, D. Thaler, A. Kessler         ||       dmcw@dataconnection.com, dthaler@windows.microsoft.com, kessler@cisco.com
  RFC5133          ||      M. Tuexen, K. Morneault         ||       tuexen@fh-muenster.de, kmorneau@cisco.com
  RFC5134          ||      M. Mealling         ||       michael@refactored-networks.com
  RFC5135          ||      D. Wing, T. Eckert         ||       dwing-ietf@fuggles.com, eckert@cisco.com
  RFC5136          ||      P. Chimento, J. Ishac         ||       Philip.Chimento@jhuapl.edu, jishac@nasa.gov
  RFC5137          ||      J. Klensin         ||       john-ietf@jck.com
  RFC5138          ||      S. Cox         ||       Simon.Cox@csiro.au
  RFC5139          ||      M. Thomson, J. Winterbottom         ||       martin.thomson@andrew.com, james.winterbottom@andrew.com
  RFC5140          ||      M. Bangalore, R. Kumar, J. Rosenberg, H. Salama, D.N. Shah         ||       manjax@cisco.com, rajneesh@cisco.com, jdrosen@cisco.com, hsalama@citexsoftware.com, dhaval@moowee.tv
  RFC5141          ||      J. Goodwin, H. Apel         ||       goodwin@iso.org, apel@iso.org
  RFC5142          ||      B. Haley, V. Devarapalli, H. Deng, J. Kempf         ||       brian.haley@hp.com, vijay.devarapalli@azairenet.com, kempf@docomolabs-usa.com, denghui@chinamobile.com
  RFC5143          ||      A. Malis, J. Brayley, J. Shirron, L. Martini, S. Vogelsang         ||       andrew.g.malis@verizon.com, jeremy.brayley@ecitele.com, john.shirron@ecitele.com, lmartini@cisco.com, steve.vogelsang@alcatel-lucent.com
  RFC5144          ||      A. Newton, M. Sanz         ||       andy@arin.net, sanz@denic.de
  RFC5145          ||      K. Shiomoto, Ed.         ||       shiomoto.kohei@lab.ntt.co.jp
  RFC5146          ||      K. Kumaki, Ed.         ||       ke-kumaki@kddi.com
  RFC5147          ||      E. Wilde, M. Duerst         ||       dret@berkeley.edu, duerst@it.aoyama.ac.jp
  RFC5148          ||      T. Clausen, C. Dearlove, B. Adamson         ||       T.Clausen@computer.org, chris.dearlove@baesystems.com, adamson@itd.nrl.navy.mil
  RFC5149          ||      J. Korhonen, U. Nilsson, V. Devarapalli         ||       jouni.korhonen@teliasonera.com, ulf.s.nilsson@teliasonera.com, vijay.devarapalli@azairenet.com
  RFC5150          ||      A. Ayyangar, K. Kompella, JP. Vasseur, A. Farrel         ||       arthi@juniper.net, kireeti@juniper.net, jpv@cisco.com, adrian@olddog.co.uk
  RFC5151          ||      A. Farrel, Ed., A. Ayyangar, JP. Vasseur         ||       adrian@olddog.co.uk, arthi@juniper.net, jpv@cisco.com
  RFC5152          ||      JP. Vasseur, Ed., A. Ayyangar, Ed., R. Zhang         ||       jpv@cisco.com, arthi@juniper.net, raymond.zhang@bt.com
  RFC5153          ||      E. Boschi, L. Mark, J. Quittek, M. Stiemerling, P. Aitken         ||       elisa.boschi@hitachi-eu.com, lutz.mark@fokus.fraunhofer.de, quittek@nw.neclab.eu, stiemerling@nw.neclab.eu, paitken@cisco.com
  RFC5154          ||      J. Jee, Ed., S. Madanapalli, J. Mandin         ||       jhjee@etri.re.kr, smadanapalli@gmail.com, j_mandin@yahoo.com
  RFC5155          ||      B. Laurie, G. Sisson, R. Arends, D. Blacka         ||       ben@links.org, geoff-s@panix.com, roy@nominet.org.uk, davidb@verisign.com
  RFC5156          ||      M. Blanchet         ||       Marc.Blanchet@viagenie.ca
  RFC5157          ||      T. Chown         ||       tjc@ecs.soton.ac.uk
  RFC5158          ||      G. Huston         ||       gih@apnic.net
  RFC5159          ||      L. Dondeti, Ed., A. Jerichow         ||       ldondeti@qualcomm.com, anja.jerichow@nsn.com
  RFC5160          ||      P. Levis, M. Boucadair         ||       pierre.levis@orange-ftgroup.com, mohamed.boucadair@orange-ftgroup.com
  RFC5161          ||      A. Gulbrandsen, Ed., A. Melnikov, Ed.         ||       arnt@oryx.com, Alexey.Melnikov@isode.com
  RFC5162          ||      A. Melnikov, D. Cridland, C. Wilson         ||       Alexey.Melnikov@isode.com, dave.cridland@isode.com, corby@computer.org
  RFC5163          ||      G. Fairhurst, B. Collini-Nocker         ||       gorry@erg.abdn.ac.uk, bnocker@cosy.sbg.ac.at
  RFC5164          ||      T. Melia, Ed.         ||       tmelia@cisco.com
  RFC5165          ||      C. Reed         ||       creed@opengeospatial.org
  RFC5166          ||      S. Floyd, Ed.         ||       floyd@icir.org
  RFC5167          ||      M. Dolly, R. Even         ||       mdolly@att.com, roni.even@polycom.co.il
  RFC5168          ||      O. Levin, R. Even, P. Hagendorf         ||       oritl@microsoft.com, roni.even@polycom.co.il, pierre@radvision.com
  RFC5169          ||      T. Clancy, M. Nakhjiri, V. Narayanan, L. Dondeti         ||       clancy@LTSnet.net, madjid.nakhjiri@motorola.com, vidyan@qualcomm.com, ldondeti@qualcomm.com
  RFC5170          ||      V. Roca, C. Neumann, D. Furodet         ||       vincent.roca@inria.fr, christoph.neumann@thomson.net, david.furodet@st.com
  RFC5171          ||      M. Foschiano         ||       foschia@cisco.com
  RFC5172          ||      S. Varada, Ed.         ||       varada@ieee.org
  RFC5173          ||      J. Degener, P. Guenther         ||       jutta@pobox.com, guenther@sendmail.com
  RFC5174          ||      J-P. Evain         ||       evain@ebu.ch
  RFC5175          ||      B. Haberman, Ed., R. Hinden         ||       brian@innovationslab.net, bob.hinden@gmail.com
  RFC5176          ||      M. Chiba, G. Dommety, M. Eklund, D. Mitton, B. Aboba         ||       mchiba@cisco.com, gdommety@cisco.com, meklund@cisco.com, david@mitton.com, bernarda@microsoft.com
  RFC5177          ||      K. Leung, G. Dommety, V. Narayanan, A. Petrescu         ||       kleung@cisco.com, gdommety@cisco.com, vidyan@qualcomm.com, alexandru.petrescu@motorola.com
  RFC5178          ||      N. Williams, A. Melnikov         ||       Nicolas.Williams@sun.com, Alexey.Melnikov@isode.com
  RFC5179          ||      N. Williams         ||       Nicolas.Williams@sun.com
  RFC5180          ||      C. Popoviciu, A. Hamza, G. Van de Velde, D. Dugatkin         ||       cpopovic@cisco.com, ahamza@cisco.com, gunter@cisco.com, diego@fastsoft.com
  RFC5181          ||      M-K. Shin, Ed., Y-H. Han, S-E. Kim, D. Premec         ||       myungki.shin@gmail.com, yhhan@kut.ac.kr, sekim@kt.co.kr, domagoj.premec@siemens.com
  RFC5182          ||      A. Melnikov         ||       Alexey.Melnikov@isode.com
  RFC5183          ||      N. Freed         ||       ned.freed@mrochek.com
  RFC5184          ||      F. Teraoka, K. Gogo, K. Mitsuya, R. Shibui, K. Mitani         ||       tera@ics.keio.ac.jp, gogo@tera.ics.keio.ac.jp, mitsuya@sfc.wide.ad.jp, shibrie@tera.ics.keio.ac.jp, koki@tera.ics.keio.ac.jp, rajeev_koodli@yahoo.com
  RFC5185          ||      S. Mirtorabi, P. Psenak, A. Lindem, Ed., A. Oswal         ||       sina@nuovasystems.com, ppsenak@cisco.com, acee@redback.com, aoswal@redback.com
  RFC5186          ||      B. Haberman, J. Martin         ||       brian@innovationslab.net, jim@wovensystems.com
  RFC5187          ||      P. Pillay-Esnault, A. Lindem         ||       ppe@cisco.com, acee@redback.com
  RFC5188          ||      H. Desineni, Q. Xie         ||       hd@qualcomm.com, Qiaobing.Xie@Gmail.com
  RFC5189          ||      M. Stiemerling, J. Quittek, T. Taylor         ||       stiemerling@nw.neclab.eu, quittek@nw.neclab.eu, tom.taylor.stds@gmail.com
  RFC5190          ||      J. Quittek, M. Stiemerling, P. Srisuresh         ||       quittek@nw.neclab.eu, stiemerling@nw.neclab.eu, srisuresh@yahoo.com
  RFC5191          ||      D. Forsberg, Y. Ohba, Ed., B. Patil, H. Tschofenig, A. Yegin         ||       dan.forsberg@nokia.com, yohba@tari.toshiba.com, basavaraj.patil@nsn.com, hannes.tschofenig@nsn.com, a.yegin@partner.samsung.com
  RFC5192          ||      L. Morand, A. Yegin, S. Kumar, S. Madanapalli         ||       lionel.morand@orange-ftgroup.com, a.yegin@partner.samsung.com, surajk@techmahindra.com, syam@samsung.com
  RFC5193          ||      P. Jayaraman, R. Lopez, Y. Ohba, Ed., M. Parthasarathy, A. Yegin         ||       prakash_jayaraman@net.com, rafa@um.es, yohba@tari.toshiba.com, mohanp@sbcglobal.net, a.yegin@partner.samsung.com
  RFC5194          ||      A. van Wijk, Ed., G. Gybels, Ed.         ||       guido.gybels@rnid.org.uk, arnoud@realtimetext.org
  RFC5195          ||      H. Ould-Brahim, D. Fedyk, Y. Rekhter         ||       hbrahim@nortel.com, yakov@juniper.net, dwfedyk@nortel.com
  RFC5196          ||      M. Lonnfors, K. Kiss         ||       mikko.lonnfors@nokia.com, krisztian.kiss@nokia.com
  RFC5197          ||      S. Fries, D. Ignjatic         ||       steffen.fries@siemens.com, dignjatic@polycom.com
  RFC5198          ||      J. Klensin, M. Padlipsky         ||       john-ietf@jck.com, the.map@alum.mit.edu
  RFC5201          ||      R. Moskowitz, P. Nikander, P. Jokela, Ed., T. Henderson         ||       rgm@icsalabs.com, pekka.nikander@nomadiclab.com, petri.jokela@nomadiclab.com, thomas.r.henderson@boeing.com
  RFC5202          ||      P. Jokela, R. Moskowitz, P. Nikander         ||       petri.jokela@nomadiclab.com, rgm@icsalabs.com, pekka.nikander@nomadiclab.com
  RFC5203          ||      J. Laganier, T. Koponen, L. Eggert         ||       julien.ietf@laposte.net, teemu.koponen@iki.fi, lars.eggert@nokia.com
  RFC5204          ||      J. Laganier, L. Eggert         ||       julien.ietf@laposte.net, lars.eggert@nokia.com
  RFC5205          ||      P. Nikander, J. Laganier         ||       pekka.nikander@nomadiclab.com, julien.ietf@laposte.net
  RFC5206          ||      P. Nikander, T. Henderson, Ed., C. Vogt, J. Arkko         ||       pekka.nikander@nomadiclab.com, thomas.r.henderson@boeing.com, christian.vogt@ericsson.com, jari.arkko@ericsson.com
  RFC5207          ||      M. Stiemerling, J. Quittek, L. Eggert         ||       stiemerling@netlab.nec.de, quittek@nw.neclab.eu, lars.eggert@nokia.com
  RFC5208          ||      B. Kaliski         ||       kaliski_burt@emc.com
  RFC5209          ||      P. Sangster, H. Khosravi, M. Mani, K. Narayan, J. Tardo         ||       Paul_Sangster@symantec.com, hormuzd.m.khosravi@intel.com, mmani@avaya.com, kaushik@cisco.com, joseph.tardo@nevisnetworks.com
  RFC5210          ||      J. Wu, J. Bi, X. Li, G. Ren, K. Xu, M. Williams         ||       jianping@cernet.edu.cn, junbi@cernet.edu.cn, xing@cernet.edu.cn, rg03@mails.tsinghua.edu.cn, xuke@csnet1.cs.tsinghua.edu.cn, miw@juniper.net
  RFC5211          ||      J. Curran         ||       jcurran@istaff.org
  RFC5212          ||      K. Shiomoto, D. Papadimitriou, JL. Le Roux, M. Vigoureux, D. Brungard         ||       shiomoto.kohei@lab.ntt.co.jp, dimitri.papadimitriou@alcatel-lucent.be, jeanlouis.leroux@orange-ftgroup.com, martin.vigoureux@alcatel-lucent.fr, dbrungard@att.com
  RFC5213          ||      S. Gundavelli, Ed., K. Leung, V. Devarapalli, K. Chowdhury, B. Patil         ||       sgundave@cisco.com, kleung@cisco.com, vijay@wichorus.com, kchowdhury@starentnetworks.com, basavaraj.patil@nokia.com
  RFC5214          ||      F. Templin, T. Gleeson, D. Thaler         ||       fred.l.templin@boeing.com, tgleeson@cisco.com, dthaler@microsoft.com
  RFC5215          ||      L. Barbato         ||       lu_zero@gentoo.org
  RFC5216          ||      D. Simon, B. Aboba, R. Hurst         ||       dansimon@microsoft.com, bernarda@microsoft.com, rmh@microsoft.com
  RFC5217          ||      M. Shimaoka, Ed., N. Hastings, R. Nielsen         ||       m-shimaoka@secom.co.jp, nelson.hastings@nist.gov, nielsen_rebecca@bah.com
  RFC5218          ||      D. Thaler, B. Aboba         ||       dthaler@microsoft.com, bernarda@microsoft.com
  RFC5219          ||      R. Finlayson         ||       finlayson@live555.com
  RFC5220          ||      A. Matsumoto, T. Fujisaki, R. Hiromi, K. Kanayama         ||       arifumi@nttv6.net, fujisaki@nttv6.net, hiromi@inetcore.com, kanayama_kenichi@intec-si.co.jp
  RFC5221          ||      A. Matsumoto, T. Fujisaki, R. Hiromi, K. Kanayama         ||       arifumi@nttv6.net, fujisaki@nttv6.net, hiromi@inetcore.com, kanayama_kenichi@intec-si.co.jp
  RFC5222          ||      T. Hardie, A. Newton, H. Schulzrinne, H. Tschofenig         ||       hardie@qualcomm.com, andy@hxr.us, hgs+ecrit@cs.columbia.edu, Hannes.Tschofenig@nsn.com
  RFC5223          ||      H. Schulzrinne, J. Polk, H. Tschofenig         ||       hgs+ecrit@cs.columbia.edu, jmpolk@cisco.com, Hannes.Tschofenig@nsn.com
  RFC5224          ||      M. Brenner         ||       mrbrenner@alcatel-lucent.com
  RFC5225          ||      G. Pelletier, K. Sandlund         ||       ghyslain.pelletier@ericsson.com, kristofer.sandlund@ericsson.com
  RFC5226          ||      T. Narten, H. Alvestrand         ||       narten@us.ibm.com, Harald@Alvestrand.no
  RFC5227          ||      S. Cheshire         ||       rfc@stuartcheshire.org
  RFC5228          ||      P. Guenther, Ed., T. Showalter, Ed.         ||       guenther@sendmail.com, tjs@psaux.com
  RFC5229          ||      K. Homme         ||       kjetilho@ifi.uio.no
  RFC5230          ||      T. Showalter, N. Freed, Ed.         ||       tjs@psaux.com, ned.freed@mrochek.com
  RFC5231          ||      W. Segmuller, B. Leiba         ||       werewolf@us.ibm.com, leiba@watson.ibm.com
  RFC5232          ||      A. Melnikov         ||       alexey.melnikov@isode.com
  RFC5233          ||      K. Murchison         ||       murch@andrew.cmu.edu
  RFC5234          ||      D. Crocker, Ed., P. Overell         ||       dcrocker@bbiw.net, paul@bayleaf.org.uk
  RFC5235          ||      C. Daboo         ||       cyrus@daboo.name
  RFC5236          ||      A. Jayasumana, N. Piratla, T. Banka, A. Bare, R. Whitner         ||       Anura.Jayasumana@colostate.edu, Nischal.Piratla@telekom.de, Tarun.Banka@colostate.edu, abhijit_bare@agilent.com, rick_whitner@agilent.com
  RFC5237          ||      J. Arkko, S. Bradner         ||       jari.arkko@piuha.net, sob@harvard.edu
  RFC5238          ||      T. Phelan         ||       tphelan@sonusnet.com
  RFC5239          ||      M. Barnes, C. Boulton, O. Levin         ||       mary.barnes@nortel.com, cboulton@avaya.com, oritl@microsoft.com
  RFC5240          ||      B. Joshi, R. Bijlani         ||       bharat_joshi@infosys.com, rainab@gmail.com
  RFC5241          ||      A. Falk, S. Bradner         ||       falk@bbn.com, sob@harvard.edu
  RFC5242          ||      J. Klensin, H. Alvestrand         ||       john+ietf@jck.com, harald@alvestrand.no
  RFC5243          ||      R. Ogier         ||       rich.ogier@earthlink.net
  RFC5244          ||      H. Schulzrinne, T. Taylor         ||       schulzrinne@cs.columbia.edu, tom.taylor.stds@gmail.com
  RFC5245          ||      J. Rosenberg         ||       jdrosen@jdrosen.net
  RFC5246          ||      T. Dierks, E. Rescorla         ||       tim@dierks.org, ekr@rtfm.com
  RFC5247          ||      B. Aboba, D. Simon, P. Eronen         ||       bernarda@microsoft.com, dansimon@microsoft.com, pe@iki.fi
  RFC5248          ||      T. Hansen, J. Klensin         ||       tony+mailesc@maillennium.att.com, john+ietf@jck.com
  RFC5249          ||      D. Harrington, Ed.         ||       dharrington@huawei.com
  RFC5250          ||      L. Berger, I. Bryskin, A. Zinin, R. Coltun         ||       lberger@labn.net, ibryskin@advaoptical.com, alex.zinin@alcatel-lucent.com, none
  RFC5251          ||      D. Fedyk, Ed., Y. Rekhter, Ed., D. Papadimitriou, R. Rabbat, L. Berger         ||       dwfedyk@nortel.com, yakov@juniper.net, Dimitri.Papadimitriou@alcatel-lucent.be, rabbat@alum.mit.edu, lberger@labn.net
  RFC5252          ||      I. Bryskin, L. Berger         ||       ibryskin@advaoptical.com, lberger@labn.net
  RFC5253          ||      T. Takeda, Ed.         ||       takeda.tomonori@lab.ntt.co.jp
  RFC5254          ||      N. Bitar, Ed., M. Bocci, Ed., L. Martini, Ed.         ||       nabil.bitar@verizon.com, matthew.bocci@alcatel-lucent.co.uk, lmartini@cisco.com
  RFC5255          ||      C. Newman, A. Gulbrandsen, A. Melnikov         ||       chris.newman@sun.com, arnt@oryx.com, Alexey.Melnikov@isode.com
  RFC5256          ||      M. Crispin, K. Murchison         ||       IMAP+SORT+THREAD@Lingling.Panda.COM, murch@andrew.cmu.edu
  RFC5257          ||      C. Daboo, R. Gellens         ||       cyrus@daboo.name, randy@qualcomm.com
  RFC5258          ||      B. Leiba, A. Melnikov         ||       leiba@watson.ibm.com, Alexey.Melnikov@isode.com
  RFC5259          ||      A. Melnikov, Ed., P. Coates, Ed.         ||       Alexey.Melnikov@isode.com, peter.coates@Sun.COM
  RFC5260          ||      N. Freed         ||       ned.freed@mrochek.com
  RFC5261          ||      J. Urpalainen         ||       jari.urpalainen@nokia.com
  RFC5262          ||      M. Lonnfors, E. Leppanen, H. Khartabil, J. Urpalainen         ||       mikko.lonnfors@nokia.com, eva.leppanen@saunalahti.fi, hisham.khartabil@gmail.com, jari.urpalainen@nokia.com
  RFC5263          ||      M. Lonnfors, J. Costa-Requena, E. Leppanen, H. Khartabil         ||       mikko.lonnfors@nokia.com, jose.costa-requena@nokia.com, eva.leppanen@saunalahti.fi, hisham.khartabil@gmail.com
  RFC5264          ||      A. Niemi, M. Lonnfors, E. Leppanen         ||       aki.niemi@nokia.com, mikko.lonnfors@nokia.com, eva.leppanen@saunalaht.fi
  RFC5265          ||      S. Vaarala, E. Klovning         ||       sami.vaarala@iki.fi, espen@birdstep.com
  RFC5266          ||      V. Devarapalli, P. Eronen         ||       vijay@wichorus.com, pe@iki.fi
  RFC5267          ||      D. Cridland, C. King         ||       dave.cridland@isode.com, cking@mumbo.ca
  RFC5268          ||      R. Koodli, Ed.         ||       rkoodli@starentnetworks.com[
  RFC5269          ||      J. Kempf, R. Koodli         ||       kempf@docomolabs-usa.com, rkoodli@starentnetworks.com
  RFC5270          ||      H. Jang, J. Jee, Y. Han, S. Park, J. Cha         ||       heejin.jang@gmail.com, jhjee@etri.re.kr, yhhan@kut.ac.kr, soohong.park@samsung.com, jscha@etri.re.kr
  RFC5271          ||      H. Yokota, G. Dommety         ||       yokota@kddilabs.jp, gdommety@cisco.com
  RFC5272          ||      J. Schaad, M. Myers         ||       jimsch@nwlink.com, mmyers@fastq.com
  RFC5273          ||      J. Schaad, M. Myers         ||       jimsch@nwlink.com, mmyers@fastq.com
  RFC5274          ||      J. Schaad, M. Myers         ||       jimsch@nwlink.com, mmyers@fastq.com
  RFC5275          ||      S. Turner         ||       turners@ieca.com
  RFC5276          ||      C. Wallace         ||       cwallace@cygnacom.com
  RFC5277          ||      S. Chisholm, H. Trevino         ||       schishol@nortel.com, htrevino@cisco.com
  RFC5278          ||      J. Livingood, D. Troshynski         ||       jason_livingood@cable.comcast.com, dtroshynski@acmepacket.com
  RFC5279          ||      A. Monrad, S. Loreto         ||       atle.monrad@ericsson.com, Salvatore.Loreto@ericsson.com
  RFC5280          ||      D. Cooper, S. Santesson, S. Farrell, S. Boeyen, R. Housley, W. Polk         ||       david.cooper@nist.gov, stefans@microsoft.com, stephen.farrell@cs.tcd.ie, sharon.boeyen@entrust.com, housley@vigilsec.com, wpolk@nist.gov
  RFC5281          ||      P. Funk, S. Blake-Wilson         ||       PaulFunk@alum.mit.edu, sblakewilson@nl.safenet-inc.com
  RFC5282          ||      D. Black, D. McGrew         ||       black_david@emc.com, mcgrew@cisco.com
  RFC5283          ||      B. Decraene, JL. Le Roux, I. Minei         ||       bruno.decraene@orange-ftgroup.com, jeanlouis.leroux@orange-ftgroup.com, ina@juniper.net
  RFC5284          ||      G. Swallow, A. Farrel         ||       swallow@cisco.com, adrian@olddog.co.uk
  RFC5285          ||      D. Singer, H. Desineni         ||       singer@apple.com, hd@qualcomm.com
  RFC5286          ||      A. Atlas, Ed., A. Zinin, Ed.         ||       alia.atlas@bt.com, alex.zinin@alcatel-lucent.com
  RFC5287          ||      A. Vainshtein, Y(J). Stein         ||       Alexander.Vainshtein@ecitele.com, yaakov_s@rad.com
  RFC5288          ||      J. Salowey, A. Choudhury, D. McGrew         ||       jsalowey@cisco.com, abhijitc@cisco.com, mcgrew@cisco.com
  RFC5289          ||      E. Rescorla         ||       ekr@rtfm.com
  RFC5290          ||      S. Floyd, M. Allman         ||       floyd@icir.org, mallman@icir.org
  RFC5291          ||      E. Chen, Y. Rekhter         ||       enkechen@cisco.com, yakov@juniper.net
  RFC5292          ||      E. Chen, S. Sangli         ||       enkechen@cisco.com, rsrihari@cisco.com
  RFC5293          ||      J. Degener, P. Guenther         ||       jutta@pobox.com, guenther@sendmail.com
  RFC5294          ||      P. Savola, J. Lingard         ||       psavola@funet.fi, jchl@arastra.com
  RFC5295          ||      J. Salowey, L. Dondeti, V. Narayanan, M. Nakhjiri         ||       jsalowey@cisco.com, ldondeti@qualcomm.com, vidyan@qualcomm.com, madjid.nakhjiri@motorola.com
  RFC5296          ||      V. Narayanan, L. Dondeti         ||       vidyan@qualcomm.com, ldondeti@qualcomm.com
  RFC5297          ||      D. Harkins         ||       dharkins@arubanetworks.com
  RFC5298          ||      T. Takeda, Ed., A. Farrel, Ed., Y. Ikejiri, JP. Vasseur         ||       takeda.tomonori@lab.ntt.co.jp, y.ikejiri@ntt.com, adrian@olddog.co.uk, jpv@cisco.com
  RFC5301          ||      D. McPherson, N. Shen         ||       danny@arbor.net, naiming@cisco.com
  RFC5302          ||      T. Li, H. Smit, T. Przygienda         ||       tony.li@tony.li, hhw.smit@xs4all.nl, prz@net4u.ch
  RFC5303          ||      D. Katz, R. Saluja, D. Eastlake 3rd         ||       dkatz@juniper.net, rajesh.saluja@tenetindia.com, d3e3e3@gmail.com
  RFC5304          ||      T. Li, R. Atkinson         ||       tony.li@tony.li, rja@extremenetworks.com
  RFC5305          ||      T. Li, H. Smit         ||       tony.li@tony.li, hhwsmit@xs4all.nl
  RFC5306          ||      M. Shand, L. Ginsberg         ||       mshand@cisco.com, ginsberg@cisco.com
  RFC5307          ||      K. Kompella, Ed., Y. Rekhter, Ed.         ||       kireeti@juniper.net, yakov@juniper.net
  RFC5308          ||      C. Hopps         ||       chopps@cisco.com
  RFC5309          ||      N. Shen, Ed., A. Zinin, Ed.         ||       naiming@cisco.com, alex.zinin@alcatel-lucent.com
  RFC5310          ||      M. Bhatia, V. Manral, T. Li, R. Atkinson, R. White, M. Fanto         ||       manav@alcatel-lucent.com, vishwas@ipinfusion.com, tony.li@tony.li, rja@extremenetworks.com, riw@cisco.com, mfanto@aegisdatasecurity.com
  RFC5311          ||      D. McPherson, Ed., L. Ginsberg, S. Previdi, M. Shand         ||       danny@arbor.net, ginsberg@cisco.com, sprevidi@cisco.com, mshand@cisco.com
  RFC5316          ||      M. Chen, R. Zhang, X. Duan         ||       mach@huawei.com, zhangrenhai@huawei.com, duanxiaodong@chinamobile.com
  RFC5317          ||      S. Bryant, Ed., L. Andersson, Ed.         ||       stbryant@cisco.com, loa@pi.nu
  RFC5318          ||      J. Hautakorpi, G. Camarillo         ||       Jani.Hautakorpi@ericsson.com, Gonzalo.Camarillo@ericsson.com
  RFC5320          ||      F. Templin, Ed.         ||       fltemplin@acm.org
  RFC5321          ||      J. Klensin         ||       john+smtp@jck.com
  RFC5322          ||      P. Resnick, Ed.         ||       presnick@qti.qualcomm.com
  RFC5323          ||      J. Reschke, Ed., S. Reddy, J. Davis, A. Babich         ||       julian.reschke@greenbytes.de, Surendra.Reddy@mitrix.com, jrd3@alum.mit.edu, ababich@us.ibm.com
  RFC5324          ||      C. DeSanti, F. Maino, K. McCloghrie         ||       cds@cisco.com, fmaino@cisco.com, kzm@cisco.com
  RFC5325          ||      S. Burleigh, M. Ramadas, S. Farrell         ||       Scott.Burleigh@jpl.nasa.gov, mramadas@gmail.com, stephen.farrell@cs.tcd.ie
  RFC5326          ||      M. Ramadas, S. Burleigh, S. Farrell         ||       mramadas@gmail.com, Scott.Burleigh@jpl.nasa.gov, stephen.farrell@cs.tcd.ie
  RFC5327          ||      S. Farrell, M. Ramadas, S. Burleigh         ||       stephen.farrell@cs.tcd.ie, mramadas@gmail.com, Scott.Burleigh@jpl.nasa.gov
  RFC5328          ||      A. Adolf, P. MacAvock         ||       alexander.adolf@micronas.com, macavock@dvb.org
  RFC5329          ||      K. Ishiguro, V. Manral, A. Davey, A. Lindem, Ed.         ||       kunihiro@ipinfusion.com, vishwas@ipinfusion.com, Alan.Davey@dataconnection.com, acee@redback.com
  RFC5330          ||      JP. Vasseur, Ed., M. Meyer, K. Kumaki, A. Bonda         ||       jpv@cisco.com, matthew.meyer@bt.com, ke-kumaki@kddi.com, alberto.tempiabonda@telecomitalia.it
  RFC5331          ||      R. Aggarwal, Y. Rekhter, E. Rosen         ||       rahul@juniper.net, yakov@juniper.net, erosen@cisco.com
  RFC5332          ||      T. Eckert, E. Rosen, Ed., R. Aggarwal, Y. Rekhter         ||       eckert@cisco.com, erosen@cisco.com, rahul@juniper.net, yakov@juniper.net
  RFC5333          ||      R. Mahy, B. Hoeneisen         ||       rohan@ekabal.com, bernie@ietf.hoeneisen.ch
  RFC5334          ||      I. Goncalves, S. Pfeiffer, C. Montgomery         ||       justivo@gmail.com, silvia@annodex.net, monty@xiph.org
  RFC5335          ||      A. Yang, Ed.         ||       abelyang@twnic.net.tw
  RFC5336          ||      J. Yao, Ed., W. Mao, Ed.         ||       yaojk@cnnic.cn, maowei_ietf@cnnic.cn
  RFC5337          ||      C. Newman, A. Melnikov, Ed.         ||       chris.newman@sun.com, Alexey.Melnikov@isode.com
  RFC5338          ||      T. Henderson, P. Nikander, M. Komu         ||       thomas.r.henderson@boeing.com, pekka.nikander@nomadiclab.com, miika@iki.fi
  RFC5339          ||      JL. Le Roux, Ed., D. Papadimitriou, Ed.         ||       jeanlouis.leroux@orange-ftgroup.com, dimitri.papadimitriou@alcatel-lucent.be
  RFC5340          ||      R. Coltun, D. Ferguson, J. Moy, A. Lindem         ||       none, dennis@juniper.net, jmoy@sycamorenet.com, acee@redback.com
  RFC5341          ||      C. Jennings, V. Gurbani         ||       fluffy@cisco.com, vkg@alcatel-lucent.com
  RFC5342          ||      D. Eastlake 3rd         ||       d3e3e3@gmail.com
  RFC5343          ||      J. Schoenwaelder         ||       j.schoenwaelder@jacobs-university.de
  RFC5344          ||      A. Houri, E. Aoki, S. Parameswar         ||       avshalom@il.ibm.com, aoki@aol.net, Sriram.Parameswar@microsoft.com
  RFC5345          ||      J. Schoenwaelder         ||       j.schoenwaelder@jacobs-university.de
  RFC5346          ||      J. Lim, W. Kim, C. Park, L. Conroy         ||       jhlim@nida.or.kr, wkim@nida.or.kr, ckp@nida.or.kr, lconroy@insensate.co.uk
  RFC5347          ||      F. Andreasen, D. Hancock         ||       fandreas@cisco.com, d.hancock@cablelabs.com
  RFC5348          ||      S. Floyd, M. Handley, J. Padhye, J. Widmer         ||       floyd@icir.org, M.Handley@cs.ucl.ac.uk, padhye@microsoft.com, widmer@acm.org
  RFC5349          ||      L. Zhu, K. Jaganathan, K. Lauter         ||       lzhu@microsoft.com, karthikj@microsoft.com, klauter@microsoft.com
  RFC5350          ||      J. Manner, A. McDonald         ||       jukka.manner@tkk.fi, andrew.mcdonald@roke.co.uk
  RFC5351          ||      P. Lei, L. Ong, M. Tuexen, T. Dreibholz         ||       peterlei@cisco.com, Lyong@Ciena.com, tuexen@fh-muenster.de, dreibh@iem.uni-due.de
  RFC5352          ||      R. Stewart, Q. Xie, M. Stillman, M. Tuexen         ||       randall@lakerest.net, Qiaobing.Xie@gmail.org, maureen.stillman@nokia.com, tuexen@fh-muenster.de
  RFC5353          ||      Q. Xie, R. Stewart, M. Stillman, M. Tuexen, A. Silverton         ||       Qiaobing.Xie@gmail.org, randall@lakerest.net, maureen.stillman@nokia.com, tuexen@fh-muenster.de, ajs.ietf@gmail.com
  RFC5354          ||      R. Stewart, Q. Xie, M. Stillman, M. Tuexen         ||       randall@lakerest.net, Qiaobing.Xie@gmail.org, maureen.stillman@nokia.com, tuexen@fh-muenster.de
  RFC5355          ||      M. Stillman, Ed., R. Gopal, E. Guttman, S. Sengodan, M. Holdrege         ||       maureen.stillman@nokia.com, ram.gopal@nsn.com, Erik.Guttman@sun.com, Senthil.sengodan@nsn.com, Holdrege@gmail.com
  RFC5356          ||      T. Dreibholz, M. Tuexen         ||       dreibh@iem.uni-due.de, tuexen@fh-muenster.de
  RFC5357          ||      K. Hedayat, R. Krzanowski, A. Morton, K. Yum, J. Babiarz         ||       khedayat@brixnet.com, roman.krzanowski@verizon.com, acmorton@att.com, kyum@juniper.net, babiarz@nortel.com
  RFC5358          ||      J. Damas, F. Neves         ||       Joao_Damas@isc.org, fneves@registro.br
  RFC5359          ||      A. Johnston, Ed., R. Sparks, C. Cunningham, S. Donovan, K. Summers         ||       alan@sipstation.com, RjS@nostrum.com, chrcunni@cisco.com, srd@cisco.com, ksummers@sonusnet.com
  RFC5360          ||      J. Rosenberg, G. Camarillo, Ed., D. Willis         ||       jdrosen@cisco.com, Gonzalo.Camarillo@ericsson.com, dean.willis@softarmor.com
  RFC5361          ||      G. Camarillo         ||       Gonzalo.Camarillo@ericsson.com
  RFC5362          ||      G. Camarillo         ||       Gonzalo.Camarillo@ericsson.com
  RFC5363          ||      G. Camarillo, A.B. Roach         ||       Gonzalo.Camarillo@ericsson.com, Adam.Roach@tekelec.com
  RFC5364          ||      M. Garcia-Martin, G. Camarillo         ||       miguel.a.garcia@ericsson.com, Gonzalo.Camarillo@ericsson.com
  RFC5365          ||      M. Garcia-Martin, G. Camarillo         ||       miguel.a.garcia@ericsson.com, Gonzalo.Camarillo@ericsson.com
  RFC5366          ||      G. Camarillo, A. Johnston         ||       Gonzalo.Camarillo@ericsson.com, alan@sipstation.com
  RFC5367          ||      G. Camarillo, A.B. Roach, O. Levin         ||       Gonzalo.Camarillo@ericsson.com, Adam.Roach@tekelec.com, oritl@microsoft.com
  RFC5368          ||      G. Camarillo, A. Niemi, M. Isomaki, M. Garcia-Martin, H. Khartabil         ||       Gonzalo.Camarillo@ericsson.com, Aki.Niemi@nokia.com, markus.isomaki@nokia.com, miguel.a.garcia@ericsson.com, hisham.khartabil@gmail.com
  RFC5369          ||      G. Camarillo         ||       Gonzalo.Camarillo@ericsson.com
  RFC5370          ||      G. Camarillo         ||       Gonzalo.Camarillo@ericsson.com
  RFC5371          ||      S. Futemma, E. Itakura, A. Leung         ||       satosi-f@sm.sony.co.jp, itakura@sm.sony.co.jp, andrew@ualberta.net
  RFC5372          ||      A. Leung, S. Futemma, E. Itakura         ||       andrew@ualberta.net, satosi-f@sm.sony.co.jp, itakura@sm.sony.co.jp
  RFC5373          ||      D. Willis, Ed., A. Allen         ||       dean.willis@softarmor.com, aallen@rim.com
  RFC5374          ||      B. Weis, G. Gross, D. Ignjatic         ||       bew@cisco.com, gmgross@securemulticast.net, dignjatic@polycom.com
  RFC5375          ||      G. Van de Velde, C. Popoviciu, T. Chown, O. Bonness, C. Hahn         ||       gunter@cisco.com, cpopovic@cisco.com, tjc@ecs.soton.ac.uk, Olaf.Bonness@t-systems.com, HahnC@t-systems.com
  RFC5376          ||      N. Bitar, R. Zhang, K. Kumaki         ||       nabil.n.bitar@verizon.com, ke-kumaki@kddi.com, Raymond.zhang@bt.com
  RFC5377          ||      J. Halpern, Ed.         ||       jmh@joelhalpern.com
  RFC5378          ||      S. Bradner, Ed., J. Contreras, Ed.         ||       sob@harvard.edu, jorge.contreras@wilmerhale.com
  RFC5379          ||      M. Munakata, S. Schubert, T. Ohba         ||       munakata.mayumi@lab.ntt.co.jp, shida@ntt-at.com, ohba.takumi@lab.ntt.co.jp
  RFC5380          ||      H. Soliman, C. Castelluccia, K. ElMalki, L. Bellier         ||       hesham@elevatemobile.com, claude.castelluccia@inria.fr, karim@athonet.com, ludovic.bellier@inria.fr
  RFC5381          ||      T. Iijima, Y. Atarashi, H. Kimura, M. Kitani, H. Okita         ||       tomoyuki.iijima@alaxala.com, atarashi@alaxala.net, h-kimura@alaxala.net, makoto.kitani@alaxala.com, hideki.okita.pf@hitachi.com
  RFC5382          ||      S. Guha, Ed., K. Biswas, B. Ford, S. Sivakumar, P. Srisuresh         ||       saikat@cs.cornell.edu, kbiswas@cisco.com, baford@mpi-sws.org, ssenthil@cisco.com, srisuresh@yahoo.com
  RFC5383          ||      R. Gellens         ||       randy@qualcomm.com
  RFC5384          ||      A. Boers, I. Wijnands, E. Rosen         ||       aboers@cisco.com, ice@cisco.com, erosen@cisco.com
  RFC5385          ||      J. Touch         ||       touch@isi.edu
  RFC5386          ||      N. Williams, M. Richardson         ||       Nicolas.Williams@sun.com, mcr@sandelman.ottawa.on.ca
  RFC5387          ||      J. Touch, D. Black, Y. Wang         ||       touch@isi.edu, black_david@emc.com, yu-shun.wang@microsoft.com
  RFC5388          ||      S. Niccolini, S. Tartarelli, J. Quittek, T. Dietz, M. Swany         ||       saverio.niccolini@nw.neclab.eu, sandra.tartarelli@nw.neclab.eu, quittek@nw.neclab.eu, thomas.dietz@nw.neclab.eu, swany@UDel.Edu
  RFC5389          ||      J. Rosenberg, R. Mahy, P. Matthews, D. Wing         ||       jdrosen@cisco.com, rohan@ekabal.com, philip_matthews@magma.ca, dwing-ietf@fuggles.com
  RFC5390          ||      J. Rosenberg         ||       jdrosen@cisco.com
  RFC5391          ||      A. Sollaud         ||       aurelien.sollaud@orange-ftgroup.com
  RFC5392          ||      M. Chen, R. Zhang, X. Duan         ||       mach@huawei.com, zhangrenhai@huawei.com, duanxiaodong@chinamobile.com
  RFC5393          ||      R. Sparks, Ed., S. Lawrence, A. Hawrylyshen, B. Campen         ||       RjS@nostrum.com, scott.lawrence@nortel.com, alan.ietf@polyphase.ca, bcampen@estacado.net
  RFC5394          ||      I. Bryskin, D. Papadimitriou, L. Berger, J. Ash         ||       ibryskin@advaoptical.com, dimitri.papadimitriou@alcatel.be, lberger@labn.net, gash5107@yahoo.com
  RFC5395          ||      D. Eastlake 3rd         ||       d3e3e3@gmail.com
  RFC5396          ||      G. Huston, G. Michaelson         ||       gih@apnic.net, ggm@apnic.net
  RFC5397          ||      W. Sanchez, C. Daboo         ||       wsanchez@wsanchez.net, cyrus@daboo.name
  RFC5398          ||      G. Huston         ||       gih@apnic.net
  RFC5401          ||      B. Adamson, C. Bormann, M. Handley, J. Macker         ||       adamson@itd.nrl.navy.mil, cabo@tzi.org, M.Handley@cs.ucl.ac.uk, macker@itd.nrl.navy.mil
  RFC5402          ||      T. Harding, Ed.         ||       tharding@us.axway.com
  RFC5403          ||      M. Eisler         ||       mike@eisler.com
  RFC5404          ||      M. Westerlund, I. Johansson         ||       magnus.westerlund@ericsson.com, ingemar.s.johansson@ericsson.com
  RFC5405          ||      L. Eggert, G. Fairhurst         ||       lars.eggert@nokia.com, gorry@erg.abdn.ac.uk
  RFC5406          ||      S. Bellovin         ||       bellovin@acm.org
  RFC5407          ||      M. Hasebe, J. Koshiko, Y. Suzuki, T. Yoshikawa, P. Kyzivat         ||       hasebe.miki@east.ntt.co.jp, j.koshiko@east.ntt.co.jp, suzuki.yasushi@lab.ntt.co.jp, tomoyuki.yoshikawa@east.ntt.co.jp, pkyzivat@cisco.com
  RFC5408          ||      G. Appenzeller, L. Martin, M. Schertler         ||       appenz@cs.stanford.edu, martin@voltage.com, mschertler@us.axway.com
  RFC5409          ||      L. Martin, M. Schertler         ||       martin@voltage.com, mschertler@us.axway.com
  RFC5410          ||      A. Jerichow, Ed., L. Piron         ||       anja.jerichow@nsn.com, laurent.piron@nagravision.com
  RFC5411          ||      J. Rosenberg         ||       jdrosen@cisco.com
  RFC5412          ||      P. Calhoun, R. Suri, N. Cam-Winget, M. Williams, S. Hares, B. O'Hara, S. Kelly         ||       pcalhoun@cisco.com, rsuri@cisco.com, ncamwing@cisco.com, gwhiz@gwhiz.com, shares@ndzh.com, bob.ohara@computer.org, scott@hyperthought.com
  RFC5413          ||      P. Narasimhan, D. Harkins, S. Ponnuswamy         ||       partha@arubanetworks.com, dharkins@arubanetworks.com, subbu@arubanetworks.com
  RFC5414          ||      S. Iino, S. Govindan, M. Sugiura, H. Cheng         ||       iino.satoshi@jp.panasonic.com, saravanan.govindan@sg.panasonic.com, sugiura.mikihito@jp.panasonic.com, hong.cheng@sg.panasonic.com
  RFC5415          ||      P. Calhoun, Ed., M. Montemurro, Ed., D. Stanley, Ed.         ||       pcalhoun@cisco.com, mmontemurro@rim.com, dstanley@arubanetworks.com
  RFC5416          ||      P. Calhoun, Ed., M. Montemurro, Ed., D. Stanley, Ed.         ||       pcalhoun@cisco.com, mmontemurro@rim.com, dstanley@arubanetworks.com
  RFC5417          ||      P. Calhoun         ||       pcalhoun@cisco.com
  RFC5418          ||      S. Kelly, T. Clancy         ||       scott@hyperthought.com, clancy@LTSnet.net
  RFC5419          ||      B. Patil, G. Dommety         ||       basavaraj.patil@nokia.com, gdommety@cisco.com
  RFC5420          ||      A. Farrel, Ed., D. Papadimitriou, JP. Vasseur, A. Ayyangarps         ||       adrian@olddog.co.uk, dimitri.papadimitriou@alcatel.be, jpv@cisco.com, arthi@juniper.net
  RFC5421          ||      N. Cam-Winget, H. Zhou         ||       ncamwing@cisco.com, hzhou@cisco.com
  RFC5422          ||      N. Cam-Winget, D. McGrew, J. Salowey, H. Zhou         ||       ncamwing@cisco.com, mcgrew@cisco.com, jsalowey@cisco.com, hzhou@cisco.com
  RFC5423          ||      R. Gellens, C. Newman         ||       rg+ietf@qualcomm.com, chris.newman@sun.com
  RFC5424          ||      R. Gerhards         ||       rgerhards@adiscon.com
  RFC5425          ||      F. Miao, Ed., Y. Ma, Ed., J. Salowey, Ed.         ||       miaofy@huawei.com, myz@huawei.com, jsalowey@cisco.com
  RFC5426          ||      A. Okmianski         ||       aokmians@cisco.com
  RFC5427          ||      G. Keeni         ||       glenn@cysols.com
  RFC5428          ||      S. Channabasappa, W. De Ketelaere, E. Nechamkin         ||       Sumanth@cablelabs.com, deketelaere@tComLabs.com, enechamkin@broadcom.com
  RFC5429          ||      A. Stone, Ed.         ||       aaron@serendipity.palo-alto.ca.us
  RFC5430          ||      M. Salter, E. Rescorla, R. Housley         ||       msalter@restarea.ncsc.mil, ekr@rtfm.com, housley@vigilsec.com
  RFC5431          ||      D. Sun         ||       dongsun@alcatel-lucent.com
  RFC5432          ||      J. Polk, S. Dhesikan, G. Camarillo         ||       jmpolk@cisco.com, sdhesika@cisco.com, Gonzalo.Camarillo@ericsson.com
  RFC5433          ||      T. Clancy, H. Tschofenig         ||       clancy@ltsnet.net, Hannes.Tschofenig@gmx.net
  RFC5434          ||      T. Narten         ||       narten@us.ibm.com
  RFC5435          ||      A. Melnikov, Ed., B. Leiba, Ed., W. Segmuller, T. Martin         ||       Alexey.Melnikov@isode.com, leiba@watson.ibm.com, werewolf@us.ibm.com, timmartin@alumni.cmu.edu
  RFC5436          ||      B. Leiba, M. Haardt         ||       leiba@watson.ibm.com, michael.haardt@freenet.ag
  RFC5437          ||      P. Saint-Andre, A. Melnikov         ||       ietf@stpeter.im, Alexey.Melnikov@isode.com
  RFC5438          ||      E. Burger, H. Khartabil         ||       eburger@standardstrack.com, hisham.khartabil@gmail.com
  RFC5439          ||      S. Yasukawa, A. Farrel, O. Komolafe         ||       s.yasukawa@hco.ntt.co.jp, adrian@olddog.co.uk, femi@cisco.com
  RFC5440          ||      JP. Vasseur, Ed., JL. Le Roux, Ed.         ||       jpv@cisco.com, jeanlouis.leroux@orange-ftgroup.com
  RFC5441          ||      JP. Vasseur, Ed., R. Zhang, N. Bitar, JL. Le Roux         ||       jpv@cisco.com, raymond.zhang@bt.com, nabil.n.bitar@verizon.com, jeanlouis.leroux@orange-ftgroup.com
  RFC5442          ||      E. Burger, G. Parsons         ||       eburger@standardstrack.com, gparsons@nortel.com
  RFC5443          ||      M. Jork, A. Atlas, L. Fang         ||       Markus.Jork@genband.com, alia.atlas@bt.com, lufang@cisco.com
  RFC5444          ||      T. Clausen, C. Dearlove, J. Dean, C. Adjih         ||       T.Clausen@computer.org, chris.dearlove@baesystems.com, jdean@itd.nrl.navy.mil, Cedric.Adjih@inria.fr
  RFC5445          ||      M. Watson         ||       mark@digitalfountain.com
  RFC5446          ||      J. Korhonen, U. Nilsson         ||       jouni.nospam@gmail.com, ulf.s.nilsson@teliasonera.com
  RFC5447          ||      J. Korhonen, Ed., J. Bournelle, H. Tschofenig, C. Perkins, K. Chowdhury         ||       jouni.nospam@gmail.com, julien.bournelle@orange-ftgroup.com, Hannes.Tschofenig@nsn.com, charliep@wichorus.com, kchowdhury@starentnetworks.com
  RFC5448          ||      J. Arkko, V. Lehtovirta, P. Eronen         ||       jari.arkko@piuha.net, vesa.lehtovirta@ericsson.com, pe@iki.fi
  RFC5449          ||      E. Baccelli, P. Jacquet, D. Nguyen, T. Clausen         ||       Emmanuel.Baccelli@inria.fr, Philippe.Jacquet@inria.fr, dang.nguyen@crc.ca, T.Clausen@computer.org
  RFC5450          ||      D. Singer, H. Desineni         ||       singer@apple.com, hd@qualcomm.com
  RFC5451          ||      M. Kucherawy         ||       msk+ietf@sendmail.com
  RFC5452          ||      A. Hubert, R. van Mook         ||       bert.hubert@netherlabs.nl, remco@eu.equinix.com
  RFC5453          ||      S. Krishnan         ||       suresh.krishnan@ericsson.com
  RFC5454          ||      G. Tsirtsis, V. Park, H. Soliman         ||       tsirtsis@googlemail.com, vpark@qualcomm.com, hesham@elevatemobile.com
  RFC5455          ||      S. Sivabalan, Ed., J. Parker, S. Boutros, K. Kumaki         ||       msiva@cisco.com, jdparker@cisco.com, sboutros@cisco.com, ke-kumaki@kddi.com
  RFC5456          ||      M. Spencer, B. Capouch, E. Guy, Ed., F. Miller, K. Shumard         ||       markster@digium.com, brianc@saintjoe.edu, edguy@emcsw.com, mail@frankwmiller.net, kshumard@gmail.com
  RFC5457          ||      E. Guy, Ed.         ||       edguy@emcsw.com
  RFC5458          ||      H. Cruickshank, P. Pillai, M. Noisternig, S. Iyengar         ||       h.cruickshank@surrey.ac.uk, p.pillai@bradford.ac.uk, mnoist@cosy.sbg.ac.at, sunil.iyengar@logica.com
  RFC5459          ||      A. Sollaud         ||       aurelien.sollaud@orange-ftgroup.com
  RFC5460          ||      M. Stapp         ||       mjs@cisco.com
  RFC5461          ||      F. Gont         ||       fernando@gont.com.ar
  RFC5462          ||      L. Andersson, R. Asati         ||       loa@pi.nu, rajiva@cisco.com
  RFC5463          ||      N. Freed         ||       ned.freed@mrochek.com
  RFC5464          ||      C. Daboo         ||       cyrus@daboo.name
  RFC5465          ||      A. Gulbrandsen, C. King, A. Melnikov         ||       arnt@oryx.com, Curtis.King@isode.com, Alexey.Melnikov@isode.com
  RFC5466          ||      A. Melnikov, C. King         ||       Alexey.Melnikov@isode.com, Curtis.King@isode.com
  RFC5467          ||      L. Berger, A. Takacs, D. Caviglia, D. Fedyk, J. Meuric         ||       lberger@labn.net, attila.takacs@ericsson.com, diego.caviglia@ericsson.com, dwfedyk@nortel.com, julien.meuric@orange-ftgroup.com
  RFC5468          ||      S. Dasgupta, J. de Oliveira, JP. Vasseur         ||       sukrit@ece.drexel.edu, jau@ece.drexel.edu, jpv@cisco.com
  RFC5469          ||      P. Eronen, Ed.         ||       pe@iki.fi
  RFC5470          ||      G. Sadasivan, N. Brownlee, B. Claise, J. Quittek         ||       gsadasiv@rohati.com, n.brownlee@auckland.ac.nz, bclaise@cisco.com, quittek@nw.neclab.eu
  RFC5471          ||      C. Schmoll, P. Aitken, B. Claise         ||       carsten.schmoll@fokus.fraunhofer.de, paitken@cisco.com, bclaise@cisco.com
  RFC5472          ||      T. Zseby, E. Boschi, N. Brownlee, B. Claise         ||       tanja.zseby@fokus.fraunhofer.de, elisa.boschi@hitachi-eu.com, nevil@caida.org, bclaise@cisco.com
  RFC5473          ||      E. Boschi, L. Mark, B. Claise         ||       elisa.boschi@hitachi-eu.com, lutz.mark@ifam.fraunhofer.de, bclaise@cisco.com
  RFC5474          ||      N. Duffield, Ed., D. Chiou, B. Claise, A. Greenberg, M. Grossglauser, J. Rexford         ||       duffield@research.att.com, Derek@ece.utexas.edu, bclaise@cisco.com, albert@microsoft.com, matthias.grossglauser@epfl.ch, jrex@cs.princeton.edu
  RFC5475          ||      T. Zseby, M. Molina, N. Duffield, S. Niccolini, F. Raspall         ||       tanja.zseby@fokus.fraunhofer.de, maurizio.molina@dante.org.uk, duffield@research.att.com, saverio.niccolini@netlab.nec.de, fredi@entel.upc.es
  RFC5476          ||      B. Claise, Ed., A. Johnson, J. Quittek         ||       bclaise@cisco.com, andrjohn@cisco.com, quittek@nw.neclab.eu
  RFC5477          ||      T. Dietz, B. Claise, P. Aitken, F. Dressler, G. Carle         ||       Thomas.Dietz@nw.neclab.eu, bclaise@cisco.com, paitken@cisco.com, dressler@informatik.uni-erlangen.de, carle@informatik.uni-tuebingen.de
  RFC5478          ||      J. Polk         ||       jmpolk@cisco.com
  RFC5479          ||      D. Wing, Ed., S. Fries, H. Tschofenig, F. Audet         ||       dwing-ietf@fuggles.com, steffen.fries@siemens.com, Hannes.Tschofenig@nsn.com, audet@nortel.com
  RFC5480          ||      S. Turner, D. Brown, K. Yiu, R. Housley, T. Polk         ||       turners@ieca.com, kelviny@microsoft.com, dbrown@certicom.com, housley@vigilsec.com, wpolk@nist.gov
  RFC5481          ||      A. Morton, B. Claise         ||       acmorton@att.com, bclaise@cisco.com
  RFC5482          ||      L. Eggert, F. Gont         ||       lars.eggert@nokia.com, fernando@gont.com.ar
  RFC5483          ||      L. Conroy, K. Fujiwara         ||       lconroy@insensate.co.uk, fujiwara@jprs.co.jp
  RFC5484          ||      D. Singer         ||       singer@apple.com
  RFC5485          ||      R. Housley         ||       housley@vigilsec.com
  RFC5486          ||      D. Malas, Ed., D. Meyer, Ed.         ||       d.malas@cablelabs.com, dmm@1-4-5.net
  RFC5487          ||      M. Badra         ||       badra@isima.fr
  RFC5488          ||      S. Gundavelli, G. Keeni, K. Koide, K. Nagami         ||       sgundave@cisco.com, glenn@cysols.com, ka-koide@kddi.com, nagami@inetcore.com
  RFC5489          ||      M. Badra, I. Hajjeh         ||       badra@isima.fr, ibrahim.hajjeh@ineovation.fr
  RFC5490          ||      A. Melnikov         ||       Alexey.Melnikov@isode.com
  RFC5491          ||      J. Winterbottom, M. Thomson, H. Tschofenig         ||       james.winterbottom@andrew.com, martin.thomson@andrew.com, Hannes.Tschofenig@gmx.net
  RFC5492          ||      J. Scudder, R. Chandra         ||       jgs@juniper.net, rchandra@sonoasystems.com
  RFC5493          ||      D. Caviglia, D. Bramanti, D. Li, D. McDysan         ||       diego.caviglia@ericsson.com, dino.bramanti@ericsson.com, danli@huawei.com, dave.mcdysan@verizon.com
  RFC5494          ||      J. Arkko, C. Pignataro         ||       jari.arkko@piuha.net, cpignata@cisco.com
  RFC5495          ||      D. Li, J. Gao, A. Satyanarayana, S. Bardalai         ||       danli@huawei.com, gjhhit@huawei.com, asatyana@cisco.com, snigdho.bardalai@us.fujitsu.com
  RFC5496          ||      IJ. Wijnands, A. Boers, E. Rosen         ||       ice@cisco.com, aboers@cisco.com, erosen@cisco.com
  RFC5497          ||      T. Clausen, C. Dearlove         ||       T.Clausen@computer.org, chris.dearlove@baesystems.com
  RFC5498          ||      I. Chakeres         ||       ian.chakeres@gmail.com
  RFC5501          ||      Y. Kamite, Ed., Y. Wada, Y. Serbest, T. Morin, L. Fang         ||       y.kamite@ntt.com, wada.yuichiro@lab.ntt.co.jp, yetik_serbest@labs.att.com, thomas.morin@francetelecom.com, lufang@cisco.com
  RFC5502          ||      J. van Elburg         ||       HansErik.van.Elburg@ericsson.com
  RFC5503          ||      F. Andreasen, B. McKibben, B. Marshall         ||       fandreas@cisco.com, B.McKibben@cablelabs.com, wtm@research.att.com
  RFC5504          ||      K. Fujiwara, Ed., Y. Yoneya, Ed.         ||       fujiwara@jprs.co.jp, yone@jprs.co.jp
  RFC5505          ||      B. Aboba, D. Thaler, L. Andersson, S. Cheshire         ||       bernarda@microsoft.com, dthaler@microsoft.com, loa.andersson@ericsson.com, cheshire@apple.com
  RFC5506          ||      I. Johansson, M. Westerlund         ||       ingemar.s.johansson@ericsson.com, magnus.westerlund@ericsson.com
  RFC5507          ||      IAB, P. Faltstrom, Ed., R. Austein, Ed., P. Koch, Ed.         ||       iab@iab.org, paf@cisco.com, sra@isc.org, pk@denic.de
  RFC5508          ||      P. Srisuresh, B. Ford, S. Sivakumar, S. Guha         ||       srisuresh@yahoo.com, baford@mpi-sws.org, ssenthil@cisco.com, saikat@cs.cornell.edu
  RFC5509          ||      S. Loreto         ||       Salvatore.Loreto@ericsson.com
  RFC5510          ||      J. Lacan, V. Roca, J. Peltotalo, S. Peltotalo         ||       jerome.lacan@isae.fr, vincent.roca@inria.fr, jani.peltotalo@tut.fi, sami.peltotalo@tut.fi
  RFC5511          ||      A. Farrel         ||       adrian@olddog.co.uk
  RFC5512          ||      P. Mohapatra, E. Rosen         ||       pmohapat@cisco.com, erosen@cisco.com
  RFC5513          ||      A. Farrel         ||       adrian@olddog.co.uk
  RFC5514          ||      E. Vyncke         ||       evyncke@cisco.com
  RFC5515          ||      V. Mammoliti, C. Pignataro, P. Arberg, J. Gibbons, P. Howard         ||       vince@cisco.com, cpignata@cisco.com, parberg@redback.com, jgibbons@juniper.net, howsoft@mindspring.com
  RFC5516          ||      M. Jones, L. Morand         ||       mark.jones@bridgewatersystems.com, lionel.morand@orange-ftgroup.com
  RFC5517          ||      S. HomChaudhuri, M. Foschiano         ||       sanjibhc@gmail.com, foschia@cisco.com
  RFC5518          ||      P. Hoffman, J. Levine, A. Hathcock         ||       paul.hoffman@domain-assurance.org, john.levine@domain-assurance.org, arvel.hathcock@altn.com
  RFC5519          ||      J. Chesterfield, B. Haberman, Ed.         ||       julian.chesterfield@cl.cam.ac.uk, brian@innovationslab.net
  RFC5520          ||      R. Bradford, Ed., JP. Vasseur, A. Farrel         ||       rbradfor@cisco.com, jpv@cisco.com, adrian@olddog.co.uk
  RFC5521          ||      E. Oki, T. Takeda, A. Farrel         ||       oki@ice.uec.ac.jp, takeda.tomonori@lab.ntt.co.jp, adrian@olddog.co.uk
  RFC5522          ||      W. Eddy, W. Ivancic, T. Davis         ||       weddy@grc.nasa.gov, William.D.Ivancic@grc.nasa.gov, Terry.L.Davis@boeing.com
  RFC5523          ||      L. Berger         ||       lberger@labn.net
  RFC5524          ||      D. Cridland         ||       dave.cridland@isode.com
  RFC5525          ||      T. Dreibholz, J. Mulik         ||       dreibh@iem.uni-due.de, jaiwant@mulik.com
  RFC5526          ||      J. Livingood, P. Pfautz, R. Stastny         ||       jason_livingood@cable.comcast.com, ppfautz@att.com, richard.stastny@gmail.com
  RFC5527          ||      M. Haberler, O. Lendl, R. Stastny         ||       ietf@mah.priv.at, otmar.lendl@enum.at, richardstastny@gmail.com
  RFC5528          ||      A. Kato, M. Kanda, S. Kanno         ||       akato@po.ntts.co.jp, kanda.masayuki@lab.ntt.co.jp, kanno-s@po.ntts.co.jp
  RFC5529          ||      A. Kato, M. Kanda, S. Kanno         ||       akato@po.ntts.co.jp, kanda.masayuki@lab.ntt.co.jp, kanno-s@po.ntts.co.jp
  RFC5530          ||      A. Gulbrandsen         ||       arnt@oryx.com
  RFC5531          ||      R. Thurlow         ||       robert.thurlow@sun.com
  RFC5532          ||      T. Talpey, C. Juszczak         ||       tmtalpey@gmail.com, chetnh@earthlink.net
  RFC5533          ||      E. Nordmark, M. Bagnulo         ||       erik.nordmark@sun.com, marcelo@it.uc3m.es
  RFC5534          ||      J. Arkko, I. van Beijnum         ||       jari.arkko@ericsson.com, iljitsch@muada.com
  RFC5535          ||      M. Bagnulo         ||       marcelo@it.uc3m.es
  RFC5536          ||      K. Murchison, Ed., C. Lindsey, D. Kohn         ||       murch@andrew.cmu.edu, chl@clerew.man.ac.uk, dan@dankohn.com
  RFC5537          ||      R. Allbery, Ed., C. Lindsey         ||       rra@stanford.edu, chl@clerew.man.ac.uk
  RFC5538          ||      F. Ellermann         ||       hmdmhdfmhdjmzdtjmzdtzktdkztdjz@gmail.com
  RFC5539          ||      M. Badra         ||       badra@isima.fr
  RFC5540          ||      RFC Editor         ||       rfc-editor@rfc-editor.org
  RFC5541          ||      JL. Le Roux, JP. Vasseur, Y. Lee         ||       jeanlouis.leroux@orange-ftgroup.com, jpv@cisco.com, ylee@huawei.com
  RFC5542          ||      T. Nadeau, Ed., D. Zelig, Ed., O. Nicklass, Ed.         ||       tom.nadeau@bt.com, davidz@oversi.com, orlyn@radvision.com
  RFC5543          ||      H. Ould-Brahim, D. Fedyk, Y. Rekhter         ||       hbrahim@nortel.com, donald.fedyk@alcatel-lucent.com, yakov@juniper.com
  RFC5544          ||      A. Santoni         ||       adriano.santoni@actalis.it
  RFC5545          ||      B. Desruisseaux, Ed.         ||       bernard.desruisseaux@oracle.com
  RFC5546          ||      C. Daboo, Ed.         ||       cyrus@daboo.name
  RFC5547          ||      M. Garcia-Martin, M. Isomaki, G. Camarillo, S. Loreto, P. Kyzivat         ||       miguel.a.garcia@ericsson.com, markus.isomaki@nokia.com, Gonzalo.Camarillo@ericsson.com, Salvatore.Loreto@ericsson.com, pkyzivat@cisco.com
  RFC5548          ||      M. Dohler, Ed., T. Watteyne, Ed., T. Winter, Ed., D. Barthel, Ed.         ||       mischa.dohler@cttc.es, watteyne@eecs.berkeley.edu, wintert@acm.org, Dominique.Barthel@orange-ftgroup.com
  RFC5549          ||      F. Le Faucheur, E. Rosen         ||       flefauch@cisco.com, erosen@cisco.com
  RFC5550          ||      D. Cridland, Ed., A. Melnikov, Ed., S. Maes, Ed.         ||       dave.cridland@isode.com, Alexey.Melnikov@isode.com, stephane.maes@oracle.com
  RFC5551          ||      R. Gellens, Ed.         ||       rg+ietf@qualcomm.com
  RFC5552          ||      D. Burke, M. Scott         ||       daveburke@google.com, Mark.Scott@genesyslab.com
  RFC5553          ||      A. Farrel, Ed., R. Bradford, JP. Vasseur         ||       adrian@olddog.co.uk, rbradfor@cisco.com, jpv@cisco.com
  RFC5554          ||      N. Williams         ||       Nicolas.Williams@sun.com
  RFC5555          ||      H. Soliman, Ed.         ||       hesham@elevatemobile.com
  RFC5556          ||      J. Touch, R. Perlman         ||       touch@isi.edu, Radia.Perlman@sun.com
  RFC5557          ||      Y. Lee, JL. Le Roux, D. King, E. Oki         ||       ylee@huawei.com, jeanlouis.leroux@orange-ftgroup.com, daniel@olddog.co.uk, oki@ice.uec.ac.jp
  RFC5558          ||      F. Templin, Ed.         ||       fltemplin@acm.org
  RFC5559          ||      P. Eardley, Ed.         ||       philip.eardley@bt.com
  RFC5560          ||      H. Uijterwaal         ||       henk@ripe.net
  RFC5561          ||      B. Thomas, K. Raza, S. Aggarwal, R. Aggarwal, JL. Le Roux         ||       bobthomas@alum.mit.edu, skraza@cisco.com, shivani@juniper.net, rahul@juniper.net, jeanlouis.leroux@orange-ftgroup.com
  RFC5562          ||      A. Kuzmanovic, A. Mondal, S. Floyd, K. Ramakrishnan         ||       akuzma@northwestern.edu, a-mondal@northwestern.edu, floyd@icir.org, kkrama@research.att.com
  RFC5563          ||      K. Leung, G. Dommety, P. Yegani, K. Chowdhury         ||       kleung@cisco.com, gdommety@cisco.com, pyegani@cisco.com, kchowdhury@starentnetworks.com
  RFC5564          ||      A. El-Sherbiny, M. Farah, I. Oueichek, A. Al-Zoman         ||       El-sherbiny@un.org, farah14@un.org, oueichek@scs-net.org, azoman@citc.gov.sa
  RFC5565          ||      J. Wu, Y. Cui, C. Metz, E. Rosen         ||       jianping@cernet.edu.cn, yong@csnet1.cs.tsinghua.edu.cn, chmetz@cisco.com, erosen@cisco.com
  RFC5566          ||      L. Berger, R. White, E. Rosen         ||       lberger@labn.net, riw@cisco.com, erosen@cisco.com
  RFC5567          ||      T. Melanchuk, Ed.         ||       tim.melanchuk@gmail.com
  RFC5568          ||      R. Koodli, Ed.         ||       rkoodli@starentnetworks.com
  RFC5569          ||      R. Despres         ||       remi.despres@free.fr
  RFC5570          ||      M. StJohns, R. Atkinson, G. Thomas         ||       mstjohns@comcast.net, rja@extremenetworks.com, none
  RFC5571          ||      B. Storer, C. Pignataro, Ed., M. Dos Santos, B. Stevant, Ed., L. Toutain, J. Tremblay         ||       bstorer@cisco.com, cpignata@cisco.com, mariados@cisco.com, bruno.stevant@telecom-bretagne.eu, laurent.toutain@telecom-bretagne.eu, jf@jftremblay.com
  RFC5572          ||      M. Blanchet, F. Parent         ||       Marc.Blanchet@viagenie.ca, Florent.Parent@beon.ca
  RFC5573          ||      M. Thomson         ||       martin.thomson@andrew.com
  RFC5574          ||      G. Herlein, J. Valin, A. Heggestad, A. Moizard         ||       gherlein@herlein.com, jean-marc.valin@usherbrooke.ca, aeh@db.org, jack@atosc.org
  RFC5575          ||      P. Marques, N. Sheth, R. Raszuk, B. Greene, J. Mauch, D. McPherson         ||       roque@cisco.com, nsheth@juniper.net, raszuk@cisco.com, bgreene@juniper.net, jmauch@us.ntt.net, danny@arbor.net
  RFC5576          ||      J. Lennox, J. Ott, T. Schierl         ||       jonathan@vidyo.com, jo@acm.org, ts@thomas-schierl.de
  RFC5577          ||      P. Luthi, R. Even         ||       patrick.luthi@tandberg.no, ron.even.tlv@gmail.com
  RFC5578          ||      B. Berry, Ed., S. Ratliff, E. Paradise, T. Kaiser, M. Adams         ||       bberry@cisco.com, sratliff@cisco.com, pdice@cisco.com, timothy.kaiser@harris.com, Michael.D.Adams@L-3com.com
  RFC5579          ||      F. Templin, Ed.         ||       fltemplin@acm.org
  RFC5580          ||      H. Tschofenig, Ed., F. Adrangi, M. Jones, A. Lior, B. Aboba         ||       Hannes.Tschofenig@gmx.net, farid.adrangi@intel.com, mark.jones@bridgewatersystems.com, avi@bridgewatersystems.com, bernarda@microsoft.com
  RFC5581          ||      D. Shaw         ||       dshaw@jabberwocky.com
  RFC5582          ||      H. Schulzrinne         ||       hgs+ecrit@cs.columbia.edu
  RFC5583          ||      T. Schierl, S. Wenger         ||       ts@thomas-schierl.de, stewe@stewe.org
  RFC5584          ||      M. Hatanaka, J. Matsumoto         ||       actech@jp.sony.com, actech@jp.sony.com
  RFC5585          ||      T. Hansen, D. Crocker, P. Hallam-Baker         ||       tony+dkimov@maillennium.att.com, dcrocker@bbiw.net, phillip@hallambaker.com
  RFC5586          ||      M. Bocci, Ed., M. Vigoureux, Ed., S. Bryant, Ed.         ||       matthew.bocci@alcatel-lucent.com, martin.vigoureux@alcatel-lucent.com, stbryant@cisco.com
  RFC5587          ||      N. Williams         ||       Nicolas.Williams@sun.com
  RFC5588          ||      N. Williams         ||       Nicolas.Williams@sun.com
  RFC5589          ||      R. Sparks, A. Johnston, Ed., D. Petrie         ||       RjS@nostrum.com, alan@sipstation.com, dan.ietf@SIPez.com
  RFC5590          ||      D. Harrington, J. Schoenwaelder         ||       ietfdbh@comcast.net, j.schoenwaelder@jacobs-university.de
  RFC5591          ||      D. Harrington, W. Hardaker         ||       ietfdbh@comcast.net, ietf@hardakers.net
  RFC5592          ||      D. Harrington, J. Salowey, W. Hardaker         ||       ietfdbh@comcast.net, jsalowey@cisco.com, ietf@hardakers.net
  RFC5593          ||      N. Cook         ||       neil.cook@noware.co.uk
  RFC5594          ||      J. Peterson, A. Cooper         ||       jon.peterson@neustar.biz, acooper@cdt.org
  RFC5595          ||      G. Fairhurst         ||       gorry@erg.abdn.ac.uk
  RFC5596          ||      G. Fairhurst         ||       gorry@erg.abdn.ac.uk
  RFC5597          ||      R. Denis-Courmont         ||       rem@videolan.org
  RFC5598          ||      D. Crocker         ||       dcrocker@bbiw.net
  RFC5601          ||      T. Nadeau, Ed., D. Zelig, Ed.         ||       thomas.nadeau@bt.com, davidz@oversi.com
  RFC5602          ||      D. Zelig, Ed., T. Nadeau, Ed.         ||       davidz@oversi.com, tom.nadeau@bt.com
  RFC5603          ||      D. Zelig, Ed., T. Nadeau, Ed.         ||       davidz@oversi.com, tom.nadeau@bt.com
  RFC5604          ||      O. Nicklass         ||       orlyn@radvision.com
  RFC5605          ||      O. Nicklass, T. Nadeau         ||       orlyn@radvision.com, tom.nadeau@bt.com
  RFC5606          ||      J. Peterson, T. Hardie, J. Morris         ||       jon.peterson@neustar.biz, hardie@qualcomm.com, jmorris@cdt.org
  RFC5607          ||      D. Nelson, G. Weber         ||       dnelson@elbrysnetworks.com, gdweber@gmail.com
  RFC5608          ||      K. Narayan, D. Nelson         ||       kaushik_narayan@yahoo.com, dnelson@elbrysnetworks.com
  RFC5609          ||      V. Fajardo, Ed., Y. Ohba, R. Marin-Lopez         ||       vfajardo@research.telcordia.com, yoshihiro.ohba@toshiba.co.jp, rafa@um.es
  RFC5610          ||      E. Boschi, B. Trammell, L. Mark, T. Zseby         ||       elisa.boschi@hitachi-eu.com, brian.trammell@hitachi-eu.com, lutz.mark@ifam.fraunhofer.de, tanja.zseby@fokus.fraunhofer.de
  RFC5611          ||      A. Vainshtein, S. Galtzur         ||       Alexander.Vainshtein@ecitele.com, sharon.galtzur@rebellion.co.uk
  RFC5612          ||      P. Eronen, D. Harrington         ||       pe@iki.fi, dharrington@huawei.com
  RFC5613          ||      A. Zinin, A. Roy, L. Nguyen, B. Friedman, D. Yeung         ||       alex.zinin@alcatel-lucent.com, akr@cisco.com, lhnguyen@cisco.com, barryf@google.com, myeung@cisco.com
  RFC5614          ||      R. Ogier, P. Spagnolo         ||       rich.ogier@earthlink.net, phillipspagnolo@gmail.com
  RFC5615          ||      C. Groves, Y. Lin         ||       Christian.Groves@nteczone.com, linyangbo@huawei.com
  RFC5616          ||      N. Cook         ||       neil.cook@noware.co.uk
  RFC5617          ||      E. Allman, J. Fenton, M. Delany, J. Levine         ||       eric+dkim@sendmail.org, fenton@bluepopcorn.net, markd+dkim@yahoo-inc.com, standards@taugh.com
  RFC5618          ||      A. Morton, K. Hedayat         ||       acmorton@att.com, kaynam.hedayat@exfo.com
  RFC5619          ||      S. Yamamoto, C. Williams, H. Yokota, F. Parent         ||       shu@nict.go.jp, carlw@mcsr-labs.org, yokota@kddilabs.jp, Florent.Parent@beon.ca
  RFC5620          ||      O. Kolkman, Ed., IAB         ||       olaf@nlnetlabs.nl, iab@iab.org
  RFC5621          ||      G. Camarillo         ||       Gonzalo.Camarillo@ericsson.com
  RFC5622          ||      S. Floyd, E. Kohler         ||       floyd@icir.org, kohler@cs.ucla.edu
  RFC5623          ||      E. Oki, T. Takeda, JL. Le Roux, A. Farrel         ||       oki@ice.uec.ac.jp, takeda.tomonori@lab.ntt.co.jp, jeanlouis.leroux@orange-ftgroup.com, adrian@olddog.co.uk
  RFC5624          ||      J. Korhonen, Ed., H. Tschofenig, E. Davies         ||       jouni.korhonen@nsn.com, Hannes.Tschofenig@gmx.net, elwynd@dial.pipex.com
  RFC5625          ||      R. Bellis         ||       ray.bellis@nominet.org.uk
  RFC5626          ||      C. Jennings, Ed., R. Mahy, Ed., F. Audet, Ed.         ||       fluffy@cisco.com, rohan@ekabal.com, francois.audet@skypelabs.com
  RFC5627          ||      J. Rosenberg         ||       jdrosen@cisco.com
  RFC5628          ||      P. Kyzivat         ||       pkyzivat@cisco.com
  RFC5629          ||      J. Rosenberg         ||       jdrosen@cisco.com
  RFC5630          ||      F. Audet         ||       francois.audet@skypelabs.com
  RFC5631          ||      R. Shacham, H. Schulzrinne, S. Thakolsri, W. Kellerer         ||       shacham@cs.columbia.edu, hgs@cs.columbia.edu, thakolsri@docomolab-euro.com, kellerer@docomolab-euro.com
  RFC5632          ||      C. Griffiths, J. Livingood, L. Popkin, R. Woundy, Y. Yang         ||       chris_griffiths@cable.comcast.com, jason_livingood@cable.comcast.com, laird@pando.com, richard_woundy@cable.comcast.com, yry@cs.yale.edu
  RFC5633          ||      S. Dawkins, Ed.         ||       spencer@wonderhamster.org
  RFC5634          ||      G. Fairhurst, A. Sathiaseelan         ||       gorry@erg.abdn.ac.uk, arjuna@erg.abdn.ac.uk
  RFC5635          ||      W. Kumari, D. McPherson         ||       warren@kumari.net, danny@arbor.net
  RFC5636          ||      S. Park, H. Park, Y. Won, J. Lee, S. Kent         ||       shpark@kisa.or.kr, hrpark@kisa.or.kr, yjwon@kisa.or.kr, jilee@kisa.or.kr, kent@bbn.com
  RFC5637          ||      G. Giaretta, I. Guardini, E. Demaria, J. Bournelle, R. Lopez         ||       gerardo@qualcomm.com, ivano.guardini@telecomitalia.it, elena.demaria@telecomitalia.it, julien.bournelle@gmail.com, rafa@dif.um.es
  RFC5638          ||      H. Sinnreich, Ed., A. Johnston, E. Shim, K. Singh         ||       henrys@adobe.com, alan@sipstation.com, eunsooshim@gmail.com, kns10@cs.columbia.edu
  RFC5639          ||      M. Lochter, J. Merkle         ||       manfred.lochter@bsi.bund.de, johannes.merkle@secunet.com
  RFC5640          ||      C. Filsfils, P. Mohapatra, C. Pignataro         ||       cfilsfil@cisco.com, pmohapat@cisco.com, cpignata@cisco.com
  RFC5641          ||      N. McGill, C. Pignataro         ||       nmcgill@cisco.com, cpignata@cisco.com
  RFC5642          ||      S. Venkata, S. Harwani, C. Pignataro, D. McPherson         ||       svenkata@google.com, sharwani@cisco.com, cpignata@cisco.com, danny@arbor.net
  RFC5643          ||      D. Joyal, Ed., V. Manral, Ed.         ||       djoyal@nortel.com, vishwas@ipinfusion.com
  RFC5644          ||      E. Stephan, L. Liang, A. Morton         ||       emile.stephan@orange-ftgroup.com, L.Liang@surrey.ac.uk, acmorton@att.com
  RFC5645          ||      D. Ewell, Ed.         ||       doug@ewellic.org
  RFC5646          ||      A. Phillips, Ed., M. Davis, Ed.         ||       addison@inter-locale.com, markdavis@google.com
  RFC5647          ||      K. Igoe, J. Solinas         ||       kmigoe@nsa.gov, jasolin@orion.ncsc.mil
  RFC5648          ||      R. Wakikawa, Ed., V. Devarapalli, G. Tsirtsis, T. Ernst, K. Nagami         ||       ryuji.wakikawa@gmail.com, vijay@wichorus.com, Tsirtsis@gmail.com, thierry.ernst@inria.fr, nagami@inetcore.com
  RFC5649          ||      R. Housley, M. Dworkin         ||       housley@vigilsec.com, dworkin@nist.gov
  RFC5650          ||      M. Morgenstern, S. Baillie, U. Bonollo         ||       moti.Morgenstern@ecitele.com, scott.baillie@nec.com.au, umberto.bonollo@nec.com.au
  RFC5651          ||      M. Luby, M. Watson, L. Vicisano         ||       luby@qti.qualcomm.com, watson@qualcomm.com, vicisano@qualcomm.com
  RFC5652          ||      R. Housley         ||       housley@vigilsec.com
  RFC5653          ||      M. Upadhyay, S. Malkani         ||       m.d.upadhyay+ietf@gmail.com, Seema.Malkani@gmail.com
  RFC5654          ||      B. Niven-Jenkins, Ed., D. Brungard, Ed., M. Betts, Ed., N. Sprecher, S. Ueno         ||       benjamin.niven-jenkins@bt.com, dbrungard@att.com, malcolm.betts@huawei.com, nurit.sprecher@nsn.com, satoshi.ueno@ntt.com
  RFC5655          ||      B. Trammell, E. Boschi, L. Mark, T. Zseby, A. Wagner         ||       brian.trammell@hitachi-eu.com, elisa.boschi@hitachi-eu.com, lutz.mark@ifam.fraunhofer.de, tanja.zseby@fokus.fraunhofer.de, arno@wagner.name
  RFC5656          ||      D. Stebila, J. Green         ||       douglas@stebila.ca, jonathan.green@queensu.ca
  RFC5657          ||      L. Dusseault, R. Sparks         ||       lisa.dusseault@gmail.com, RjS@nostrum.com
  RFC5658          ||      T. Froment, C. Lebel, B. Bonnaerens         ||       thomas.froment@tech-invite.com, Christophe.Lebel@alcatel-lucent.fr, ben.bonnaerens@alcatel-lucent.be
  RFC5659          ||      M. Bocci, S. Bryant         ||       matthew.bocci@alcatel-lucent.com, stbryant@cisco.com
  RFC5660          ||      N. Williams         ||       Nicolas.Williams@sun.com
  RFC5661          ||      S. Shepler, Ed., M. Eisler, Ed., D. Noveck, Ed.         ||       shepler@storspeed.com, mike@eisler.com, dnoveck@netapp.com
  RFC5662          ||      S. Shepler, Ed., M. Eisler, Ed., D. Noveck, Ed.         ||       shepler@storspeed.com, mike@eisler.com, dnoveck@netapp.com
  RFC5663          ||      D. Black, S. Fridella, J. Glasgow         ||       black_david@emc.com, stevef@nasuni.com, jglasgow@aya.yale.edu
  RFC5664          ||      B. Halevy, B. Welch, J. Zelenka         ||       bhalevy@panasas.com, welch@panasas.com, jimz@panasas.com
  RFC5665          ||      M. Eisler         ||       mike@eisler.com
  RFC5666          ||      T. Talpey, B. Callaghan         ||       tmtalpey@gmail.com, brentc@apple.com
  RFC5667          ||      T. Talpey, B. Callaghan         ||       tmtalpey@gmail.com, brentc@apple.com
  RFC5668          ||      Y. Rekhter, S. Sangli, D. Tappan         ||       yakov@juniper.net, rsrihari@cisco.com, Dan.Tappan@Gmail.com
  RFC5669          ||      S. Yoon, J. Kim, H. Park, H. Jeong, Y. Won         ||       seokung@kisa.or.kr, seopo@kisa.or.kr, hrpark@kisa.or.kr, hcjung@kisa.or.kr, yjwon@kisa.or.kr
  RFC5670          ||      P. Eardley, Ed.         ||       philip.eardley@bt.com
  RFC5671          ||      S. Yasukawa, A. Farrel, Ed.         ||       yasukawa.seisho@lab.ntt.co.jp, adrian@olddog.co.uk
  RFC5672          ||      D. Crocker, Ed.         ||       dcrocker@bbiw.net
  RFC5673          ||      K. Pister, Ed., P. Thubert, Ed., S. Dwars, T. Phinney         ||       kpister@dustnetworks.com, pthubert@cisco.com, sicco.dwars@shell.com, tom.phinney@cox.net
  RFC5674          ||      S. Chisholm, R. Gerhards         ||       schishol@nortel.com, rgerhards@adiscon.com
  RFC5675          ||      V. Marinov, J. Schoenwaelder         ||       v.marinov@jacobs-university.de, j.schoenwaelder@jacobs-university.de
  RFC5676          ||      J. Schoenwaelder, A. Clemm, A. Karmakar         ||       j.schoenwaelder@jacobs-university.de, alex@cisco.com, akarmaka@cisco.com
  RFC5677          ||      T. Melia, Ed., G. Bajko, S. Das, N. Golmie, JC. Zuniga         ||       telemaco.melia@alcatel-lucent.com, Gabor.Bajko@nokia.com, subir@research.telcordia.com, nada.golmie@nist.gov, j.c.zuniga@ieee.org
  RFC5678          ||      G. Bajko, S. Das         ||       gabor.bajko@nokia.com, subir@research.telcordia.com
  RFC5679          ||      G. Bajko         ||       gabor.bajko@nokia.com
  RFC5680          ||      S. Dawkins, Ed.         ||       spencer@wonderhamster.org
  RFC5681          ||      M. Allman, V. Paxson, E. Blanton         ||       mallman@icir.org, vern@icir.org, eblanton@cs.purdue.edu
  RFC5682          ||      P. Sarolahti, M. Kojo, K. Yamamoto, M. Hata         ||       pasi.sarolahti@iki.fi, kojo@cs.helsinki.fi, yamamotokaz@nttdocomo.co.jp, hatama@s1.nttdocomo.co.jp
  RFC5683          ||      A. Brusilovsky, I. Faynberg, Z. Zeltsan, S. Patel         ||       Alec.Brusilovsky@alcatel-lucent.com, igor.faynberg@alcatel-lucent.com, zeltsan@alcatel-lucent.com, sarvar@google.com
  RFC5684          ||      P. Srisuresh, B. Ford         ||       srisuresh@yahoo.com, bryan.ford@yale.edu
  RFC5685          ||      V. Devarapalli, K. Weniger         ||       vijay@wichorus.com, kilian.weniger@googlemail.com
  RFC5686          ||      Y. Hiwasaki, H. Ohmuro         ||       hiwasaki.yusuke@lab.ntt.co.jp, ohmuro.hitoshi@lab.ntt.co.jp
  RFC5687          ||      H. Tschofenig, H. Schulzrinne         ||       Hannes.Tschofenig@gmx.net, hgs+ecrit@cs.columbia.edu
  RFC5688          ||      J. Rosenberg         ||       jdrosen@jdrosen.net
  RFC5689          ||      C. Daboo         ||       cyrus@daboo.name
  RFC5690          ||      S. Floyd, A. Arcia, D. Ros, J. Iyengar         ||       floyd@icir.org, ae.arcia@telecom-bretagne.eu, David.Ros@telecom-bretagne.eu, jiyengar@fandm.edu
  RFC5691          ||      F. de Bont, S. Doehla, M. Schmidt, R. Sperschneider         ||       frans.de.bont@philips.com, stefan.doehla@iis.fraunhofer.de, malte.schmidt@dolby.com, ralph.sperschneider@iis.fraunhofer.de
  RFC5692          ||      H. Jeon, S. Jeong, M. Riegel         ||       hongseok.jeon@gmail.com, sjjeong@etri.re.kr, maximilian.riegel@nsn.com
  RFC5693          ||      J. Seedorf, E. Burger         ||       jan.seedorf@nw.neclab.eu, eburger@standardstrack.com
  RFC5694          ||      G. Camarillo, Ed., IAB         ||       Gonzalo.Camarillo@ericsson.com, iab@iab.org
  RFC5695          ||      A. Akhter, R. Asati, C. Pignataro         ||       aakhter@cisco.com, rajiva@cisco.com, cpignata@cisco.com
  RFC5696          ||      T. Moncaster, B. Briscoe, M. Menth         ||       toby.moncaster@bt.com, bob.briscoe@bt.com, menth@informatik.uni-wuerzburg.de
  RFC5697          ||      S. Farrell         ||       stephen.farrell@cs.tcd.ie
  RFC5698          ||      T. Kunz, S. Okunick, U. Pordesch         ||       thomas.kunz@sit.fraunhofer.de, susanne.okunick@pawisda.de, ulrich.pordesch@zv.fraunhofer.de
  RFC5701          ||      Y. Rekhter         ||       yakov@juniper.net
  RFC5702          ||      J. Jansen         ||       jelte@NLnetLabs.nl
  RFC5703          ||      T. Hansen, C. Daboo         ||       tony+sieveloop@maillennium.att.com, cyrus@daboo.name
  RFC5704          ||      S. Bryant, Ed., M. Morrow, Ed., IAB         ||       stbryant@cisco.com, mmorrow@cisco.com, iab@iab.org
  RFC5705          ||      E. Rescorla         ||       ekr@rtfm.com
  RFC5706          ||      D. Harrington         ||       ietfdbh@comcast.net
  RFC5707          ||      A. Saleem, Y. Xin, G. Sharratt         ||       adnan.saleem@RadiSys.com, yong.xin@RadiSys.com, garland.sharratt@gmail.com
  RFC5708          ||      A. Keromytis         ||       angelos@cs.columbia.edu
  RFC5709          ||      M. Bhatia, V. Manral, M. Fanto, R. White, M. Barnes, T. Li, R. Atkinson         ||       manav@alcatel-lucent.com, vishwas@ipinfusion.com, mfanto@aegisdatasecurity.com, riw@cisco.com, mjbarnes@cisco.com, tony.li@tony.li, rja@extremenetworks.com
  RFC5710          ||      L. Berger, D. Papadimitriou, JP. Vasseur         ||       lberger@labn.net, Dimitri.Papadimitriou@alcatel-lucent.be, jpv@cisco.com
  RFC5711          ||      JP. Vasseur, Ed., G. Swallow, I. Minei         ||       jpv@cisco.com, swallow@cisco.com, ina@juniper.net
  RFC5712          ||      M. Meyer, Ed., JP. Vasseur, Ed.         ||       matthew.meyer@bt.com, jpv@cisco.com
  RFC5713          ||      H. Moustafa, H. Tschofenig, S. De Cnodder         ||       hassnaa.moustafa@orange-ftgroup.com, Hannes.Tschofenig@gmx.net, stefaan.de_cnodder@alcatel-lucent.com
  RFC5714          ||      M. Shand, S. Bryant         ||       mshand@cisco.com, stbryant@cisco.com
  RFC5715          ||      M. Shand, S. Bryant         ||       mshand@cisco.com, stbryant@cisco.com
  RFC5716          ||      J. Lentini, C. Everhart, D. Ellard, R. Tewari, M. Naik         ||       jlentini@netapp.com, everhart@netapp.com, dellard@bbn.com, tewarir@us.ibm.com, manoj@almaden.ibm.com
  RFC5717          ||      B. Lengyel, M. Bjorklund         ||       balazs.lengyel@ericsson.com, mbj@tail-f.com
  RFC5718          ||      D. Beller, A. Farrel         ||       dieter.beller@alcatel-lucent.com, adrian@olddog.co.uk
  RFC5719          ||      D. Romascanu, H. Tschofenig         ||       dromasca@gmail.com , Hannes.Tschofenig@gmx.net
  RFC5720          ||      F. Templin         ||       fltemplin@acm.org
  RFC5721          ||      R. Gellens, C. Newman         ||       rg+ietf@qualcomm.com, chris.newman@sun.com
  RFC5722          ||      S. Krishnan         ||       suresh.krishnan@ericsson.com
  RFC5723          ||      Y. Sheffer, H. Tschofenig         ||       yaronf@checkpoint.com, Hannes.Tschofenig@gmx.net
  RFC5724          ||      E. Wilde, A. Vaha-Sipila         ||       dret@berkeley.edu, antti.vaha-sipila@nokia.com
  RFC5725          ||      A. Begen, D. Hsu, M. Lague         ||       abegen@cisco.com, dohsu@cisco.com, mlague@cisco.com
  RFC5726          ||      Y. Qiu, F. Zhao, Ed., R. Koodli         ||       qiuying@i2r.a-star.edu.sg, fanzhao@google.com, rkoodli@cisco.com
  RFC5727          ||      J. Peterson, C. Jennings, R. Sparks         ||       jon.peterson@neustar.biz, fluffy@cisco.com, rjsparks@nostrum.com
  RFC5728          ||      S. Combes, P. Amundsen, M. Lambert, H-P. Lexow         ||       stephane.combes@esa.int, pca@verisat.no, micheline.lambert@advantechamt.com, hlexow@stmi.com
  RFC5729          ||      J. Korhonen, Ed., M. Jones, L. Morand, T. Tsou         ||       jouni.nospam@gmail.com, Mark.Jones@bridgewatersystems.com, Lionel.morand@orange-ftgroup.com, tena@huawei.com
  RFC5730          ||      S. Hollenbeck         ||       shollenbeck@verisign.com
  RFC5731          ||      S. Hollenbeck         ||       shollenbeck@verisign.com
  RFC5732          ||      S. Hollenbeck         ||       shollenbeck@verisign.com
  RFC5733          ||      S. Hollenbeck         ||       shollenbeck@verisign.com
  RFC5734          ||      S. Hollenbeck         ||       shollenbeck@verisign.com
  RFC5735          ||      M. Cotton, L. Vegoda         ||       michelle.cotton@icann.org, leo.vegoda@icann.org
  RFC5736          ||      G. Huston, M. Cotton, L. Vegoda         ||       gih@apnic.net, michelle.cotton@icann.org, leo.vegoda@icann.org
  RFC5737          ||      J. Arkko, M. Cotton, L. Vegoda         ||       jari.arkko@piuha.net, michelle.cotton@icann.org, leo.vegoda@icann.org
  RFC5738          ||      P. Resnick, C. Newman         ||       presnick@qti.qualcomm.com, chris.newman@sun.com
  RFC5739          ||      P. Eronen, J. Laganier, C. Madson         ||       pe@iki.fi, julienl@qualcomm.com, cmadson@cisco.com
  RFC5740          ||      B. Adamson, C. Bormann, M. Handley, J. Macker         ||       adamson@itd.nrl.navy.mil, cabo@tzi.org, M.Handley@cs.ucl.ac.uk, macker@itd.nrl.navy.mil
  RFC5741          ||      L. Daigle, Ed., O. Kolkman, Ed., IAB         ||       leslie@thinkingcat.com, olaf@nlnetlabs.nl, iab@iab.org
  RFC5742          ||      H. Alvestrand, R. Housley         ||       harald@alvestrand.no, housley@vigilsec.com
  RFC5743          ||      A. Falk         ||       falk@bbn.com
  RFC5744          ||      R. Braden, J. Halpern         ||       braden@isi.edu, jhalpern@redback.com
  RFC5745          ||      A. Malis, Ed., IAB         ||       andrew.g.malis@verizon.com, iab@iab.org
  RFC5746          ||      E. Rescorla, M. Ray, S. Dispensa, N. Oskov         ||       ekr@rtfm.com, marsh@extendedsubset.com, dispensa@phonefactor.com, nasko.oskov@microsoft.com
  RFC5747          ||      J. Wu, Y. Cui, X. Li, M. Xu, C. Metz         ||       jianping@cernet.edu.cn, cy@csnet1.cs.tsinghua.edu.cn, xing@cernet.edu.cn, xmw@csnet1.cs.tsinghua.edu.cn, chmetz@cisco.com
  RFC5748          ||      S. Yoon, J. Jeong, H. Kim, H. Jeong, Y. Won         ||       seokung@kisa.or.kr, jijeong@kisa.or.kr, rinyfeel@kisa.or.kr, hcjung@kisa.or.kr, yjwon@kisa.or.kr
  RFC5749          ||      K. Hoeper, Ed., M. Nakhjiri, Y. Ohba, Ed.         ||       khoeper@motorola.com, madjid.nakhjiri@motorola.com, yoshihiro.ohba@toshiba.co.jp
  RFC5750          ||      B. Ramsdell, S. Turner         ||       blaker@gmail.com, turners@ieca.com
  RFC5751          ||      B. Ramsdell, S. Turner         ||       blaker@gmail.com, turners@ieca.com
  RFC5752          ||      S. Turner, J. Schaad         ||       turners@ieca.com, jimsch@exmsft.com
  RFC5753          ||      S. Turner, D. Brown         ||       turners@ieca.com, dbrown@certicom.com
  RFC5754          ||      S. Turner         ||       turners@ieca.com
  RFC5755          ||      S. Farrell, R. Housley, S. Turner         ||       stephen.farrell@cs.tcd.ie, housley@vigilsec.com, turners@ieca.com
  RFC5756          ||      S. Turner, D. Brown, K. Yiu, R. Housley, T. Polk         ||       turners@ieca.com, dbrown@certicom.com, kelviny@microsoft.com, housley@vigilsec.com, wpolk@nist.gov
  RFC5757          ||      T. Schmidt, M. Waehlisch, G. Fairhurst         ||       schmidt@informatik.haw-hamburg.de, mw@link-lab.net, gorry@erg.abdn.ac.uk
  RFC5758          ||      Q. Dang, S. Santesson, K. Moriarty, D. Brown, T. Polk         ||       quynh.dang@nist.gov, sts@aaa-sec.com, Moriarty_Kathleen@emc.com, dbrown@certicom.com, tim.polk@nist.gov
  RFC5759          ||      J. Solinas, L. Zieglar         ||       jasolin@orion.ncsc.mil, llziegl@tycho.ncsc.mil
  RFC5760          ||      J. Ott, J. Chesterfield, E. Schooler         ||       jo@acm.org, julianchesterfield@cantab.net, eve_schooler@acm.org
  RFC5761          ||      C. Perkins, M. Westerlund         ||       csp@csperkins.org, magnus.westerlund@ericsson.com
  RFC5762          ||      C. Perkins         ||       csp@csperkins.org
  RFC5763          ||      J. Fischl, H. Tschofenig, E. Rescorla         ||       jason.fischl@skype.net, Hannes.Tschofenig@gmx.net, ekr@rtfm.com
  RFC5764          ||      D. McGrew, E. Rescorla         ||       mcgrew@cisco.com, ekr@rtfm.com
  RFC5765          ||      H. Schulzrinne, E. Marocco, E. Ivov         ||       hgs@cs.columbia.edu, enrico.marocco@telecomitalia.it, emcho@sip-communicator.org
  RFC5766          ||      R. Mahy, P. Matthews, J. Rosenberg         ||       rohan@ekabal.com, philip_matthews@magma.ca, jdrosen@jdrosen.net
  RFC5767          ||      M. Munakata, S. Schubert, T. Ohba         ||       munakata.mayumi@lab.ntt.co.jp, shida@ntt-at.com, ohba.takumi@lab.ntt.co.jp
  RFC5768          ||      J. Rosenberg         ||       jdrosen@jdrosen.net
  RFC5769          ||      R. Denis-Courmont         ||       remi.denis-courmont@nokia.com
  RFC5770          ||      M. Komu, T. Henderson, H. Tschofenig, J. Melen, A. Keranen, Ed.         ||       miika@iki.fi, thomas.r.henderson@boeing.com, Hannes.Tschofenig@gmx.net, jan.melen@ericsson.com, ari.keranen@ericsson.com
  RFC5771          ||      M. Cotton, L. Vegoda, D. Meyer         ||       michelle.cotton@icann.org, leo.vegoda@icann.org, dmm@1-4-5.net
  RFC5772          ||      A. Doria, E. Davies, F. Kastenholz         ||       avri@ltu.se, elwynd@dial.pipex.com, frank@bbn.com
  RFC5773          ||      E. Davies, A. Doria         ||       elwynd@dial.pipex.com, avri@acm.org
  RFC5774          ||      K. Wolf, A. Mayrhofer         ||       karlheinz.wolf@nic.at, alexander.mayrhofer@nic.at
  RFC5775          ||      M. Luby, M. Watson, L. Vicisano         ||       luby@qti.qualcomm.com, watson@qualcomm.com, vicisano@qualcomm.com
  RFC5776          ||      V. Roca, A. Francillon, S. Faurite         ||       vincent.roca@inria.fr, aurelien.francillon@inria.fr, faurite@lcpc.fr
  RFC5777          ||      J. Korhonen, H. Tschofenig, M. Arumaithurai, M. Jones, Ed., A. Lior         ||       jouni.korhonen@nsn.com, Hannes.Tschofenig@gmx.net, mayutan.arumaithurai@gmail.com, mark.jones@bridgewatersystems.com, avi@bridgewatersystems.com
  RFC5778          ||      J. Korhonen, Ed., H. Tschofenig, J. Bournelle, G. Giaretta, M. Nakhjiri         ||       jouni.nospam@gmail.com, Hannes.Tschofenig@gmx.net, julien.bournelle@orange-ftgroup.com, gerardo.giaretta@gmail.com, madjid.nakhjiri@motorola.com
  RFC5779          ||      J. Korhonen, Ed., J. Bournelle, K. Chowdhury, A. Muhanna, U. Meyer         ||       jouni.nospam@gmail.com, julien.bournelle@orange-ftgroup.com, kchowdhury@cisco.com, Ahmad.muhanna@ericsson.com, meyer@umic.rwth-aachen.de
  RFC5780          ||      D. MacDonald, B. Lowekamp         ||       derek.macdonald@gmail.com, bbl@lowekamp.net
  RFC5781          ||      S. Weiler, D. Ward, R. Housley         ||       weiler@tislabs.com, dward@juniper.net, housley@vigilsec.com
  RFC5782          ||      J. Levine         ||       standards@taugh.com
  RFC5783          ||      M. Welzl, W. Eddy         ||       michawe@ifi.uio.no, wes@mti-systems.com
  RFC5784          ||      N. Freed, S. Vedam         ||       ned.freed@mrochek.com, Srinivas.Sv@Sun.COM
  RFC5785          ||      M. Nottingham, E. Hammer-Lahav         ||       mnot@mnot.net, eran@hueniverse.com
  RFC5786          ||      R. Aggarwal, K. Kompella         ||       rahul@juniper.net, kireeti@juniper.net
  RFC5787          ||      D. Papadimitriou         ||       dimitri.papadimitriou@alcatel-lucent.be
  RFC5788          ||      A. Melnikov, D. Cridland         ||       Alexey.Melnikov@isode.com, dave.cridland@isode.com
  RFC5789          ||      L. Dusseault, J. Snell         ||       lisa.dusseault@gmail.com, jasnell@gmail.com
  RFC5790          ||      H. Liu, W. Cao, H. Asaeda         ||       Liuhui47967@huawei.com, caowayne@huawei.com, asaeda@wide.ad.jp
  RFC5791          ||      J. Reschke, J. Kunze         ||       julian.reschke@greenbytes.de, jak@ucop.edu
  RFC5792          ||      P. Sangster, K. Narayan         ||       Paul_Sangster@symantec.com, kaushik@cisco.com
  RFC5793          ||      R. Sahita, S. Hanna, R. Hurst, K. Narayan         ||       Ravi.Sahita@intel.com, shanna@juniper.net, Ryan.Hurst@microsoft.com, kaushik@cisco.com
  RFC5794          ||      J. Lee, J. Lee, J. Kim, D. Kwon, C. Kim         ||       jklee@ensec.re.kr, jlee05@ensec.re.kr, jaeheon@ensec.re.kr, ds_kwon@ensec.re.kr, jbr@ensec.re.kr
  RFC5795          ||      K. Sandlund, G. Pelletier, L-E. Jonsson         ||       kristofer.sandlund@ericsson.com, ghyslain.pelletier@ericsson.com, lars-erik@lejonsson.com
  RFC5796          ||      W. Atwood, S. Islam, M. Siami         ||       bill@cse.concordia.ca, Salekul.Islam@emt.inrs.ca, mzrsm@yahoo.ca
  RFC5797          ||      J. Klensin, A. Hoenes         ||       john+ietf@jck.com, ah@TR-Sys.de
  RFC5798          ||      S. Nadas, Ed.         ||       stephen.nadas@ericsson.com
  RFC5801          ||      S. Josefsson, N. Williams         ||       simon@josefsson.org, Nicolas.Williams@oracle.com
  RFC5802          ||      C. Newman, A. Menon-Sen, A. Melnikov, N. Williams         ||       chris.newman@oracle.com, ams@toroid.org, Alexey.Melnikov@isode.com, Nicolas.Williams@oracle.com
  RFC5803          ||      A. Melnikov         ||       alexey.melnikov@isode.com
  RFC5804          ||      A. Melnikov, Ed., T. Martin         ||       Alexey.Melnikov@isode.com, timmartin@alumni.cmu.edu
  RFC5805          ||      K. Zeilenga         ||       Kurt.Zeilenga@Isode.COM
  RFC5806          ||      S. Levy, M. Mohali, Ed.         ||       stlevy@cisco.com, marianne.mohali@orange-ftgroup.com
  RFC5807          ||      Y. Ohba, A. Yegin         ||       yoshihiro.ohba@toshiba.co.jp, alper.yegin@yegin.org
  RFC5808          ||      R. Marshall, Ed.         ||       rmarshall@telecomsys.com
  RFC5810          ||      A. Doria, Ed., J. Hadi Salim, Ed., R. Haas, Ed., H. Khosravi, Ed., W. Wang, Ed., L. Dong, R. Gopal, J. Halpern         ||       avri@ltu.se, hadi@mojatatu.com, rha@zurich.ibm.com, hormuzd.m.khosravi@intel.com, wmwang@mail.zjgsu.edu.cn, donglg@zjgsu.edu.cn, ram.gopal@nsn.com, jmh@joelhalpern.com
  RFC5811          ||      J. Hadi Salim, K. Ogawa         ||       hadi@mojatatu.com, ogawa.kentaro@lab.ntt.co.jp
  RFC5812          ||      J. Halpern, J. Hadi Salim         ||       jmh@joelhalpern.com, hadi@mojatatu.com
  RFC5813          ||      R. Haas         ||       rha@zurich.ibm.com
  RFC5814          ||      W. Sun, Ed., G. Zhang, Ed.         ||       sunwq@mit.edu, zhangguoying@mail.ritt.com.cn
  RFC5815          ||      T. Dietz, Ed., A. Kobayashi, B. Claise, G. Muenz         ||       Thomas.Dietz@nw.neclab.eu, akoba@nttv6.net, bclaise@cisco.com, muenz@net.in.tum.de
  RFC5816          ||      S. Santesson, N. Pope         ||       sts@aaa-sec.com, nick.pope@thales-esecurity.com
  RFC5817          ||      Z. Ali, JP. Vasseur, A. Zamfir, J. Newton         ||       zali@cisco.com, jpv@cisco.com, ancaz@cisco.com, jonathan.newton@cw.com
  RFC5818          ||      D. Li, H. Xu, S. Bardalai, J. Meuric, D. Caviglia         ||       danli@huawei.com, xuhuiying@huawei.com, snigdho.bardalai@us.fujitsu.com, julien.meuric@orange-ftgroup.com, diego.caviglia@ericsson.com
  RFC5819          ||      A. Melnikov, T. Sirainen         ||       Alexey.Melnikov@isode.com, tss@iki.fi
  RFC5820          ||      A. Roy, Ed., M. Chandra, Ed.         ||       akr@cisco.com, mw.chandra@gmail.com
  RFC5824          ||      K. Kumaki, Ed., R. Zhang, Y. Kamite         ||       ke-kumaki@kddi.com, raymond.zhang@bt.com, y.kamite@ntt.com
  RFC5825          ||      K. Fujiwara, B. Leiba         ||       fujiwara@jprs.co.jp, barryleiba@computer.org
  RFC5826          ||      A. Brandt, J. Buron, G. Porcu         ||       abr@sdesigns.dk, jbu@sdesigns.dk, gporcu@gmail.com
  RFC5827          ||      M. Allman, K. Avrachenkov, U. Ayesta, J. Blanton, P. Hurtig         ||       mallman@icir.org, k.avrachenkov@sophia.inria.fr, urtzi@laas.fr, jblanton@irg.cs.ohiou.edu, per.hurtig@kau.se
  RFC5828          ||      D. Fedyk, L. Berger, L. Andersson         ||       donald.fedyk@alcatel-lucent.com, lberger@labn.net, loa.andersson@ericsson.com
  RFC5829          ||      A. Brown, G. Clemm, J. Reschke, Ed.         ||       albertcbrown@us.ibm.com, geoffrey.clemm@us.ibm.com, julian.reschke@greenbytes.de
  RFC5830          ||      V. Dolmatov, Ed.         ||       dol@cryptocom.ru
  RFC5831          ||      V. Dolmatov, Ed.         ||       dol@cryptocom.ru
  RFC5832          ||      V. Dolmatov, Ed.         ||       dol@cryptocom.ru
  RFC5833          ||      Y. Shi, Ed., D. Perkins, Ed., C. Elliott, Ed., Y. Zhang, Ed.         ||       rishyang@gmail.com, dperkins@dsperkins.com, chelliot@pobox.com, yzhang@fortinet.com
  RFC5834          ||      Y. Shi, Ed., D. Perkins, Ed., C. Elliott, Ed., Y. Zhang, Ed.         ||       rishyang@gmail.com, dperkins@dsperkins.com, chelliot@pobox.com, yzhang@fortinet.com
  RFC5835          ||      A. Morton, Ed., S. Van den Berghe, Ed.         ||       acmorton@att.com, steven.van_den_berghe@alcatel-lucent.com
  RFC5836          ||      Y. Ohba, Ed., Q. Wu, Ed., G. Zorn, Ed.         ||       oshihiro.ohba@toshiba.co.jp, sunseawq@huawei.com, gwz@net-zen.net
  RFC5837          ||      A. Atlas, Ed., R. Bonica, Ed., C. Pignataro, Ed., N. Shen, JR. Rivers         ||       alia.atlas@bt.com, rbonica@juniper.net, cpignata@cisco.com, naiming@cisco.com, jrrivers@yahoo.com
  RFC5838          ||      A. Lindem, Ed., S. Mirtorabi, A. Roy, M. Barnes, R. Aggarwal         ||       acee.lindem@ericsson.com, smirtora@cisco.com, akr@cisco.com, mjbarnes@cisco.com, rahul@juniper.net
  RFC5839          ||      A. Niemi, D. Willis, Ed.         ||       aki.niemi@nokia.com, dean.willis@softarmor.com
  RFC5840          ||      K. Grewal, G. Montenegro, M. Bhatia         ||       ken.grewal@intel.com, gabriel.montenegro@microsoft.com, manav.bhatia@alcatel-lucent.com
  RFC5841          ||      R. Hay, W. Turkal         ||       rhay@google.com, turkal@google.com
  RFC5842          ||      G. Clemm, J. Crawford, J. Reschke, Ed., J. Whitehead         ||       geoffrey.clemm@us.ibm.com, ccjason@us.ibm.com, julian.reschke@greenbytes.de, ejw@cse.ucsc.edu
  RFC5843          ||      A. Bryan         ||       anthonybryan@gmail.com
  RFC5844          ||      R. Wakikawa, S. Gundavelli         ||       ryuji@us.toyota-itc.com, sgundave@cisco.com
  RFC5845          ||      A. Muhanna, M. Khalil, S. Gundavelli, K. Leung         ||       ahmad.muhanna@ericsson.com, Mohamed.khalil@ericsson.com, sgundave@cisco.com, kleung@cisco.com
  RFC5846          ||      A. Muhanna, M. Khalil, S. Gundavelli, K. Chowdhury, P. Yegani         ||       ahmad.muhanna@ericsson.com, mohamed.khalil@ericsson.com, sgundave@cisco.com, kchowdhu@cisco.com, pyegani@juniper.net
  RFC5847          ||      V. Devarapalli, Ed., R. Koodli, Ed., H. Lim, N. Kant, S. Krishnan, J. Laganier         ||       vijay@wichorus.com, rkoodli@cisco.com, hlim@stoke.com, nishi@stoke.com, suresh.krishnan@ericsson.com, julienl@qualcomm.com
  RFC5848          ||      J. Kelsey, J. Callas, A. Clemm         ||       john.kelsey@nist.gov, jon@callas.org, alex@cisco.com
  RFC5849          ||      E. Hammer-Lahav, Ed.         ||       eran@hueniverse.com
  RFC5850          ||      R. Mahy, R. Sparks, J. Rosenberg, D. Petrie, A. Johnston, Ed.         ||       rohan@ekabal.com, rjsparks@nostrum.com, jdrosen@jdrosen.net, dpetrie@sipez.com, alan@sipstation.com
  RFC5851          ||      S. Ooghe, N. Voigt, M. Platnic, T. Haag, S. Wadhwa         ||       sven.ooghe@alcatel-lucent.com, norbert.voigt@nsn.com, mplatnic@gmail.com, haagt@telekom.de, swadhwa@juniper.net
  RFC5852          ||      D. Caviglia, D. Ceccarelli, D. Bramanti, D. Li, S. Bardalai         ||       diego.caviglia@ericsson.com, daniele.ceccarelli@ericsson.com, none, danli@huawei.com, sbardalai@gmail.com
  RFC5853          ||      J. Hautakorpi, Ed., G. Camarillo, R. Penfield, A. Hawrylyshen, M. Bhatia         ||       Jani.Hautakorpi@ericsson.com, Gonzalo.Camarillo@ericsson.com, bpenfield@acmepacket.com, alan.ietf@polyphase.ca, mbhatia@3clogic.com
  RFC5854          ||      A. Bryan, T. Tsujikawa, N. McNab, P. Poeml         ||       anthonybryan@gmail.com, tatsuhiro.t@gmail.com, neil@nabber.org, peter@poeml.de
  RFC5855          ||      J. Abley, T. Manderson         ||       joe.abley@icann.org, terry.manderson@icann.org
  RFC5856          ||      E. Ertekin, R. Jasani, C. Christou, C. Bormann         ||       ertekin_emre@bah.com, ro@breakcheck.com, christou_chris@bah.com, cabo@tzi.org
  RFC5857          ||      E. Ertekin, C. Christou, R. Jasani, T. Kivinen, C. Bormann         ||       ertekin_emre@bah.com, christou_chris@bah.com, ro@breakcheck.com, kivinen@iki.fi, cabo@tzi.org
  RFC5858          ||      E. Ertekin, C. Christou, C. Bormann         ||       ertekin_emre@bah.com, christou_chris@bah.com, cabo@tzi.org
  RFC5859          ||      R. Johnson         ||       raj@cisco.com
  RFC5860          ||      M. Vigoureux, Ed., D. Ward, Ed., M. Betts, Ed.         ||       martin.vigoureux@alcatel-lucent.com, dward@juniper.net, malcolm.betts@rogers.com
  RFC5861          ||      M. Nottingham         ||       mnot@yahoo-inc.com
  RFC5862          ||      S. Yasukawa, A. Farrel         ||       yasukawa.seisho@lab.ntt.co.jp, adrian@olddog.co.uk
  RFC5863          ||      T. Hansen, E. Siegel, P. Hallam-Baker, D. Crocker         ||       tony+dkimov@maillennium.att.com, dkim@esiegel.net, phillip@hallambaker.com, dcrocker@bbiw.net
  RFC5864          ||      R. Allbery         ||       rra@stanford.edu
  RFC5865          ||      F. Baker, J. Polk, M. Dolly         ||       fred@cisco.com, jmpolk@cisco.com, mdolly@att.com
  RFC5866          ||      D. Sun, Ed., P. McCann, H. Tschofenig, T. Tsou, A. Doria, G. Zorn, Ed.         ||       d.sun@alcatel-lucent.com, pete.mccann@motorola.com, Hannes.Tschofenig@gmx.net, tena@huawei.com, avri@ltu.se, gwz@net-zen.net
  RFC5867          ||      J. Martocci, Ed., P. De Mil, N. Riou, W. Vermeylen         ||       jerald.p.martocci@jci.com, pieter.demil@intec.ugent.be, nicolas.riou@fr.schneider-electric.com, wouter@vooruit.be
  RFC5868          ||      S. Sakane, K. Kamada, S. Zrelli, M. Ishiyama         ||       Shouichi.Sakane@jp.yokogawa.com, Ken-ichi.Kamada@jp.yokogawa.com, Saber.Zrelli@jp.yokogawa.com, masahiro@isl.rdc.toshiba.co.jp
  RFC5869          ||      H. Krawczyk, P. Eronen         ||       hugokraw@us.ibm.com, pe@iki.fi
  RFC5870          ||      A. Mayrhofer, C. Spanring         ||       alexander.mayrhofer@ipcom.at, christian@spanring.eu
  RFC5871          ||      J. Arkko, S. Bradner         ||       jari.arkko@piuha.net, sob@harvard.edu
  RFC5872          ||      J. Arkko, A. Yegin         ||       jari.arkko@piuha.net, alper.yegin@yegin.org
  RFC5873          ||      Y. Ohba, A. Yegin         ||       yoshihiro.ohba@toshiba.co.jp, alper.yegin@yegin.org
  RFC5874          ||      J. Rosenberg, J. Urpalainen         ||       jdrosen.net, jari.urpalainen@nokia.com
  RFC5875          ||      J. Urpalainen, D. Willis, Ed.         ||       jari.urpalainen@nokia.com, dean.willis@softarmor.com
  RFC5876          ||      J. Elwell         ||       john.elwell@siemens-enterprise.com
  RFC5877          ||      R. Housley         ||       housley@vigilsec.com
  RFC5878          ||      M. Brown, R. Housley         ||       mark@redphonesecurity.com, housley@vigilsec.com
  RFC5879          ||      T. Kivinen, D. McDonald         ||       kivinen@iki.fi, danmcd@opensolaris.org
  RFC5880          ||      D. Katz, D. Ward         ||       dkatz@juniper.net, dward@juniper.net
  RFC5881          ||      D. Katz, D. Ward         ||       dkatz@juniper.net, dward@juniper.net
  RFC5882          ||      D. Katz, D. Ward         ||       dkatz@juniper.net, dward@juniper.net
  RFC5883          ||      D. Katz, D. Ward         ||       dkatz@juniper.net, dward@juniper.net
  RFC5884          ||      R. Aggarwal, K. Kompella, T. Nadeau, G. Swallow         ||       rahul@juniper.net, kireeti@juniper.net, tom.nadeau@bt.com, swallow@cisco.com
  RFC5885          ||      T. Nadeau, Ed., C. Pignataro, Ed.         ||       tom.nadeau@bt.com, cpignata@cisco.com
  RFC5886          ||      JP. Vasseur, Ed., JL. Le Roux, Y. Ikejiri         ||       jpv@cisco.com, jeanlouis.leroux@orange-ftgroup.com, y.ikejiri@ntt.com
  RFC5887          ||      B. Carpenter, R. Atkinson, H. Flinck         ||       brian.e.carpenter@gmail.com, rja@extremenetworks.com, hannu.flinck@nsn.com
  RFC5888          ||      G. Camarillo, H. Schulzrinne         ||       Gonzalo.Camarillo@ericsson.com, schulzrinne@cs.columbia.edu
  RFC5889          ||      E. Baccelli, Ed., M. Townsley, Ed.         ||       Emmanuel.Baccelli@inria.fr, mark@townsley.net
  RFC5890          ||      J. Klensin         ||       john+ietf@jck.com
  RFC5891          ||      J. Klensin         ||       john+ietf@jck.com
  RFC5892          ||      P. Faltstrom, Ed.         ||       paf@cisco.com
  RFC5893          ||      H. Alvestrand, Ed., C. Karp         ||       harald@alvestrand.no, ck@nic.museum
  RFC5894          ||      J. Klensin         ||       john+ietf@jck.com
  RFC5895          ||      P. Resnick, P. Hoffman         ||       presnick@qti.qualcomm.com, paul.hoffman@vpnc.org
  RFC5896          ||      L. Hornquist Astrand, S. Hartman         ||       lha@apple.com, hartmans-ietf@mit.edu
  RFC5897          ||      J. Rosenberg         ||       jdrosen@jdrosen.net
  RFC5898          ||      F. Andreasen, G. Camarillo, D. Oran, D. Wing         ||       fandreas@cisco.com, Gonzalo.Camarillo@ericsson.com, oran@cisco.com, dwing-ietf@fuggles.com
  RFC5901          ||      P. Cain, D. Jevans         ||       pcain@coopercain.com, dave.jevans@antiphishing.org
  RFC5902          ||      D. Thaler, L. Zhang, G. Lebovitz         ||       dthaler@microsoft.com, lixia@cs.ucla.edu, gregory.ietf@gmail.com, iab@iab.org
  RFC5903          ||      D. Fu, J. Solinas         ||       defu@orion.ncsc.mil, jasolin@orion.ncsc.mil
  RFC5904          ||      G. Zorn         ||       gwz@net-zen.net
  RFC5905          ||      D. Mills, J. Martin, Ed., J. Burbank, W. Kasch         ||       mills@udel.edu, jrmii@isc.org, jack.burbank@jhuapl.edu, william.kasch@jhuapl.edu
  RFC5906          ||      B. Haberman, Ed., D. Mills         ||       brian@innovationslab.net, mills@udel.edu
  RFC5907          ||      H. Gerstung, C. Elliott, B. Haberman, Ed.         ||       heiko.gerstung@meinberg.de, chelliot@pobox.com, brian@innovationslab.net
  RFC5908          ||      R. Gayraud, B. Lourdelet         ||       richard.gayraud@free.fr, blourdel@cisco.com
  RFC5909          ||      J-M. Combes, S. Krishnan, G. Daley         ||       jeanmichel.combes@orange-ftgroup.com, Suresh.Krishnan@ericsson.com, hoskuld@hotmail.com
  RFC5910          ||      J. Gould, S. Hollenbeck         ||       jgould@verisign.com, shollenbeck@verisign.com
  RFC5911          ||      P. Hoffman, J. Schaad         ||       paul.hoffman@vpnc.org, jimsch@exmsft.com
  RFC5912          ||      P. Hoffman, J. Schaad         ||       paul.hoffman@vpnc.org, jimsch@exmsft.com
  RFC5913          ||      S. Turner, S. Chokhani         ||       turners@ieca.com, SChokhani@cygnacom.com
  RFC5914          ||      R. Housley, S. Ashmore, C. Wallace         ||       housley@vigilsec.com, srashmo@radium.ncsc.mil, cwallace@cygnacom.com
  RFC5915          ||      S. Turner, D. Brown         ||       turners@ieca.com, dbrown@certicom.com
  RFC5916          ||      S. Turner         ||       turners@ieca.com
  RFC5917          ||      S. Turner         ||       turners@ieca.com
  RFC5918          ||      R. Asati, I. Minei, B. Thomas         ||       rajiva@cisco.com, ina@juniper.net, bobthomas@alum.mit.edu
  RFC5919          ||      R. Asati, P. Mohapatra, E. Chen, B. Thomas         ||       rajiva@cisco.com, pmohapat@cisco.com, chenying220@huawei.com, bobthomas@alum.mit.edu
  RFC5920          ||      L. Fang, Ed.         ||       lufang@cisco.com
  RFC5921          ||      M. Bocci, Ed., S. Bryant, Ed., D. Frost, Ed., L. Levrau, L. Berger         ||       matthew.bocci@alcatel-lucent.com, stbryant@cisco.com, danfrost@cisco.com, lieven.levrau@alcatel-lucent.com, lberger@labn.net
  RFC5922          ||      V. Gurbani, S. Lawrence, A. Jeffrey         ||       vkg@alcatel-lucent.com, scott-ietf@skrb.org, ajeffrey@alcatel-lucent.com
  RFC5923          ||      V. Gurbani, Ed., R. Mahy, B. Tate         ||       vkg@alcatel-lucent.com, rohan@ekabal.com, brett@broadsoft.com
  RFC5924          ||      S. Lawrence, V. Gurbani         ||       scott-ietf@skrb.org, vkg@bell-labs.com
  RFC5925          ||      J. Touch, A. Mankin, R. Bonica         ||       touch@isi.edu, mankin@psg.com, rbonica@juniper.net
  RFC5926          ||      G. Lebovitz, E. Rescorla         ||       gregory.ietf@gmail.com, ekr@rtfm.com
  RFC5927          ||      F. Gont         ||       fernando@gont.com.ar
  RFC5928          ||      M. Petit-Huguenin         ||       petithug@acm.org
  RFC5929          ||      J. Altman, N. Williams, L. Zhu         ||       jaltman@secure-endpoints.com, Nicolas.Williams@oracle.com, larry.zhu@microsoft.com
  RFC5930          ||      S. Shen, Y. Mao, NSS. Murthy         ||       shenshuo@cnnic.cn, yumao9@gmail.com, ssmurthy.nittala@freescale.com
  RFC5931          ||      D. Harkins, G. Zorn         ||       dharkins@arubanetworks.com, gwz@net-zen.net
  RFC5932          ||      A. Kato, M. Kanda, S. Kanno         ||       kato.akihiro@po.ntts.co.jp, kanda.masayuki@lab.ntt.co.jp, kanno.satoru@po.ntts.co.jp
  RFC5933          ||      V. Dolmatov, Ed., A. Chuprina, I. Ustinov         ||       dol@cryptocom.ru, ran@cryptocom.ru, igus@cryptocom.ru
  RFC5934          ||      R. Housley, S. Ashmore, C. Wallace         ||       housley@vigilsec.com, srashmo@radium.ncsc.mil, cwallace@cygnacom.com
  RFC5935          ||      M. Ellison, B. Natale         ||       ietf@ellisonsoftware.com, rnatale@mitre.org
  RFC5936          ||      E. Lewis, A. Hoenes, Ed.         ||       ed.lewis@neustar.biz, ah@TR-Sys.de
  RFC5937          ||      S. Ashmore, C. Wallace         ||       srashmo@radium.ncsc.mil, cwallace@cygnacom.com
  RFC5938          ||      A. Morton, M. Chiba         ||       acmorton@att.com, mchiba@cisco.com
  RFC5939          ||      F. Andreasen         ||       fandreas@cisco.com
  RFC5940          ||      S. Turner, R. Housley         ||       turners@ieca.com, housley@vigilsec.com
  RFC5941          ||      D. M'Raihi, S. Boeyen, M. Grandcolas, S. Bajaj         ||       davidietf@gmail.com, sharon.boeyen@entrust.com, michael.grandcolas@hotmail.com, sbajaj@verisign.com
  RFC5942          ||      H. Singh, W. Beebee, E. Nordmark         ||       shemant@cisco.com, wbeebee@cisco.com, erik.nordmark@oracle.com
  RFC5943          ||      B. Haberman, Ed.         ||       brian@innovationslab.net
  RFC5944          ||      C. Perkins, Ed.         ||       charliep@computer.org
  RFC5945          ||      F. Le Faucheur, J. Manner, D. Wing, A. Guillou         ||       flefauch@cisco.com, jukka.manner@tkk.fi, dwing-ietf@fuggles.com, allan.guillou@sfr.com
  RFC5946          ||      F. Le Faucheur, J. Manner, A. Narayanan, A. Guillou, H. Malik         ||       flefauch@cisco.com, jukka.manner@tkk.fi, ashokn@cisco.com, allan.guillou@sfr.com, Hemant.Malik@airtel.in
  RFC5947          ||      J. Elwell, H. Kaplan         ||       john.elwell@siemens-enterprise.com, hkaplan@acmepacket.com
  RFC5948          ||      S. Madanapalli, S. Park, S. Chakrabarti, G. Montenegro         ||       smadanapalli@gmail.com, soohong.park@samsung.com, samitac@ipinfusion.com, gabriel.montenegro@microsoft.com
  RFC5949          ||      H. Yokota, K. Chowdhury, R. Koodli, B. Patil, F. Xia         ||       yokota@kddilabs.jp, kchowdhu@cisco.com, rkoodli@cisco.com, basavaraj.patil@nokia.com, xiayangsong@huawei.com
  RFC5950          ||      S. Mansfield, Ed., E. Gray, Ed., K. Lam, Ed.         ||       scott.mansfield@ericsson.com, eric.gray@ericsson.com, Kam.Lam@alcatel-lucent.com
  RFC5951          ||      K. Lam, S. Mansfield, E. Gray         ||       Kam.Lam@Alcatel-Lucent.com, Scott.Mansfield@Ericsson.com, Kam.Lam@Alcatel-Lucent.com
  RFC5952          ||      S. Kawamura, M. Kawashima         ||       kawamucho@mesh.ad.jp, kawashimam@vx.jp.nec.com
  RFC5953          ||      W. Hardaker         ||       ietf@hardakers.net
  RFC5954          ||      V. Gurbani, Ed., B. Carpenter, Ed., B. Tate, Ed.         ||       vkg@bell-labs.com, brian.e.carpenter@gmail.com, brett@broadsoft.com
  RFC5955          ||      A. Santoni         ||       adriano.santoni@actalis.it
  RFC5956          ||      A. Begen         ||       abegen@cisco.com
  RFC5957          ||      D. Karp         ||       dkarp@zimbra.com
  RFC5958          ||      S. Turner         ||       turners@ieca.com
  RFC5959          ||      S. Turner         ||       turners@ieca.com
  RFC5960          ||      D. Frost, Ed., S. Bryant, Ed., M. Bocci, Ed.         ||       danfrost@cisco.com, stbryant@cisco.com, matthew.bocci@alcatel-lucent.com
  RFC5961          ||      A. Ramaiah, R. Stewart, M. Dalal         ||       ananth@cisco.com, randall@lakerest.net, mdalal@cisco.com
  RFC5962          ||      H. Schulzrinne, V. Singh, H. Tschofenig, M. Thomson         ||       hgs@cs.columbia.edu, vs2140@cs.columbia.edu, Hannes.Tschofenig@gmx.net, martin.thomson@andrew.com
  RFC5963          ||      R. Gagliano         ||       rogaglia@cisco.com
  RFC5964          ||      J. Winterbottom, M. Thomson         ||       james.winterbottom@andrew.com, martin.thomson@andrew.com
  RFC5965          ||      Y. Shafranovich, J. Levine, M. Kucherawy         ||       ietf@shaftek.org, standards@taugh.com, msk@cloudmark.com
  RFC5966          ||      R. Bellis         ||       ray.bellis@nominet.org.uk
  RFC5967          ||      S. Turner         ||       turners@ieca.com
  RFC5968          ||      J. Ott, C. Perkins         ||       jo@netlab.tkk.fi, csp@csperkins.org
  RFC5969          ||      W. Townsley, O. Troan         ||       mark@townsley.net, ot@cisco.com
  RFC5970          ||      T. Huth, J. Freimann, V. Zimmer, D. Thaler         ||       thuth@de.ibm.com, jfrei@de.ibm.com, vincent.zimmer@intel.com, dthaler@microsoft.com
  RFC5971          ||      H. Schulzrinne, R. Hancock         ||       hgs+nsis@cs.columbia.edu, robert.hancock@roke.co.uk
  RFC5972          ||      T. Tsenov, H. Tschofenig, X. Fu, Ed., C. Aoun, E. Davies         ||       tseno.tsenov@mytum.de, Hannes.Tschofenig@nsn.com, fu@cs.uni-goettingen.de, cedaoun@yahoo.fr, elwynd@dial.pipex.com
  RFC5973          ||      M. Stiemerling, H. Tschofenig, C. Aoun, E. Davies         ||       Martin.Stiemerling@neclab.eu, Hannes.Tschofenig@nsn.com, cedaoun@yahoo.fr, elwynd@dial.pipex.com
  RFC5974          ||      J. Manner, G. Karagiannis, A. McDonald         ||       jukka.manner@tkk.fi, karagian@cs.utwente.nl, andrew.mcdonald@roke.co.uk
  RFC5975          ||      G. Ash, Ed., A. Bader, Ed., C. Kappler, Ed., D. Oran, Ed.         ||       gash5107@yahoo.com, Attila.Bader@ericsson.com, cornelia.kappler@cktecc.de, oran@cisco.com
  RFC5976          ||      G. Ash, A. Morton, M. Dolly, P. Tarapore, C. Dvorak, Y. El Mghazli         ||       gash5107@yahoo.com, acmorton@att.com, mdolly@att.com, tarapore@att.com, cdvorak@att.com, yacine.el_mghazli@alcatel.fr
  RFC5977          ||      A. Bader, L. Westberg, G. Karagiannis, C. Kappler, T. Phelan         ||       Attila.Bader@ericsson.com, Lars.Westberg@ericsson.com, g.karagiannis@ewi.utwente.nl, cornelia.kappler@cktecc.de, tphelan@sonusnet.com
  RFC5978          ||      J. Manner, R. Bless, J. Loughney, E. Davies, Ed.         ||       jukka.manner@tkk.fi, bless@kit.edu, john.loughney@nokia.com, elwynd@folly.org.uk
  RFC5979          ||      C. Shen, H. Schulzrinne, S. Lee, J. Bang         ||       charles@cs.columbia.edu, hgs@cs.columbia.edu, sung1.lee@samsung.com, jh0278.bang@samsung.com
  RFC5980          ||      T. Sanda, Ed., X. Fu, S. Jeong, J. Manner, H. Tschofenig         ||       sanda.takako@jp.panasonic.com, fu@cs.uni-goettingen.de, shjeong@hufs.ac.kr, jukka.manner@tkk.fi, Hannes.Tschofenig@nsn.com
  RFC5981          ||      J. Manner, M. Stiemerling, H. Tschofenig, R. Bless, Ed.         ||       jukka.manner@tkk.fi, martin.stiemerling@neclab.eu, Hannes.Tschofenig@gmx.net, roland.bless@kit.edu
  RFC5982          ||      A. Kobayashi, Ed., B. Claise, Ed.         ||       akoba@nttv6.net, bclaise@cisco.com
  RFC5983          ||      R. Gellens         ||       rg+ietf@qualcomm.com
  RFC5984          ||      K-M. Moller         ||       kalle@tankesaft.se
  RFC5985          ||      M. Barnes, Ed.         ||       mary.ietf.barnes@gmail.com
  RFC5986          ||      M. Thomson, J. Winterbottom         ||       martin.thomson@andrew.com, james.winterbottom@andrew.com
  RFC5987          ||      J. Reschke         ||       julian.reschke@greenbytes.de
  RFC5988          ||      M. Nottingham         ||       mnot@mnot.net
  RFC5989          ||      A.B. Roach         ||       adam@nostrum.com
  RFC5990          ||      J. Randall, B. Kaliski, J. Brainard, S. Turner         ||       jdrandall@comcast.net, kaliski_burt@emc.com, jbrainard@rsa.com, turners@ieca.com
  RFC5991          ||      D. Thaler, S. Krishnan, J. Hoagland         ||       dthaler@microsoft.com, suresh.krishnan@ericsson.com, Jim_Hoagland@symantec.com
  RFC5992          ||      S. Sharikov, D. Miloshevic, J. Klensin         ||       s.shar@regtime.net, dmiloshevic@afilias.info, john-ietf@jck.com
  RFC5993          ||      X. Duan, S. Wang, M. Westerlund, K. Hellwig, I. Johansson         ||       duanxiaodong@chinamobile.com, wangshuaiyu@chinamobile.com, magnus.westerlund@ericsson.com, karl.hellwig@ericsson.com, ingemar.s.johansson@ericsson.com
  RFC5994          ||      S. Bryant, Ed., M. Morrow, G. Swallow, R. Cherukuri, T. Nadeau, N. Harrison, B. Niven-Jenkins         ||       stbryant@cisco.com, mmorrow@cisco.com, swallow@cisco.com, cherukuri@juniper.net, thomas.nadeau@huawei.com, neil.2.harrison@bt.com, ben@niven-jenkins.co.uk
  RFC5995          ||      J. Reschke         ||       julian.reschke@greenbytes.de
  RFC5996          ||      C. Kaufman, P. Hoffman, Y. Nir, P. Eronen         ||       charliek@microsoft.com, paul.hoffman@vpnc.org, ynir@checkpoint.com, pe@iki.fi
  RFC5997          ||      A. DeKok         ||       aland@freeradius.org
  RFC5998          ||      P. Eronen, H. Tschofenig, Y. Sheffer         ||       pe@iki.fi, Hannes.Tschofenig@gmx.net, yaronf.ietf@gmail.com
  RFC6001          ||      D. Papadimitriou, M. Vigoureux, K. Shiomoto, D. Brungard, JL. Le Roux         ||       dimitri.papadimitriou@alcatel-lucent.com, martin.vigoureux@alcatel-lucent.fr, shiomoto.kohei@lab.ntt.co.jp, dbrungard@att.com, jean-louis.leroux@rd.francetelecom.com
  RFC6002          ||      L. Berger, D. Fedyk         ||       lberger@labn.net, donald.fedyk@alcatel-lucent.com
  RFC6003          ||      D. Papadimitriou         ||       dimitri.papadimitriou@alcatel-lucent.be
  RFC6004          ||      L. Berger, D. Fedyk         ||       lberger@labn.net, donald.fedyk@alcatel-lucent.com
  RFC6005          ||      L. Berger, D. Fedyk         ||       lberger@labn.net, donald.fedyk@alcatel-lucent.com
  RFC6006          ||      Q. Zhao, Ed., D. King, Ed., F. Verhaeghe, T. Takeda, Z. Ali, J. Meuric         ||       qzhao@huawei.com, daniel@olddog.co.uk, fabien.verhaeghe@gmail.com, takeda.tomonori@lab.ntt.co.jp, zali@cisco.com, julien.meuric@orange-ftgroup.com
  RFC6007          ||      I. Nishioka, D. King         ||       i-nishioka@cb.jp.nec.com, daniel@olddog.co.uk
  RFC6008          ||      M. Kucherawy         ||       msk@cloudmark.com
  RFC6009          ||      N. Freed         ||       ned.freed@mrochek.com
  RFC6010          ||      R. Housley, S. Ashmore, C. Wallace         ||       housley@vigilsec.com, srashmo@radium.ncsc.mil, cwallace@cygnacom.com
  RFC6011          ||      S. Lawrence, Ed., J. Elwell         ||       scott-ietf@skrb.org, john.elwell@siemens-enterprise.com
  RFC6012          ||      J. Salowey, T. Petch, R. Gerhards, H. Feng         ||       jsalowey@cisco.com, tomSecurity@network-engineer.co.uk, rgerhards@adiscon.com, fhyfeng@gmail.com
  RFC6013          ||      W. Simpson         ||       William.Allen.Simpson@Gmail.com
  RFC6014          ||      P. Hoffman         ||       paul.hoffman@vpnc.org
  RFC6015          ||      A. Begen         ||       abegen@cisco.com
  RFC6016          ||      B. Davie, F. Le Faucheur, A. Narayanan         ||       bsd@cisco.com, flefauch@cisco.com, ashokn@cisco.com
  RFC6017          ||      K. Meadors, Ed.         ||       kyle@drummondgroup.com
  RFC6018          ||      F. Baker, W. Harrop, G. Armitage         ||       fred@cisco.com, wazz@bud.cc.swin.edu.au, garmitage@swin.edu.au
  RFC6019          ||      R. Housley         ||       housley@vigilsec.com
  RFC6020          ||      M. Bjorklund, Ed.         ||       mbj@tail-f.com
  RFC6021          ||      J. Schoenwaelder, Ed.         ||       j.schoenwaelder@jacobs-university.de
  RFC6022          ||      M. Scott, M. Bjorklund         ||       mark.scott@ericsson.com, mbj@tail-f.com
  RFC6023          ||      Y. Nir, H. Tschofenig, H. Deng, R. Singh         ||       ynir@checkpoint.com, Hannes.Tschofenig@gmx.net, denghui02@gmail.com, rsj@cisco.com
  RFC6024          ||      R. Reddy, C. Wallace         ||       r.reddy@radium.ncsc.mil, cwallace@cygnacom.com
  RFC6025          ||      C. Wallace, C. Gardiner         ||       cwallace@cygnacom.com, gardiner@bbn.com
  RFC6026          ||      R. Sparks, T. Zourzouvillys         ||       RjS@nostrum.com, theo@crazygreek.co.uk
  RFC6027          ||      Y. Nir         ||       ynir@checkpoint.com
  RFC6028          ||      G. Camarillo, A. Keranen         ||       Gonzalo.Camarillo@ericsson.com, Ari.Keranen@ericsson.com
  RFC6029          ||      I. Rimac, V. Hilt, M. Tomsu, V. Gurbani, E. Marocco         ||       rimac@bell-labs.com, volkerh@bell-labs.com, marco.tomsu@alcatel-lucent.com, vkg@bell-labs.com, enrico.marocco@telecomitalia.it
  RFC6030          ||      P. Hoyer, M. Pei, S. Machani         ||       phoyer@actividentity.com, mpei@verisign.com, smachani@diversinet.com
  RFC6031          ||      S. Turner, R. Housley         ||       turners@ieca.com, housley@vigilsec.com
  RFC6032          ||      S. Turner, R. Housley         ||       turners@ieca.com, housley@vigilsec.com
  RFC6033          ||      S. Turner         ||       turners@ieca.com
  RFC6034          ||      D. Thaler         ||       dthaler@microsoft.com
  RFC6035          ||      A. Pendleton, A. Clark, A. Johnston, H. Sinnreich         ||       aspen@telchemy.com, alan.d.clark@telchemy.com, alan.b.johnston@gmail.com, henry.sinnreich@gmail.com
  RFC6036          ||      B. Carpenter, S. Jiang         ||       brian.e.carpenter@gmail.com, shengjiang@huawei.com
  RFC6037          ||      E. Rosen, Ed., Y. Cai, Ed., IJ. Wijnands         ||       erosen@cisco.com, ycai@cisco.com, ice@cisco.com
  RFC6038          ||      A. Morton, L. Ciavattone         ||       acmorton@att.com, lencia@att.com
  RFC6039          ||      V. Manral, M. Bhatia, J. Jaeggli, R. White         ||       vishwas@ipinfusion.com, manav.bhatia@alcatel-lucent.com, joel.jaeggli@nokia.com, riw@cisco.com
  RFC6040          ||      B. Briscoe         ||       bob.briscoe@bt.com
  RFC6041          ||      A. Crouch, H. Khosravi, A. Doria, Ed., X. Wang, K. Ogawa         ||       alan.crouch@intel.com, hormuzd.m.khosravi@intel.com, avri@acm.org, carly.wang@huawei.com, ogawa.kentaro@lab.ntt.co.jp
  RFC6042          ||      A. Keromytis         ||       angelos@cs.columbia.edu
  RFC6043          ||      J. Mattsson, T. Tian         ||       john.mattsson@ericsson.com, tian.tian1@zte.com.cn
  RFC6044          ||      M. Mohali         ||       marianne.mohali@orange-ftgroup.com
  RFC6045          ||      K. Moriarty         ||       Moriarty_Kathleen@EMC.com
  RFC6046          ||      K. Moriarty, B. Trammell         ||       Moriarty_Kathleen@EMC.com, trammell@tik.ee.ethz.ch
  RFC6047          ||      A. Melnikov, Ed.         ||       Alexey.Melnikov@isode.com
  RFC6048          ||      J. Elie         ||       julien@trigofacile.com
  RFC6049          ||      A. Morton, E. Stephan         ||       acmorton@att.com, emile.stephan@orange-ftgroup.com
  RFC6050          ||      K. Drage         ||       drage@alcatel-lucent.com
  RFC6051          ||      C. Perkins, T. Schierl         ||       csp@csperkins.org, ts@thomas-schierl.de
  RFC6052          ||      C. Bao, C. Huitema, M. Bagnulo, M. Boucadair, X. Li         ||       congxiao@cernet.edu.cn, huitema@microsoft.com, marcelo@it.uc3m.es, mohamed.boucadair@orange-ftgroup.com, xing@cernet.edu.cn
  RFC6053          ||      E. Haleplidis, K. Ogawa, W. Wang, J. Hadi Salim         ||       ehalep@ece.upatras.gr, ogawa.kentaro@lab.ntt.co.jp, wmwang@mail.zjgsu.edu.cn, hadi@mojatatu.com
  RFC6054          ||      D. McGrew, B. Weis         ||       mcgrew@cisco.com, bew@cisco.com
  RFC6055          ||      D. Thaler, J. Klensin, S. Cheshire         ||       dthaler@microsoft.com, john+ietf@jck.com, cheshire@apple.com
  RFC6056          ||      M. Larsen, F. Gont         ||       michael.larsen@tieto.com, fernando@gont.com.ar
  RFC6057          ||      C. Bastian, T. Klieber, J. Livingood, J. Mills, R. Woundy         ||       chris_bastian@cable.comcast.com, tom_klieber@cable.comcast.com, jason_livingood@cable.comcast.com, jim_mills@cable.comcast.com, richard_woundy@cable.comcast.com
  RFC6058          ||      M. Liebsch, Ed., A. Muhanna, O. Blume         ||       marco.liebsch@neclab.eu, ahmad.muhanna@ericsson.com, oliver.blume@alcatel-lucent.de
  RFC6059          ||      S. Krishnan, G. Daley         ||       suresh.krishnan@ericsson.com, hoskuld@hotmail.com
  RFC6060          ||      D. Fedyk, H. Shah, N. Bitar, A. Takacs         ||       donald.fedyk@alcatel-lucent.com, hshah@ciena.com, nabil.n.bitar@verizon.com, attila.takacs@ericsson.com
  RFC6061          ||      B. Rosen         ||       br@brianrosen.net
  RFC6062          ||      S. Perreault, Ed., J. Rosenberg         ||       simon.perreault@viagenie.ca, jdrosen@jdrosen.net
  RFC6063          ||      A. Doherty, M. Pei, S. Machani, M. Nystrom         ||       andrea.doherty@rsa.com, mpei@verisign.com, smachani@diversinet.com, mnystrom@microsoft.com
  RFC6064          ||      M. Westerlund, P. Frojdh         ||       magnus.westerlund@ericsson.com, per.frojdh@ericsson.com
  RFC6065          ||      K. Narayan, D. Nelson, R. Presuhn, Ed.         ||       kaushik_narayan@yahoo.com, d.b.nelson@comcast.net, randy_presuhn@mindspring.com
  RFC6066          ||      D. Eastlake 3rd         ||       d3e3e3@gmail.com
  RFC6067          ||      M. Davis, A. Phillips, Y. Umaoka         ||       mark@macchiato.com, addison@lab126.com, yoshito_umaoka@us.ibm.com
  RFC6068          ||      M. Duerst, L. Masinter, J. Zawinski         ||       duerst@it.aoyama.ac.jp, LMM@acm.org, jwz@jwz.org
  RFC6069          ||      A. Zimmermann, A. Hannemann         ||       zimmermann@cs.rwth-aachen.de, hannemann@nets.rwth-aachen.de
  RFC6070          ||      S. Josefsson         ||       simon@josefsson.org
  RFC6071          ||      S. Frankel, S. Krishnan         ||       sheila.frankel@nist.gov, suresh.krishnan@ericsson.com
  RFC6072          ||      C. Jennings, J. Fischl, Ed.         ||       fluffy@cisco.com, jason.fischl@skype.net
  RFC6073          ||      L. Martini, C. Metz, T. Nadeau, M. Bocci, M. Aissaoui         ||       lmartini@cisco.com, chmetz@cisco.com, tnadeau@lucidvision.com, matthew.bocci@alcatel-lucent.co.uk, mustapha.aissaoui@alcatel-lucent.com
  RFC6074          ||      E. Rosen, B. Davie, V. Radoaca, W. Luo         ||       erosen@cisco.com, bsd@cisco.com, vasile.radoaca@alcatel-lucent.com, luo@weiluo.net
  RFC6075          ||      D. Cridland         ||       dave.cridland@isode.com
  RFC6076          ||      D. Malas, A. Morton         ||       d.malas@cablelabs.com, acmorton@att.com
  RFC6077          ||      D. Papadimitriou, Ed., M. Welzl, M. Scharf, B. Briscoe         ||       dimitri.papadimitriou@alcatel-lucent.be, michawe@ifi.uio.no, michael.scharf@googlemail.com, bob.briscoe@bt.com
  RFC6078          ||      G. Camarillo, J. Melen         ||       Gonzalo.Camarillo@ericsson.com, Jan.Melen@ericsson.com
  RFC6079          ||      G. Camarillo, P. Nikander, J. Hautakorpi, A. Keranen, A. Johnston         ||       Gonzalo.Camarillo@ericsson.com, Pekka.Nikander@ericsson.com, Jani.Hautakorpi@ericsson.com, Ari.Keranen@ericsson.com, alan.b.johnston@gmail.com
  RFC6080          ||      D. Petrie, S. Channabasappa, Ed.         ||       dan.ietf@SIPez.com, sumanth@cablelabs.com
  RFC6081          ||      D. Thaler         ||       dthaler@microsoft.com
  RFC6082          ||      K. Whistler, G. Adams, M. Duerst, R. Presuhn, Ed., J. Klensin         ||       kenw@sybase.com, glenn@skynav.com, duerst@it.aoyama.ac.jp, randy_presuhn@mindspring.com, john+ietf@jck.com
  RFC6083          ||      M. Tuexen, R. Seggelmann, E. Rescorla         ||       tuexen@fh-muenster.de, seggelmann@fh-muenster.de, ekr@networkresonance.com
  RFC6084          ||      X. Fu, C. Dickmann, J. Crowcroft         ||       fu@cs.uni-goettingen.de, mail@christian-dickmann.de, jon.crowcroft@cl.cam.ac.uk
  RFC6085          ||      S. Gundavelli, M. Townsley, O. Troan, W. Dec         ||       sgundave@cisco.com, townsley@cisco.com, ot@cisco.com, wdec@cisco.com
  RFC6086          ||      C. Holmberg, E. Burger, H. Kaplan         ||       christer.holmberg@ericsson.com, eburger@standardstrack.com, hkaplan@acmepacket.com
  RFC6087          ||      A. Bierman         ||       andy@yumaworks.com
  RFC6088          ||      G. Tsirtsis, G. Giarreta, H. Soliman, N. Montavont         ||       tsirtsis@qualcomm.com, gerardog@qualcomm.com, hesham@elevatemobile.com, nicolas.montavont@telecom-bretagne.eu
  RFC6089          ||      G. Tsirtsis, H. Soliman, N. Montavont, G. Giaretta, K. Kuladinithi         ||       tsirtsis@qualcomm.com, hesham@elevatemobile.com, nicolas.montavont@telecom-bretagne.eu, gerardog@qualcomm.com, koo@comnets.uni-bremen.de
  RFC6090          ||      D. McGrew, K. Igoe, M. Salter         ||       mcgrew@cisco.com, kmigoe@nsa.gov, msalter@restarea.ncsc.mil
  RFC6091          ||      N. Mavrogiannopoulos, D. Gillmor         ||       nikos.mavrogiannopoulos@esat.kuleuven.be, dkg@fifthhorseman.net
  RFC6092          ||      J. Woodyatt, Ed.         ||       jhw@apple.com
  RFC6093          ||      F. Gont, A. Yourtchenko         ||       fernando@gont.com.ar, ayourtch@cisco.com
  RFC6094          ||      M. Bhatia, V. Manral         ||       manav.bhatia@alcatel-lucent.com, vishwas@ipinfusion.com
  RFC6095          ||      B. Linowski, M. Ersue, S. Kuryla         ||       bernd.linowski.ext@nsn.com, mehmet.ersue@nsn.com, s.kuryla@gmail.com
  RFC6096          ||      M. Tuexen, R. Stewart         ||       tuexen@fh-muenster.de, randall@lakerest.net
  RFC6097          ||      J. Korhonen, V. Devarapalli         ||       jouni.nospam@gmail.com, dvijay@gmail.com
  RFC6098          ||      H. Deng, H. Levkowetz, V. Devarapalli, S. Gundavelli, B. Haley         ||       denghui02@gmail.com, henrik@levkowetz.com, dvijay@gmail.com, sgundave@cisco.com, brian.haley@hp.com
  RFC6101          ||      A. Freier, P. Karlton, P. Kocher         ||       nikos.mavrogiannopoulos@esat.kuleuven.be
  RFC6104          ||      T. Chown, S. Venaas         ||       tjc@ecs.soton.ac.uk, stig@cisco.com
  RFC6105          ||      E. Levy-Abegnoli, G. Van de Velde, C. Popoviciu, J. Mohacsi         ||       elevyabe@cisco.com, gunter@cisco.com, chip@technodyne.com, mohacsi@niif.hu
  RFC6106          ||      J. Jeong, S. Park, L. Beloeil, S. Madanapalli         ||       pjeong@brocade.com, soohong.park@samsung.com, luc.beloeil@orange-ftgroup.com, smadanapalli@gmail.com
  RFC6107          ||      K. Shiomoto, Ed., A. Farrel, Ed.         ||       shiomoto.kohei@lab.ntt.co.jp, adrian@olddog.co.uk
  RFC6108          ||      C. Chung, A. Kasyanov, J. Livingood, N. Mody, B. Van Lieu         ||       chae_chung@cable.comcast.com, alexander_kasyanov@cable.comcast.com, jason_livingood@cable.comcast.com, nirmal_mody@cable.comcast.com, brian@vanlieu.net
  RFC6109          ||      C. Petrucci, F. Gennai, A. Shahin, A. Vinciarelli         ||       petrucci@digitpa.gov.it, francesco.gennai@isti.cnr.it, alba.shahin@isti.cnr.it, alessandro.vinciarelli@gmail.com
  RFC6110          ||      L. Lhotka, Ed.         ||       ladislav@lhotka.name
  RFC6111          ||      L. Zhu         ||       lzhu@microsoft.com
  RFC6112          ||      L. Zhu, P. Leach, S. Hartman         ||       larry.zhu@microsoft.com, paulle@microsoft.com, hartmans-ietf@mit.edu
  RFC6113          ||      S. Hartman, L. Zhu         ||       hartmans-ietf@mit.edu, larry.zhu@microsoft.com
  RFC6114          ||      M. Katagi, S. Moriai         ||       Masanobu.Katagi@jp.sony.com, clefia-q@jp.sony.com
  RFC6115          ||      T. Li, Ed.         ||       tony.li@tony.li
  RFC6116          ||      S. Bradner, L. Conroy, K. Fujiwara         ||       sob@harvard.edu, lconroy@insensate.co.uk, fujiwara@jprs.co.jp
  RFC6117          ||      B. Hoeneisen, A. Mayrhofer, J. Livingood         ||       bernie@ietf.hoeneisen.ch, alexander.mayrhofer@enum.at, jason_livingood@cable.comcast.com
  RFC6118          ||      B. Hoeneisen, A. Mayrhofer         ||       bernie@ietf.hoeneisen.ch, alexander.mayrhofer@enum.at
  RFC6119          ||      J. Harrison, J. Berger, M. Bartlett         ||       jon.harrison@metaswitch.com, jon.berger@metaswitch.com, mike.bartlett@metaswitch.com
  RFC6120          ||      P. Saint-Andre         ||       ietf@stpeter.im
  RFC6121          ||      P. Saint-Andre         ||       ietf@stpeter.im
  RFC6122          ||      P. Saint-Andre         ||       ietf@stpeter.im
  RFC6123          ||      A. Farrel         ||       adrian@olddog.co.uk
  RFC6124          ||      Y. Sheffer, G. Zorn, H. Tschofenig, S. Fluhrer         ||       yaronf.ietf@gmail.com, gwz@net-zen.net, Hannes.Tschofenig@gmx.net, sfluhrer@cisco.com
  RFC6125          ||      P. Saint-Andre, J. Hodges         ||       ietf@stpeter.im, Jeff.Hodges@PayPal.com
  RFC6126          ||      J. Chroboczek         ||       jch@pps.jussieu.fr
  RFC6127          ||      J. Arkko, M. Townsley         ||       jari.arkko@piuha.net, townsley@cisco.com
  RFC6128          ||      A. Begen         ||       abegen@cisco.com
  RFC6129          ||      L. Romary, S. Lundberg         ||       laurent.romary@inria.fr, slu@kb.dk
  RFC6130          ||      T. Clausen, C. Dearlove, J. Dean         ||       T.Clausen@computer.org, chris.dearlove@baesystems.com, jdean@itd.nrl.navy.mil
  RFC6131          ||      R. George, B. Leiba         ||       robinsgv@gmail.com, barryleiba@computer.org
  RFC6132          ||      R. George, B. Leiba         ||       robinsgv@gmail.com, barryleiba@computer.org
  RFC6133          ||      R. George, B. Leiba, A. Melnikov         ||       robinsgv@gmail.com, barryleiba@computer.org, Alexey.Melnikov@isode.com
  RFC6134          ||      A. Melnikov, B. Leiba         ||       Alexey.Melnikov@isode.com, barryleiba@computer.org
  RFC6135          ||      C. Holmberg, S. Blau         ||       christer.holmberg@ericsson.com, staffan.blau@ericsson.com
  RFC6136          ||      A. Sajassi, Ed., D. Mohan, Ed.         ||       sajassi@cisco.com, mohand@nortel.com
  RFC6137          ||      D. Zisiadis, Ed., S. Kopsidas, Ed., M. Tsavli, Ed., G. Cessieux, Ed.         ||       dzisiadis@iti.gr, spyros@uth.gr, sttsavli@uth.gr, Guillaume.Cessieux@cc.in2p3.fr
  RFC6138          ||      S. Kini, Ed., W. Lu, Ed.         ||       sriganesh.kini@ericsson.com, wenhu.lu@ericsson.com
  RFC6139          ||      S. Russert, Ed., E. Fleischman, Ed., F. Templin, Ed.         ||       russerts@hotmail.com, eric.fleischman@boeing.com, fltemplin@acm.org
  RFC6140          ||      A.B. Roach         ||       adam@nostrum.com
  RFC6141          ||      G. Camarillo, Ed., C. Holmberg, Y. Gao         ||       Gonzalo.Camarillo@ericsson.com, Christer.Holmberg@ericsson.com, gao.yang2@zte.com.cn
  RFC6142          ||      A. Moise, J. Brodkin         ||       avy@fdos.ca, jonathan.brodkin@fdos.ca
  RFC6143          ||      T. Richardson, J. Levine         ||       standards@realvnc.com, standards@taugh.com
  RFC6144          ||      F. Baker, X. Li, C. Bao, K. Yin         ||       fred@cisco.com, xing@cernet.edu.cn, congxiao@cernet.edu.cn, kyin@cisco.com
  RFC6145          ||      X. Li, C. Bao, F. Baker         ||       xing@cernet.edu.cn, congxiao@cernet.edu.cn, fred@cisco.com
  RFC6146          ||      M. Bagnulo, P. Matthews, I. van Beijnum         ||       marcelo@it.uc3m.es, philip_matthews@magma.ca, iljitsch@muada.com
  RFC6147          ||      M. Bagnulo, A. Sullivan, P. Matthews, I. van Beijnum         ||       marcelo@it.uc3m.es, ajs@shinkuro.com, philip_matthews@magma.ca, iljitsch@muada.com
  RFC6148          ||      P. Kurapati, R. Desetti, B. Joshi         ||       kurapati@juniper.net, ramakrishnadtv@infosys.com, bharat_joshi@infosys.com
  RFC6149          ||      S. Turner, L. Chen         ||       turners@ieca.com, lily.chen@nist.gov
  RFC6150          ||      S. Turner, L. Chen         ||       turners@ieca.com, lily.chen@nist.gov
  RFC6151          ||      S. Turner, L. Chen         ||       turners@ieca.com, lily.chen@nist.gov
  RFC6152          ||      J. Klensin, N. Freed, M. Rose, D. Crocker, Ed.         ||       john+ietf@jck.com, ned.freed@mrochek.com, mrose17@gmail.com, dcrocker@bbiw.net
  RFC6153          ||      S. Das, G. Bajko         ||       subir@research.Telcordia.com, gabor.bajko@nokia.com
  RFC6154          ||      B. Leiba, J. Nicolson         ||       barryleiba@computer.org, nicolson@google.com
  RFC6155          ||      J. Winterbottom, M. Thomson, H. Tschofenig, R. Barnes         ||       james.winterbottom@andrew.com, martin.thomson@andrew.com, Hannes.Tschofenig@gmx.net, rbarnes@bbn.com
  RFC6156          ||      G. Camarillo, O. Novo, S. Perreault, Ed.         ||       Gonzalo.Camarillo@ericsson.com, Oscar.Novo@ericsson.com, simon.perreault@viagenie.ca
  RFC6157          ||      G. Camarillo, K. El Malki, V. Gurbani         ||       Gonzalo.Camarillo@ericsson.com, karim@athonet.com, vkg@bell-labs.com
  RFC6158          ||      A. DeKok, Ed., G. Weber         ||       aland@freeradius.org, gdweber@gmail.com
  RFC6159          ||      T. Tsou, G. Zorn, T. Taylor, Ed.         ||       tena@huawei.com, gwz@net-zen.net, tom.taylor.stds@gmail.com
  RFC6160          ||      S. Turner         ||       turners@ieca.com
  RFC6161          ||      S. Turner         ||       turners@ieca.com
  RFC6162          ||      S. Turner         ||       turners@ieca.com
  RFC6163          ||      Y. Lee, Ed., G. Bernstein, Ed., W. Imajuku         ||       ylee@huawei.com, gregb@grotto-networking.com, imajuku.wataru@lab.ntt.co.jp
  RFC6164          ||      M. Kohno, B. Nitzan, R. Bush, Y. Matsuzaki, L. Colitti, T. Narten         ||       mkohno@juniper.net, nitzan@juniper.net, randy@psg.com, maz@iij.ad.jp, lorenzo@google.com, narten@us.ibm.com
  RFC6165          ||      A. Banerjee, D. Ward         ||       ayabaner@cisco.com, dward@juniper.net
  RFC6166          ||      S. Venaas         ||       stig@cisco.com
  RFC6167          ||      M. Phillips, P. Adams, D. Rokicki, E. Johnson         ||       m8philli@uk.ibm.com, phil_adams@us.ibm.com, derek.rokicki@softwareag.com, eric@tibco.com
  RFC6168          ||      W. Hardaker         ||       ietf@hardakers.net
  RFC6169          ||      S. Krishnan, D. Thaler, J. Hoagland         ||       suresh.krishnan@ericsson.com, dthaler@microsoft.com, Jim_Hoagland@symantec.com
  RFC6170          ||      S. Santesson, R. Housley, S. Bajaj, L. Rosenthol         ||       sts@aaa-sec.com, housley@vigilsec.com, siddharthietf@gmail.com, leonardr@adobe.com
  RFC6171          ||      K. Zeilenga         ||       Kurt.Zeilenga@Isode.COM
  RFC6172          ||      D. Black, D. Peterson         ||       david.black@emc.com, david.peterson@brocade.com
  RFC6173          ||      P. Venkatesen, Ed.         ||       prakashvn@hcl.com
  RFC6174          ||      E. Juskevicius         ||       edj.etc@gmail.com
  RFC6175          ||      E. Juskevicius         ||       edj.etc@gmail.com
  RFC6176          ||      S. Turner, T. Polk         ||       turners@ieca.com, tim.polk@nist.gov
  RFC6177          ||      T. Narten, G. Huston, L. Roberts         ||       narten@us.ibm.com, gih@apnic.net, lea.roberts@stanford.edu
  RFC6178          ||      D. Smith, J. Mullooly, W. Jaeger, T. Scholl         ||       djsmith@cisco.com, jmullool@cisco.com, wjaeger@att.com, tscholl@nlayer.net
  RFC6179          ||      F. Templin, Ed.         ||       fltemplin@acm.org
  RFC6180          ||      J. Arkko, F. Baker         ||       jari.arkko@piuha.net, fred@cisco.com
  RFC6181          ||      M. Bagnulo         ||       marcelo@it.uc3m.es
  RFC6182          ||      A. Ford, C. Raiciu, M. Handley, S. Barre, J. Iyengar         ||       alan.ford@roke.co.uk, c.raiciu@cs.ucl.ac.uk, m.handley@cs.ucl.ac.uk, sebastien.barre@uclouvain.be, jiyengar@fandm.edu
  RFC6183          ||      A. Kobayashi, B. Claise, G. Muenz, K. Ishibashi         ||       akoba@orange.plala.or.jp, bclaise@cisco.com, muenz@net.in.tum.de, ishibashi.keisuke@lab.ntt.co.jp
  RFC6184          ||      Y.-K. Wang, R. Even, T. Kristensen, R. Jesup         ||       yekuiwang@huawei.com, even.roni@huawei.com, tom.kristensen@tandberg.com, rjesup@wgate.com
  RFC6185          ||      T. Kristensen, P. Luthi         ||       tom.kristensen@tandberg.com, patrick.luthi@tandberg.com
  RFC6186          ||      C. Daboo         ||       cyrus@daboo.name
  RFC6187          ||      K. Igoe, D. Stebila         ||       kmigoe@nsa.gov, douglas@stebila.ca
  RFC6188          ||      D. McGrew         ||       mcgrew@cisco.com
  RFC6189          ||      P. Zimmermann, A. Johnston, Ed., J. Callas         ||       prz@mit.edu, alan.b.johnston@gmail.com, jon@callas.org
  RFC6190          ||      S. Wenger, Y.-K. Wang, T. Schierl, A. Eleftheriadis         ||       stewe@stewe.org, yekui.wang@huawei.com, ts@thomas-schierl.de, alex@vidyo.com
  RFC6191          ||      F. Gont         ||       fernando@gont.com.ar
  RFC6192          ||      D. Dugal, C. Pignataro, R. Dunn         ||       dave@juniper.net, cpignata@cisco.com, rodunn@cisco.com
  RFC6193          ||      M. Saito, D. Wing, M. Toyama         ||       ma.saito@nttv6.jp, dwing-ietf@fuggles.com, toyama.masashi@lab.ntt.co.jp
  RFC6194          ||      T. Polk, L. Chen, S. Turner, P. Hoffman         ||       tim.polk@nist.gov, lily.chen@nist.gov, turners@ieca.com, paul.hoffman@vpnc.org
  RFC6195          ||      D. Eastlake 3rd         ||       d3e3e3@gmail.com
  RFC6196          ||      A. Melnikov         ||       Alexey.Melnikov@isode.com
  RFC6197          ||      K. Wolf         ||       karlheinz.wolf@nic.at
  RFC6198          ||      B. Decraene, P. Francois, C. Pelsser, Z. Ahmad, A.J. Elizondo Armengol, T. Takeda         ||       bruno.decraene@orange-ftgroup.com, francois@info.ucl.ac.be, cristel@iij.ad.jp, zubair.ahmad@orange-ftgroup.com, ajea@tid.es, takeda.tomonori@lab.ntt.co.jp
  RFC6201          ||      R. Asati, C. Pignataro, F. Calabria, C. Olvera         ||       rajiva@cisco.com, cpignata@cisco.com, fcalabri@cisco.com, cesar.olvera@consulintel.es
  RFC6202          ||      S. Loreto, P. Saint-Andre, S. Salsano, G. Wilkins         ||       salvatore.loreto@ericsson.com, ietf@stpeter.im, stefano.salsano@uniroma2.it, gregw@webtide.com
  RFC6203          ||      T. Sirainen         ||       tss@iki.fi
  RFC6204          ||      H. Singh, W. Beebee, C. Donley, B. Stark, O. Troan, Ed.         ||       shemant@cisco.com, wbeebee@cisco.com, c.donley@cablelabs.com, barbara.stark@att.com, ot@cisco.com
  RFC6205          ||      T. Otani, Ed., D. Li, Ed.         ||       tm-otani@kddi.com, danli@huawei.com
  RFC6206          ||      P. Levis, T. Clausen, J. Hui, O. Gnawali, J. Ko         ||       pal@cs.stanford.edu, T.Clausen@computer.org, jhui@archrock.com, gnawali@cs.stanford.edu, jgko@cs.jhu.edu
  RFC6207          ||      R. Denenberg, Ed.         ||       rden@loc.gov
  RFC6208          ||      K. Sankar, Ed., A. Jones         ||       ksankar@cisco.com, arnold.jones@snia.org
  RFC6209          ||      W. Kim, J. Lee, J. Park, D. Kwon         ||       whkim5@ensec.re.kr, jklee@ensec.re.kr, jhpark@ensec.re.kr, ds_kwon@ensec.re.kr
  RFC6210          ||      J. Schaad         ||       ietf@augustcellars.com
  RFC6211          ||      J. Schaad         ||       ietf@augustcellars.com
  RFC6212          ||      M. Kucherawy         ||       msk@cloudmark.com
  RFC6213          ||      C. Hopps, L. Ginsberg         ||       chopps@cisco.com, ginsberg@cisco.com
  RFC6214          ||      B. Carpenter, R. Hinden         ||       brian.e.carpenter@gmail.com, bob.hinden@gmail.com
  RFC6215          ||      M. Bocci, L. Levrau, D. Frost         ||       matthew.bocci@alcatel-lucent.com, lieven.levrau@alcatel-lucent.com, danfrost@cisco.com
  RFC6216          ||      C. Jennings, K. Ono, R. Sparks, B. Hibbard, Ed.         ||       fluffy@cisco.com, kumiko@cs.columbia.edu, Robert.Sparks@tekelec.com, Brian.Hibbard@tekelec.com
  RFC6217          ||      T. Ritter         ||       tom@ritter.vg
  RFC6218          ||      G. Zorn, T. Zhang, J. Walker, J. Salowey         ||       gwz@net-zen.net, tzhang@advistatech.com, jesse.walker@intel.com, jsalowey@cisco.com
  RFC6219          ||      X. Li, C. Bao, M. Chen, H. Zhang, J. Wu         ||       xing@cernet.edu.cn, congxiao@cernet.edu.cn, fibrib@gmail.com, neilzh@gmail.com, jianping@cernet.edu.cn
  RFC6220          ||      D. McPherson, Ed., O. Kolkman, Ed., J. Klensin, Ed., G. Huston, Ed., Internet Architecture Board         ||       dmcpherson@verisign.com, olaf@NLnetLabs.nl, john+ietf@jck.com, gih@apnic.net
  RFC6221          ||      D. Miles, Ed., S. Ooghe, W. Dec, S. Krishnan, A. Kavanagh         ||       david.miles@alcatel-lucent.com, sven.ooghe@alcatel-lucent.com, wdec@cisco.com, suresh.krishnan@ericsson.com, alan.kavanagh@ericsson.com
  RFC6222          ||      A. Begen, C. Perkins, D. Wing         ||       abegen@cisco.com, csp@csperkins.org, dwing-ietf@fuggles.com
  RFC6223          ||      C. Holmberg         ||       christer.holmberg@ericsson.com
  RFC6224          ||      T. Schmidt, M. Waehlisch, S. Krishnan         ||       schmidt@informatik.haw-hamburg.de, mw@link-lab.net, suresh.krishnan@ericsson.com
  RFC6225          ||      J. Polk, M. Linsner, M. Thomson, B. Aboba, Ed.         ||       jmpolk@cisco.com, marc.linsner@cisco.com, martin.thomson@andrew.com, bernard_aboba@hotmail.com
  RFC6226          ||      B. Joshi, A. Kessler, D. McWalter         ||       bharat_joshi@infosys.com, kessler@cisco.com, david@mcwalter.eu
  RFC6227          ||      T. Li, Ed.         ||       tli@cisco.com
  RFC6228          ||      C. Holmberg         ||       christer.holmberg@ericsson.com
  RFC6229          ||      J. Strombergson, S. Josefsson         ||       joachim@secworks.se, simon@josefsson.org
  RFC6230          ||      C. Boulton, T. Melanchuk, S. McGlashan         ||       chris@ns-technologies.com, timm@rainwillow.com, smcg.stds01@mcglashan.org
  RFC6231          ||      S. McGlashan, T. Melanchuk, C. Boulton         ||       smcg.stds01@mcglashan.org, timm@rainwillow.com, chris@ns-technologies.com
  RFC6232          ||      F. Wei, Y. Qin, Z. Li, T. Li, J. Dong         ||       weifang@chinamobile.com, qinyue@chinamobile.com, lizhenqiang@chinamobile.com, tony.li@tony.li, dongjie_dj@huawei.com
  RFC6233          ||      T. Li, L. Ginsberg         ||       tony.li@tony.li, ginsberg@cisco.com
  RFC6234          ||      D. Eastlake 3rd, T. Hansen         ||       d3e3e3@gmail.com, tony+shs@maillennium.att.com
  RFC6235          ||      E. Boschi, B. Trammell         ||       boschie@tik.ee.ethz.ch, trammell@tik.ee.ethz.ch
  RFC6236          ||      I. Johansson, K. Jung         ||       ingemar.s.johansson@ericsson.com, kyunghun.jung@samsung.com
  RFC6237          ||      B. Leiba, A. Melnikov         ||       barryleiba@computer.org, Alexey.Melnikov@isode.com
  RFC6238          ||      D. M'Raihi, S. Machani, M. Pei, J. Rydell         ||       davidietf@gmail.com, smachani@diversinet.com, Mingliang_Pei@symantec.com, johanietf@gmail.com
  RFC6239          ||      K. Igoe         ||       kmigoe@nsa.gov
  RFC6240          ||      D. Zelig, Ed., R. Cohen, Ed., T. Nadeau, Ed.         ||       david_zelig@pmc-sierra.com, ronc@resolutenetworks.com, Thomas.Nadeau@ca.com
  RFC6241          ||      R. Enns, Ed., M. Bjorklund, Ed., J. Schoenwaelder, Ed., A. Bierman, Ed.         ||       rob.enns@gmail.com, mbj@tail-f.com, j.schoenwaelder@jacobs-university.de, andy@yumaworks.com
  RFC6242          ||      M. Wasserman         ||       mrw@painless-security.com
  RFC6243          ||      A. Bierman, B. Lengyel         ||       andy@yumaworks.com, balazs.lengyel@ericsson.com
  RFC6244          ||      P. Shafer         ||       phil@juniper.net
  RFC6245          ||      P. Yegani, K. Leung, A. Lior, K. Chowdhury, J. Navali         ||       pyegani@juniper.net, kleung@cisco.com, avi@bridgewatersystems.com, kchowdhu@cisco.com, jnavali@cisco.com
  RFC6246          ||      A. Sajassi, Ed., F. Brockners, D. Mohan, Ed., Y. Serbest         ||       sajassi@cisco.com, fbrockne@cisco.com, dinmohan@hotmail.com, yetik_serbest@labs.att.com
  RFC6247          ||      L. Eggert         ||       lars.eggert@nokia.com
  RFC6248          ||      A. Morton         ||       acmorton@att.com
  RFC6249          ||      A. Bryan, N. McNab, T. Tsujikawa, P. Poeml, H. Nordstrom         ||       anthonybryan@gmail.com, neil@nabber.org, tatsuhiro.t@gmail.com, peter@poeml.de, henrik@henriknordstrom.net
  RFC6250          ||      D. Thaler         ||       dthaler@microsoft.com
  RFC6251          ||      S. Josefsson         ||       simon@josefsson.org
  RFC6252          ||      A. Dutta, Ed., V. Fajardo, Y. Ohba, K. Taniuchi, H. Schulzrinne         ||       ashutosh.dutta@ieee.org, vf0213@gmail.com, yoshihiro.ohba@toshiba.co.jp, kenichi.taniuchi@toshiba.co.jp, hgs@cs.columbia.edu
  RFC6253          ||      T. Heer, S. Varjonen         ||       heer@cs.rwth-aachen.de, samu.varjonen@hiit.fi
  RFC6254          ||      M. McFadden         ||       mark.mcfadden@icann.org
  RFC6255          ||      M. Blanchet         ||       Marc.Blanchet@viagenie.ca
  RFC6256          ||      W. Eddy, E. Davies         ||       wes@mti-systems.com, elwynd@folly.org.uk
  RFC6257          ||      S. Symington, S. Farrell, H. Weiss, P. Lovell         ||       susan@mitre.org, stephen.farrell@cs.tcd.ie, howard.weiss@sparta.com, dtnbsp@gmail.com
  RFC6258          ||      S. Symington         ||       susan@mitre.org
  RFC6259          ||      S. Symington         ||       susan@mitre.org
  RFC6260          ||      S. Burleigh         ||       Scott.C.Burleigh@jpl.nasa.gov
  RFC6261          ||      A. Keranen         ||       ari.keranen@ericsson.com
  RFC6262          ||      S. Ikonin         ||       ikonin@spiritdsp.com
  RFC6263          ||      X. Marjou, A. Sollaud         ||       xavier.marjou@orange-ftgroup.com, aurelien.sollaud@orange-ftgroup.com
  RFC6264          ||      S. Jiang, D. Guo, B. Carpenter         ||       jiangsheng@huawei.com, guoseu@huawei.com, brian.e.carpenter@gmail.com
  RFC6265          ||      A. Barth         ||       abarth@eecs.berkeley.edu
  RFC6266          ||      J. Reschke         ||       julian.reschke@greenbytes.de
  RFC6267          ||      V. Cakulev, G. Sundaram         ||       violeta.cakulev@alcatel-lucent.com, ganesh.sundaram@alcatel-lucent.com
  RFC6268          ||      J. Schaad, S. Turner         ||       ietf@augustcellars.com, turners@ieca.com
  RFC6269          ||      M. Ford, Ed., M. Boucadair, A. Durand, P. Levis, P. Roberts         ||       ford@isoc.org, mohamed.boucadair@orange-ftgroup.com, adurand@juniper.net, pierre.levis@orange-ftgroup.com, roberts@isoc.org
  RFC6270          ||      M. Yevstifeyev         ||       evnikita2@gmail.com
  RFC6271          ||      J-F. Mule         ||       jf.mule@cablelabs.com
  RFC6272          ||      F. Baker, D. Meyer         ||       fred@cisco.com, dmm@cisco.com
  RFC6273          ||      A. Kukec, S. Krishnan, S. Jiang         ||       ana.kukec@fer.hr, suresh.krishnan@ericsson.com, jiangsheng@huawei.com
  RFC6274          ||      F. Gont         ||       fernando@gont.com.ar
  RFC6275          ||      C. Perkins, Ed., D. Johnson, J. Arkko         ||       charliep@computer.org, dbj@cs.rice.edu, jari.arkko@ericsson.com
  RFC6276          ||      R. Droms, P. Thubert, F. Dupont, W. Haddad, C. Bernardos         ||       rdroms@cisco.com, pthubert@cisco.com, fdupont@isc.org, Wassim.Haddad@ericsson.com, cjbc@it.uc3m.es
  RFC6277          ||      S. Santesson, P. Hallam-Baker         ||       sts@aaa-sec.com, hallam@gmail.com
  RFC6278          ||      J. Herzog, R. Khazan         ||       jherzog@ll.mit.edu, rkh@ll.mit.edu
  RFC6279          ||      M. Liebsch, Ed., S. Jeong, Q. Wu         ||       liebsch@neclab.eu, sjjeong@etri.re.kr, sunseawq@huawei.com
  RFC6280          ||      R. Barnes, M. Lepinski, A. Cooper, J. Morris, H. Tschofenig, H. Schulzrinne         ||       rbarnes@bbn.com, mlepinski@bbn.com, acooper@cdt.org, jmorris@cdt.org, Hannes.Tschofenig@gmx.net, hgs@cs.columbia.edu
  RFC6281          ||      S. Cheshire, Z. Zhu, R. Wakikawa, L. Zhang         ||       cheshire@apple.com, zhenkai@ucla.edu, ryuji@jp.toyota-itc.com, lixia@cs.ucla.edu
  RFC6282          ||      J. Hui, Ed., P. Thubert         ||       jhui@archrock.com, pthubert@cisco.com
  RFC6283          ||      A. Jerman Blazic, S. Saljic, T. Gondrom         ||       aljosa@setcce.si, svetlana.saljic@setcce.si, tobias.gondrom@gondrom.org
  RFC6284          ||      A. Begen, D. Wing, T. Van Caenegem         ||       abegen@cisco.com, dwing-ietf@fuggles.com, Tom.Van_Caenegem@alcatel-lucent.com
  RFC6285          ||      B. Ver Steeg, A. Begen, T. Van Caenegem, Z. Vax         ||       billvs@cisco.com, abegen@cisco.com, Tom.Van_Caenegem@alcatel-lucent.be, zeevvax@microsoft.com
  RFC6286          ||      E. Chen, J. Yuan         ||       enkechen@cisco.com, jenny@cisco.com
  RFC6287          ||      D. M'Raihi, J. Rydell, S. Bajaj, S. Machani, D. Naccache         ||       davidietf@gmail.com, johanietf@gmail.com, siddharthietf@gmail.com, smachani@diversinet.com, david.naccache@ens.fr
  RFC6288          ||      C. Reed         ||       creed@opengeospatial.org
  RFC6289          ||      E. Cardona, S. Channabasappa, J-F. Mule         ||       e.cardona@cablelabs.com, sumanth@cablelabs.com, jf.mule@cablelabs.com
  RFC6290          ||      Y. Nir, Ed., D. Wierbowski, F. Detienne, P. Sethi         ||       ynir@checkpoint.com, wierbows@us.ibm.com, fd@cisco.com, psethi@cisco.com
  RFC6291          ||      L. Andersson, H. van Helvoort, R. Bonica, D. Romascanu, S. Mansfield         ||       loa.andersson@ericsson.com, huub.van.helvoort@huawei.com, rbonica@juniper.net, dromasca@gmail.com , scott.mansfield@ericsson.com
  RFC6292          ||      P. Hoffman         ||       paul.hoffman@vpnc.org
  RFC6293          ||      P. Hoffman         ||       paul.hoffman@vpnc.org
  RFC6294          ||      Q. Hu, B. Carpenter         ||       qhu009@aucklanduni.ac.nz, brian.e.carpenter@gmail.com
  RFC6295          ||      J. Lazzaro, J. Wawrzynek         ||       lazzaro@cs.berkeley.edu, johnw@cs.berkeley.edu
  RFC6296          ||      M. Wasserman, F. Baker         ||       mrw@painless-security.com, fred@cisco.com
  RFC6297          ||      M. Welzl, D. Ros         ||       michawe@ifi.uio.no, david.ros@telecom-bretagne.eu
  RFC6298          ||      V. Paxson, M. Allman, J. Chu, M. Sargent         ||       vern@icir.org, mallman@icir.org, hkchu@google.com, mts71@case.edu
  RFC6301          ||      Z. Zhu, R. Wakikawa, L. Zhang         ||       zhenkai@cs.ucla.edu, ryuji.wakikawa@gmail.com, lixia@cs.ucla.edu
  RFC6302          ||      A. Durand, I. Gashinsky, D. Lee, S. Sheppard         ||       adurand@juniper.net, igor@yahoo-inc.com, donn@fb.com, Scott.Sheppard@att.com
  RFC6303          ||      M. Andrews         ||       marka@isc.org
  RFC6304          ||      J. Abley, W. Maton         ||       joe.abley@icann.org, wmaton@ryouko.imsb.nrc.ca
  RFC6305          ||      J. Abley, W. Maton         ||       joe.abley@icann.org, wmaton@ryouko.imsb.nrc.ca
  RFC6306          ||      P. Frejborg         ||       pfrejborg@gmail.com
  RFC6307          ||      D. Black, Ed., L. Dunbar, Ed., M. Roth, R. Solomon         ||       david.black@emc.com, ldunbar@huawei.com, MRoth@infinera.com, ronens@corrigent.com
  RFC6308          ||      P. Savola         ||       psavola@funet.fi
  RFC6309          ||      J. Arkko, A. Keranen, J. Mattsson         ||       jari.arkko@piuha.net, ari.keranen@ericsson.com, john.mattsson@ericsson.com
  RFC6310          ||      M. Aissaoui, P. Busschbach, L. Martini, M. Morrow, T. Nadeau, Y(J). Stein         ||       mustapha.aissaoui@alcatel-lucent.com, busschbach@alcatel-lucent.com, lmartini@cisco.com, mmorrow@cisco.com, Thomas.Nadeau@ca.com, yaakov_s@rad.com
  RFC6311          ||      R. Singh, Ed., G. Kalyani, Y. Nir, Y. Sheffer, D. Zhang         ||       rsj@cisco.com, kagarigi@cisco.com, ynir@checkpoint.com, yaronf.ietf@gmail.com, zhangdacheng@huawei.com
  RFC6312          ||      R. Koodli         ||       rkoodli@cisco.com
  RFC6313          ||      B. Claise, G. Dhandapani, P. Aitken, S. Yates         ||       bclaise@cisco.com, gowri@cisco.com, paitken@cisco.com, syates@cisco.com
  RFC6314          ||      C. Boulton, J. Rosenberg, G. Camarillo, F. Audet         ||       chris@ns-technologies.com, jdrosen@jdrosen.net, Gonzalo.Camarillo@ericsson.com, francois.audet@skype.net
  RFC6315          ||      E. Guy, K. Darilion         ||       edguy@CleverSpoke.com, klaus.darilion@nic.at
  RFC6316          ||      M. Komu, M. Bagnulo, K. Slavov, S. Sugimoto, Ed.         ||       miika@iki.fi, marcelo@it.uc3m.es, kristian.slavov@ericsson.com, shinta@sfc.wide.ad.jp
  RFC6317          ||      M. Komu, T. Henderson         ||       miika@iki.fi, thomas.r.henderson@boeing.com
  RFC6318          ||      R. Housley, J. Solinas         ||       housley@vigilsec.com, jasolin@orion.ncsc.mil
  RFC6319          ||      M. Azinger, L. Vegoda         ||       marla.azinger@ftr.com, leo.vegoda@icann.org
  RFC6320          ||      S. Wadhwa, J. Moisand, T. Haag, N. Voigt, T. Taylor, Ed.         ||       sanjay.wadhwa@alcatel-lucent.com, jmoisand@juniper.net, haagt@telekom.de, norbert.voigt@nsn.com, tom.taylor.stds@gmail.com
  RFC6321          ||      C. Daboo, M. Douglass, S. Lees         ||       cyrus@daboo.name, douglm@rpi.edu, steven.lees@microsoft.com
  RFC6322          ||      P. Hoffman         ||       paul.hoffman@vpnc.org
  RFC6323          ||      G. Renker, G. Fairhurst         ||       gerrit@erg.abdn.ac.uk, gorry@erg.abdn.ac.uk
  RFC6324          ||      G. Nakibly, F. Templin         ||       gnakibly@yahoo.com, fltemplin@acm.org
  RFC6325          ||      R. Perlman, D. Eastlake 3rd, D. Dutt, S. Gai, A. Ghanwani         ||       Radia@alum.mit.edu, d3e3e3@gmail.com, ddutt@cisco.com, silvano@ip6.com, anoop@alumni.duke.edu
  RFC6326          ||      D. Eastlake, A. Banerjee, D. Dutt, R. Perlman, A. Ghanwani         ||       d3e3e3@gmail.com, ayabaner@cisco.com, ddutt@cisco.com, Radia@alum.mit.edu, anoop@alumni.duke.edu
  RFC6327          ||      D. Eastlake 3rd, R. Perlman, A. Ghanwani, D. Dutt, V. Manral         ||       d3e3e3@gmail.com, Radia@alum.mit.edu, anoop@alumni.duke.edu, ddutt@cisco.com, vishwas.manral@hp.com
  RFC6328          ||      D. Eastlake 3rd         ||       d3e3e3@gmail.com
  RFC6329          ||      D. Fedyk, Ed., P. Ashwood-Smith, Ed., D. Allan, A. Bragg, P. Unbehagen         ||       Donald.Fedyk@alcatel-lucent.com, Peter.AshwoodSmith@huawei.com, david.i.allan@ericsson.com, nbragg@ciena.com, unbehagen@avaya.com
  RFC6330          ||      M. Luby, A. Shokrollahi, M. Watson, T. Stockhammer, L. Minder         ||       luby@qti.qualcomm.com, amin.shokrollahi@epfl.ch, watsonm@netflix.com, stockhammer@nomor.de, lminder@qualcomm.com
  RFC6331          ||      A. Melnikov         ||       Alexey.Melnikov@isode.com
  RFC6332          ||      A. Begen, E. Friedrich         ||       abegen@cisco.com, efriedri@cisco.com
  RFC6333          ||      A. Durand, R. Droms, J. Woodyatt, Y. Lee         ||       adurand@juniper.net, rdroms@cisco.com, jhw@apple.com, yiu_lee@cable.comcast.com
  RFC6334          ||      D. Hankins, T. Mrugalski         ||       dhankins@google.com, tomasz.mrugalski@eti.pg.gda.pl
  RFC6335          ||      M. Cotton, L. Eggert, J. Touch, M. Westerlund, S. Cheshire         ||       michelle.cotton@icann.org, lars.eggert@nokia.com, touch@isi.edu, magnus.westerlund@ericsson.com, cheshire@apple.com
  RFC6336          ||      M. Westerlund, C. Perkins         ||       magnus.westerlund@ericsson.com, csp@csperkins.org
  RFC6337          ||      S. Okumura, T. Sawada, P. Kyzivat         ||       shinji.okumura@softfront.jp, tu-sawada@kddi.com, pkyzivat@alum.mit.edu
  RFC6338          ||      V. Giralt, R. McDuff         ||       victoriano@uma.es, r.mcduff@uq.edu.au
  RFC6339          ||      S. Josefsson, L. Hornquist Astrand         ||       simon@josefsson.org, lha@apple.com
  RFC6340          ||      R. Presuhn         ||       randy_presuhn@mindspring.com
  RFC6341          ||      K. Rehor, Ed., L. Portman, Ed., A. Hutton, R. Jain         ||       krehor@cisco.com, leon.portman@nice.com, andrew.hutton@siemens-enterprise.com, rajnish.jain@ipc.com
  RFC6342          ||      R. Koodli         ||       rkoodli@cisco.com
  RFC6343          ||      B. Carpenter         ||       brian.e.carpenter@gmail.com
  RFC6344          ||      G. Bernstein, Ed., D. Caviglia, R. Rabbat, H. van Helvoort         ||       gregb@grotto-networking.com, diego.caviglia@ericsson.com, rabbat@alum.mit.edu, hhelvoort@huawei.com
  RFC6345          ||      P. Duffy, S. Chakrabarti, R. Cragie, Y. Ohba, Ed., A. Yegin         ||       paduffy@cisco.com, samita.chakrabarti@ericsson.com, robert.cragie@gridmerge.com, yoshihiro.ohba@toshiba.co.jp, a.yegin@partner.samsung.com
  RFC6346          ||      R. Bush, Ed.         ||       randy@psg.com
  RFC6347          ||      E. Rescorla, N. Modadugu         ||       ekr@rtfm.com, nagendra@cs.stanford.edu
  RFC6348          ||      JL. Le Roux, Ed., T. Morin, Ed.         ||       jeanlouis.leroux@orange-ftgroup.com, thomas.morin@orange-ftgroup.com
  RFC6349          ||      B. Constantine, G. Forget, R. Geib, R. Schrage         ||       barry.constantine@jdsu.com, gilles.forget@sympatico.ca, Ruediger.Geib@telekom.de, reinhard@schrageconsult.com
  RFC6350          ||      S. Perreault         ||       simon.perreault@viagenie.ca
  RFC6351          ||      S. Perreault         ||       simon.perreault@viagenie.ca
  RFC6352          ||      C. Daboo         ||       cyrus@daboo.name
  RFC6353          ||      W. Hardaker         ||       ietf@hardakers.net
  RFC6354          ||      Q. Xie         ||       Qiaobing.Xie@gmail.com
  RFC6355          ||      T. Narten, J. Johnson         ||       narten@us.ibm.com, jarrod.b.johnson@gmail.com
  RFC6356          ||      C. Raiciu, M. Handley, D. Wischik         ||       costin.raiciu@cs.pub.ro, m.handley@cs.ucl.ac.uk, d.wischik@cs.ucl.ac.uk
  RFC6357          ||      V. Hilt, E. Noel, C. Shen, A. Abdelal         ||       volker.hilt@alcatel-lucent.com, eric.noel@att.com, charles@cs.columbia.edu, aabdelal@sonusnet.com
  RFC6358          ||      P. Hoffman         ||       paul.hoffman@vpnc.org
  RFC6359          ||      S. Ginoza, M. Cotton, A. Morris         ||       sginoza@amsl.com, michelle.cotton@icann.org, amorris@amsl.com
  RFC6360          ||      R. Housley         ||       housley@vigilsec.com
  RFC6361          ||      J. Carlson, D. Eastlake 3rd         ||       carlsonj@workingcode.com, d3e3e3@gmail.com
  RFC6362          ||      K. Meadors, Ed.         ||       kyle@drummondgroup.com
  RFC6363          ||      M. Watson, A. Begen, V. Roca         ||       watsonm@netflix.com, abegen@cisco.com, vincent.roca@inria.fr
  RFC6364          ||      A. Begen         ||       abegen@cisco.com
  RFC6365          ||      P. Hoffman, J. Klensin         ||       paul.hoffman@vpnc.org, john+ietf@jck.com
  RFC6366          ||      J. Valin, K. Vos         ||       jmvalin@jmvalin.ca, koen.vos@skype.net
  RFC6367          ||      S. Kanno, M. Kanda         ||       kanno.satoru@po.ntts.co.jp, kanda.masayuki@lab.ntt.co.jp
  RFC6368          ||      P. Marques, R. Raszuk, K. Patel, K. Kumaki, T. Yamagata         ||       pedro.r.marques@gmail.com, robert@raszuk.net, keyupate@cisco.com, ke-kumaki@kddi.com, to-yamagata@kddi.com
  RFC6369          ||      E. Haleplidis, O. Koufopavlou, S. Denazis         ||       ehalep@ece.upatras.gr, odysseas@ece.upatras.gr, sdena@upatras.gr
  RFC6370          ||      M. Bocci, G. Swallow, E. Gray         ||       matthew.bocci@alcatel-lucent.com, swallow@cisco.com, eric.gray@ericsson.com
  RFC6371          ||      I. Busi, Ed., D. Allan, Ed.         ||       Italo.Busi@alcatel-lucent.com, david.i.allan@ericsson.com
  RFC6372          ||      N. Sprecher, Ed., A. Farrel, Ed.         ||       nurit.sprecher@nsn.com, adrian@olddog.co.uk
  RFC6373          ||      L. Andersson, Ed., L. Berger, Ed., L. Fang, Ed., N. Bitar, Ed., E. Gray, Ed.         ||       loa.andersson@ericsson.com, lberger@labn.net, lufang@cisco.com, nabil.n.bitar@verizon.com, Eric.Gray@Ericsson.com
  RFC6374          ||      D. Frost, S. Bryant         ||       danfrost@cisco.com, stbryant@cisco.com
  RFC6375          ||      D. Frost, Ed., S. Bryant, Ed.         ||       danfrost@cisco.com, stbryant@cisco.com
  RFC6376          ||      D. Crocker, Ed., T. Hansen, Ed., M. Kucherawy, Ed.         ||       dcrocker@bbiw.net, tony+dkimov@maillennium.att.com, msk@cloudmark.com
  RFC6377          ||      M. Kucherawy         ||       msk@cloudmark.com
  RFC6378          ||      Y. Weingarten, Ed., S. Bryant, E. Osborne, N. Sprecher, A. Fulignoli, Ed.         ||       yaacov.weingarten@nsn.com, stbryant@cisco.com, eosborne@cisco.com, nurit.sprecher@nsn.com, annamaria.fulignoli@ericsson.com
  RFC6379          ||      L. Law, J. Solinas         ||       lelaw@orion.ncsc.mil, jasolin@orion.ncsc.mil
  RFC6380          ||      K. Burgin, M. Peck         ||       kwburgi@tycho.ncsc.mil, mpeck@mitre.org
  RFC6381          ||      R. Gellens, D. Singer, P. Frojdh         ||       rg+ietf@qualcomm.com, singer@apple.com, Per.Frojdh@ericsson.com
  RFC6382          ||      D. McPherson, R. Donnelly, F. Scalzo         ||       dmcpherson@verisign.com, rdonnelly@verisign.com, fscalzo@verisign.com
  RFC6383          ||      K. Shiomoto, A. Farrel         ||       shiomoto.kohei@lab.ntt.co.jp, adrian@olddog.co.uk
  RFC6384          ||      I. van Beijnum         ||       iljitsch@muada.com
  RFC6385          ||      M. Barnes, A. Doria, H. Alvestrand, B. Carpenter         ||       mary.ietf.barnes@gmail.com, avri@acm.org, harald@alvestrand.no, brian.e.carpenter@gmail.com
  RFC6386          ||      J. Bankoski, J. Koleszar, L. Quillio, J. Salonen, P. Wilkins, Y. Xu         ||       jimbankoski@google.com, jkoleszar@google.com, louquillio@google.com, jsalonen@google.com, paulwilkins@google.com, yaowu@google.com
  RFC6387          ||      A. Takacs, L. Berger, D. Caviglia, D. Fedyk, J. Meuric         ||       attila.takacs@ericsson.com, lberger@labn.net, diego.caviglia@ericsson.com, donald.fedyk@alcatel-lucent.com, julien.meuric@orange.com
  RFC6388          ||      IJ. Wijnands, Ed., I. Minei, Ed., K. Kompella, B. Thomas         ||       ice@cisco.com, ina@juniper.net, kireeti@juniper.net, bobthomas@alum.mit.edu
  RFC6389          ||      R. Aggarwal, JL. Le Roux         ||       raggarwa_1@yahoo.com, jeanlouis.leroux@orange-ftgroup.com
  RFC6390          ||      A. Clark, B. Claise         ||       alan.d.clark@telchemy.com, bclaise@cisco.com
  RFC6391          ||      S. Bryant, Ed., C. Filsfils, U. Drafz, V. Kompella, J. Regan, S. Amante         ||       stbryant@cisco.com, cfilsfil@cisco.com, Ulrich.Drafz@telekom.de, vach.kompella@alcatel-lucent.com, joe.regan@alcatel-lucent.com, shane@level3.net
  RFC6392          ||      R. Alimi, Ed., A. Rahman, Ed., Y. Yang, Ed.         ||       ralimi@google.com, Akbar.Rahman@InterDigital.com, yry@cs.yale.edu
  RFC6393          ||      M. Yevstifeyev         ||       evnikita2@gmail.com
  RFC6394          ||      R. Barnes         ||       rbarnes@bbn.com
  RFC6395          ||      S. Gulrajani, S. Venaas         ||       sameerg@cisco.com, stig@cisco.com
  RFC6396          ||      L. Blunk, M. Karir, C. Labovitz         ||       ljb@merit.edu, mkarir@merit.edu, labovit@deepfield.net
  RFC6397          ||      T. Manderson         ||       terry.manderson@icann.org
  RFC6398          ||      F. Le Faucheur, Ed.         ||       flefauch@cisco.com
  RFC6401          ||      F. Le Faucheur, J. Polk, K. Carlberg         ||       flefauch@cisco.com, jmpolk@cisco.com, carlberg@g11.org.uk
  RFC6402          ||      J. Schaad         ||       jimsch@augustcellars.com
  RFC6403          ||      L. Zieglar, S. Turner, M. Peck         ||       llziegl@tycho.ncsc.mil, turners@ieca.com, mpeck@alumni.virginia.edu
  RFC6404          ||      J. Seedorf, S. Niccolini, E. Chen, H. Scholz         ||       jan.seedorf@nw.neclab.eu, saverio.niccolini@.neclab.eu, eric.chen@lab.ntt.co.jp, hendrik.scholz@voipfuture.com
  RFC6405          ||      A. Uzelac, Ed., Y. Lee, Ed.         ||       adam.uzelac@globalcrossing.com, yiu_lee@cable.comcast.com
  RFC6406          ||      D. Malas, Ed., J. Livingood, Ed.         ||       d.malas@cablelabs.com, Jason_Livingood@cable.comcast.com
  RFC6407          ||      B. Weis, S. Rowles, T. Hardjono         ||       bew@cisco.com, sheela@cisco.com, hardjono@mit.edu
  RFC6408          ||      M. Jones, J. Korhonen, L. Morand         ||       mark@azu.ca, jouni.nospam@gmail.com, lionel.morand@orange-ftgroup.com
  RFC6409          ||      R. Gellens, J. Klensin         ||       rg+ietf@qualcomm.com, john-ietf@jck.com
  RFC6410          ||      R. Housley, D. Crocker, E. Burger         ||       housley@vigilsec.com, dcrocker@bbiw.net, eburger@standardstrack.com
  RFC6411          ||      M. Behringer, F. Le Faucheur, B. Weis         ||       mbehring@cisco.com, flefauch@cisco.com, bew@cisco.com
  RFC6412          ||      S. Poretsky, B. Imhoff, K. Michielsen         ||       sporetsky@allot.com, bimhoff@planetspork.com, kmichiel@cisco.com
  RFC6413          ||      S. Poretsky, B. Imhoff, K. Michielsen         ||       sporetsky@allot.com, bimhoff@planetspork.com, kmichiel@cisco.com
  RFC6414          ||      S. Poretsky, R. Papneja, J. Karthik, S. Vapiwala         ||       sporetsky@allot.com, rajiv.papneja@huawei.com, jkarthik@cisco.com, svapiwal@cisco.com
  RFC6415          ||      E. Hammer-Lahav, Ed., B. Cook         ||       eran@hueniverse.com, romeda@gmail.com
  RFC6416          ||      M. Schmidt, F. de Bont, S. Doehla, J. Kim         ||       malte.schmidt@dolby.com, frans.de.bont@philips.com, stefan.doehla@iis.fraunhofer.de, kjh1905m@naver.com
  RFC6417          ||      P. Eardley, L. Eggert, M. Bagnulo, R. Winter         ||       philip.eardley@bt.com, lars.eggert@nokia.com, marcelo@it.uc3m.es, rolf.winter@neclab.eu
  RFC6418          ||      M. Blanchet, P. Seite         ||       Marc.Blanchet@viagenie.ca, pierrick.seite@orange.com
  RFC6419          ||      M. Wasserman, P. Seite         ||       mrw@painless-security.com, pierrick.seite@orange-ftgroup.com
  RFC6420          ||      Y. Cai, H. Ou         ||       ycai@cisco.com, hou@cisco.com
  RFC6421          ||      D. Nelson, Ed.         ||       d.b.nelson@comcast.net
  RFC6422          ||      T. Lemon, Q. Wu         ||       mellon@nominum.com, sunseawq@huawei.com
  RFC6423          ||      H. Li, L. Martini, J. He, F. Huang         ||       lihan@chinamobile.com, lmartini@cisco.com, hejia@huawei.com, feng.f.huang@alcatel-sbell.com.cn
  RFC6424          ||      N. Bahadur, K. Kompella, G. Swallow         ||       nitinb@juniper.net, kireeti@juniper.net, swallow@cisco.com
  RFC6425          ||      S. Saxena, Ed., G. Swallow, Z. Ali, A. Farrel, S. Yasukawa, T. Nadeau         ||       ssaxena@cisco.com, swallow@cisco.com, zali@cisco.com, adrian@olddog.co.uk, yasukawa.seisho@lab.ntt.co.jp, thomas.nadeau@ca.com
  RFC6426          ||      E. Gray, N. Bahadur, S. Boutros, R. Aggarwal         ||       eric.gray@ericsson.com, nitinb@juniper.net, sboutros@cisco.com, raggarwa_1@yahoo.com
  RFC6427          ||      G. Swallow, Ed., A. Fulignoli, Ed., M. Vigoureux, Ed., S. Boutros, D. Ward         ||       swallow@cisco.com, annamaria.fulignoli@ericsson.com, martin.vigoureux@alcatel-lucent.com, sboutros@cisco.com, dward@juniper.net
  RFC6428          ||      D. Allan, Ed., G. Swallow, Ed., J. Drake, Ed.         ||       david.i.allan@ericsson.com, swallow@cisco.com, jdrake@juniper.net
  RFC6429          ||      M. Bashyam, M. Jethanandani, A. Ramaiah         ||       mbashyam@ocarinanetworks.com, mjethanandani@gmail.com, ananth@cisco.com
  RFC6430          ||      K. Li, B. Leiba         ||       likepeng@huawei.com, barryleiba@computer.org
  RFC6431          ||      M. Boucadair, P. Levis, G. Bajko, T. Savolainen, T. Tsou         ||       mohamed.boucadair@orange.com, pierre.levis@orange.com, gabor.bajko@nokia.com, teemu.savolainen@nokia.com, tina.tsou.zouting@huawei.com
  RFC6432          ||      R. Jesske, L. Liess         ||       r.jesske@telekom.de, L.Liess@telekom.de
  RFC6433          ||      P. Hoffman         ||       paul.hoffman@vpnc.org
  RFC6434          ||      E. Jankiewicz, J. Loughney, T. Narten         ||       edward.jankiewicz@sri.com, john.loughney@nokia.com, narten@us.ibm.com
  RFC6435          ||      S. Boutros, Ed., S. Sivabalan, Ed., R. Aggarwal, Ed., M. Vigoureux, Ed., X. Dai, Ed.         ||       sboutros@cisco.com, msiva@cisco.com, raggarwa_1@yahoo.com, martin.vigoureux@alcatel-lucent.com, dai.xuehui@zte.com.cn
  RFC6436          ||      S. Amante, B. Carpenter, S. Jiang         ||       shane@level3.net, brian.e.carpenter@gmail.com, shengjiang@huawei.com
  RFC6437          ||      S. Amante, B. Carpenter, S. Jiang, J. Rajahalme         ||       shane@level3.net, brian.e.carpenter@gmail.com, jiangsheng@huawei.com, jarno.rajahalme@nsn.com
  RFC6438          ||      B. Carpenter, S. Amante         ||       brian.e.carpenter@gmail.com, shane@level3.net
  RFC6439          ||      R. Perlman, D. Eastlake, Y. Li, A. Banerjee, F. Hu         ||       Radia@alum.mit.edu, d3e3e3@gmail.com, liyizhou@huawei.com, ayabaner@cisco.com, hu.fangwei@zte.com.cn
  RFC6440          ||      G. Zorn, Q. Wu, Y. Wang         ||       gwz@net-zen.net, sunseawq@huawei.com, w52006@huawei.com
  RFC6441          ||      L. Vegoda         ||       leo.vegoda@icann.org
  RFC6442          ||      J. Polk, B. Rosen, J. Peterson         ||       jmpolk@cisco.com, br@brianrosen.net, jon.peterson@neustar.biz
  RFC6443          ||      B. Rosen, H. Schulzrinne, J. Polk, A. Newton         ||       br@brianrosen.net, hgs@cs.columbia.edu, jmpolk@cisco.com, andy@hxr.us
  RFC6444          ||      H. Schulzrinne, L. Liess, H. Tschofenig, B. Stark, A. Kuett         ||       hgs+ecrit@cs.columbia.edu, L.Liess@telekom.de, Hannes.Tschofenig@gmx.net, barbara.stark@att.com, andres.kytt@skype.net
  RFC6445          ||      T. Nadeau, Ed., A. Koushik, Ed., R. Cetin, Ed.         ||       thomas.nadeau@ca.com, kkoushik@cisco.com, riza.cetin@alcatel.be
  RFC6446          ||      A. Niemi, K. Kiss, S. Loreto         ||       aki.niemi@nokia.com, krisztian.kiss@nokia.com, salvatore.loreto@ericsson.com
  RFC6447          ||      R. Mahy, B. Rosen, H. Tschofenig         ||       rohan@ekabal.com, br@brianrosen.net, Hannes.Tschofenig@gmx.net
  RFC6448          ||      R. Yount         ||       rjy@cmu.edu
  RFC6449          ||      J. Falk, Ed.         ||       ietf@cybernothing.org
  RFC6450          ||      S. Venaas         ||       stig@cisco.com
  RFC6451          ||      A. Forte, H. Schulzrinne         ||       forte@att.com, hgs@cs.columbia.edu
  RFC6452          ||      P. Faltstrom, Ed., P. Hoffman, Ed.         ||       paf@cisco.com, paul.hoffman@vpnc.org
  RFC6453          ||      F. Dijkstra, R. Hughes-Jones         ||       Freek.Dijkstra@sara.nl, Richard.Hughes-Jones@dante.net
  RFC6454          ||      A. Barth         ||       ietf@adambarth.com
  RFC6455          ||      I. Fette, A. Melnikov         ||       ifette+ietf@google.com, Alexey.Melnikov@isode.com
  RFC6456          ||      H. Li, R. Zheng, A. Farrel         ||       hongyu.lihongyu@huawei.com, robin@huawei.com, adrian@olddog.co.uk
  RFC6457          ||      T. Takeda, Ed., A. Farrel         ||       takeda.tomonori@lab.ntt.co.jp, adrian@olddog.co.uk
  RFC6458          ||      R. Stewart, M. Tuexen, K. Poon, P. Lei, V. Yasevich         ||       randall@lakerest.net, tuexen@fh-muenster.de, ka-cheong.poon@oracle.com, peterlei@cisco.com, vladislav.yasevich@hp.com
  RFC6459          ||      J. Korhonen, Ed., J. Soininen, B. Patil, T. Savolainen, G. Bajko, K. Iisakkila         ||       jouni.nospam@gmail.com, jonne.soininen@renesasmobile.com, basavaraj.patil@nokia.com, teemu.savolainen@nokia.com, gabor.bajko@nokia.com, kaisu.iisakkila@renesasmobile.com
  RFC6460          ||      M. Salter, R. Housley         ||       misalte@nsa.gov, housley@vigilsec.com
  RFC6461          ||      S. Channabasappa, Ed.         ||       sumanth@cablelabs.com
  RFC6462          ||      A. Cooper         ||       acooper@cdt.org
  RFC6463          ||      J. Korhonen, Ed., S. Gundavelli, H. Yokota, X. Cui         ||       jouni.nospam@gmail.com, sri.gundavelli@cisco.com, yokota@kddilabs.jp, Xiangsong.Cui@huawei.com
  RFC6464          ||      J. Lennox, Ed., E. Ivov, E. Marocco         ||       jonathan@vidyo.com, emcho@jitsi.org, enrico.marocco@telecomitalia.it
  RFC6465          ||      E. Ivov, Ed., E. Marocco, Ed., J. Lennox         ||       emcho@jitsi.org, enrico.marocco@telecomitalia.it, jonathan@vidyo.com
  RFC6466          ||      G. Salgueiro         ||       gsalguei@cisco.com
  RFC6467          ||      T. Kivinen         ||       kivinen@iki.fi
  RFC6468          ||      A. Melnikov, B. Leiba, K. Li         ||       Alexey.Melnikov@isode.com, barryleiba@computer.org, likepeng@huawei.com
  RFC6469          ||      K. Kobayashi, K. Mishima, S. Casner, C. Bormann         ||       ikob@riken.jp, three@sfc.wide.ad.jp, casner@acm.org, cabo@tzi.org
  RFC6470          ||      A. Bierman         ||       andy@yumaworks.com
  RFC6471          ||      C. Lewis, M. Sergeant         ||       clewisbcp@cauce.org, matt@sergeant.org
  RFC6472          ||      W. Kumari, K. Sriram         ||       warren@kumari.net, ksriram@nist.gov
  RFC6473          ||      P. Saint-Andre         ||       ietf@stpeter.im
  RFC6474          ||      K. Li, B. Leiba         ||       likepeng@huawei.com, barryleiba@computer.org
  RFC6475          ||      G. Keeni, K. Koide, S. Gundavelli, R. Wakikawa         ||       glenn@cysols.com, ka-koide@kddi.com, sgundave@cisco.com, ryuji@us.toyota-itc.com
  RFC6476          ||      P. Gutmann         ||       pgut001@cs.auckland.ac.nz
  RFC6477          ||      A. Melnikov, G. Lunt         ||       Alexey.Melnikov@isode.com, graeme.lunt@smhs.co.uk
  RFC6478          ||      L. Martini, G. Swallow, G. Heron, M. Bocci         ||       lmartini@cisco.com, swallow@cisco.com, giheron@cisco.com, matthew.bocci@alcatel-lucent.com
  RFC6479          ||      X. Zhang, T. Tsou         ||       xiangyang.zhang@huawei.com, tena@huawei.com
  RFC6480          ||      M. Lepinski, S. Kent         ||       mlepinski@bbn.com, kent@bbn.com
  RFC6481          ||      G. Huston, R. Loomans, G. Michaelson         ||       gih@apnic.net, robertl@apnic.net, ggm@apnic.net
  RFC6482          ||      M. Lepinski, S. Kent, D. Kong         ||       mlepinski@bbn.com, skent@bbn.com, dkong@bbn.com
  RFC6483          ||      G. Huston, G. Michaelson         ||       gih@apnic.net, ggm@apnic.net
  RFC6484          ||      S. Kent, D. Kong, K. Seo, R. Watro         ||       skent@bbn.com, dkong@bbn.com, kseo@bbn.com, rwatro@bbn.com
  RFC6485          ||      G. Huston         ||       gih@apnic.net
  RFC6486          ||      R. Austein, G. Huston, S. Kent, M. Lepinski         ||       sra@isc.org, gih@apnic.net, kent@bbn.com, mlepinski@bbn.com
  RFC6487          ||      G. Huston, G. Michaelson, R. Loomans         ||       gih@apnic.net, ggm@apnic.net, robertl@apnic.net
  RFC6488          ||      M. Lepinski, A. Chi, S. Kent         ||       mlepinski@bbn.com, achi@bbn.com, kent@bbn.com
  RFC6489          ||      G. Huston, G. Michaelson, S. Kent         ||       gih@apnic.net, ggm@apnic.net, kent@bbn.com
  RFC6490          ||      G. Huston, S. Weiler, G. Michaelson, S. Kent         ||       gih@apnic.net, weiler@sparta.com, ggm@apnic.net, kent@bbn.com
  RFC6491          ||      T. Manderson, L. Vegoda, S. Kent         ||       terry.manderson@icann.org, leo.vegoda@icann.org, kent@bbn.com
  RFC6492          ||      G. Huston, R. Loomans, B. Ellacott, R. Austein         ||       gih@apnic.net, robertl@apnic.net, bje@apnic.net, sra@hactrn.net
  RFC6493          ||      R. Bush         ||       randy@psg.com
  RFC6494          ||      R. Gagliano, S. Krishnan, A. Kukec         ||       rogaglia@cisco.com, suresh.krishnan@ericsson.com, ana.kukec@enterprisearchitects.com
  RFC6495          ||      R. Gagliano, S. Krishnan, A. Kukec         ||       rogaglia@cisco.com, suresh.krishnan@ericsson.com, ana.kukec@enterprisearchitects.com
  RFC6496          ||      S. Krishnan, J. Laganier, M. Bonola, A. Garcia-Martinez         ||       suresh.krishnan@ericsson.com, julien.ietf@gmail.com, marco.bonola@gmail.com, alberto@it.uc3m.es
  RFC6497          ||      M. Davis, A. Phillips, Y. Umaoka, C. Falk         ||       mark@macchiato.com, addison@lab126.com, yoshito_umaoka@us.ibm.com, court@infiauto.com
  RFC6498          ||      J. Stone, R. Kumar, F. Andreasen         ||       joestone@cisco.com, rkumar@cisco.com, fandreas@cisco.com
  RFC6501          ||      O. Novo, G. Camarillo, D. Morgan, J. Urpalainen         ||       Oscar.Novo@ericsson.com, Gonzalo.Camarillo@ericsson.com, Dave.Morgan@fmr.com, jari.urpalainen@nokia.com
  RFC6502          ||      G. Camarillo, S. Srinivasan, R. Even, J. Urpalainen         ||       Gonzalo.Camarillo@ericsson.com, srivatsa.srinivasan@gmail.com, ron.even.tlv@gmail.com, jari.urpalainen@nokia.com
  RFC6503          ||      M. Barnes, C. Boulton, S. Romano, H. Schulzrinne         ||       mary.ietf.barnes@gmail.com, chris@ns-technologies.com, spromano@unina.it, hgs+xcon@cs.columbia.edu
  RFC6504          ||      M. Barnes, L. Miniero, R. Presta, S P. Romano         ||       mary.ietf.barnes@gmail.com, lorenzo@meetecho.com, roberta.presta@unina.it, spromano@unina.it
  RFC6505          ||      S. McGlashan, T. Melanchuk, C. Boulton         ||       smcg.stds01@mcglashan.org, timm@rainwillow.com, chris@ns-technologies.com
  RFC6506          ||      M. Bhatia, V. Manral, A. Lindem         ||       manav.bhatia@alcatel-lucent.com, vishwas.manral@hp.com, acee.lindem@ericsson.com
  RFC6507          ||      M. Groves         ||       Michael.Groves@cesg.gsi.gov.uk
  RFC6508          ||      M. Groves         ||       Michael.Groves@cesg.gsi.gov.uk
  RFC6509          ||      M. Groves         ||       Michael.Groves@cesg.gsi.gov.uk
  RFC6510          ||      L. Berger, G. Swallow         ||       lberger@labn.net, swallow@cisco.com
  RFC6511          ||      Z. Ali, G. Swallow, R. Aggarwal         ||       zali@cisco.com, swallow@cisco.com, raggarwa_1@yahoo.com
  RFC6512          ||      IJ. Wijnands, E. Rosen, M. Napierala, N. Leymann         ||       ice@cisco.com, erosen@cisco.com, mnapierala@att.com, n.leymann@telekom.de
  RFC6513          ||      E. Rosen, Ed., R. Aggarwal, Ed.         ||       erosen@cisco.com, raggarwa_1@yahoo.com
  RFC6514          ||      R. Aggarwal, E. Rosen, T. Morin, Y. Rekhter         ||       raggarwa_1@yahoo.com, erosen@cisco.com, thomas.morin@orange-ftgroup.com, yakov@juniper.net
  RFC6515          ||      R. Aggarwal, E. Rosen         ||       raggarwa_1@yahoo.com, erosen@cisco.com
  RFC6516          ||      Y. Cai, E. Rosen, Ed., I. Wijnands         ||       ycai@cisco.com, erosen@cisco.com, ice@cisco.com
  RFC6517          ||      T. Morin, Ed., B. Niven-Jenkins, Ed., Y. Kamite, R. Zhang, N. Leymann, N. Bitar         ||       thomas.morin@orange.com, ben@niven-jenkins.co.uk, y.kamite@ntt.com, raymond.zhang@alcatel-lucent.com, n.leymann@telekom.de, nabil.n.bitar@verizon.com
  RFC6518          ||      G. Lebovitz, M. Bhatia         ||       gregory.ietf@gmail.com, manav.bhatia@alcatel-lucent.com
  RFC6519          ||      R. Maglione, A. Durand         ||       roberta.maglione@telecomitalia.it, adurand@juniper.net
  RFC6520          ||      R. Seggelmann, M. Tuexen, M. Williams         ||       seggelmann@fh-muenster.de, tuexen@fh-muenster.de, michael.glenn.williams@gmail.com
  RFC6521          ||      A. Makela, J. Korhonen         ||       antti.t.makela@iki.fi, jouni.nospam@gmail.com
  RFC6522          ||      M. Kucherawy, Ed.         ||       msk@cloudmark.com
  RFC6525          ||      R. Stewart, M. Tuexen, P. Lei         ||       randall@lakerest.net, tuexen@fh-muenster.de, peterlei@cisco.com
  RFC6526          ||      B. Claise, P. Aitken, A. Johnson, G. Muenz         ||       bclaise@cisco.com, paitken@cisco.com, andrjohn@cisco.com, muenz@net.in.tum.de
  RFC6527          ||      K. Tata         ||       tata_kalyan@yahoo.com
  RFC6528          ||      F. Gont, S. Bellovin         ||       fgont@si6networks.com, bellovin@acm.org
  RFC6529          ||      A. McKenzie, S. Crocker         ||       amckenzie3@yahoo.com, steve@stevecrocker.com
  RFC6530          ||      J. Klensin, Y. Ko         ||       john-ietf@jck.com, yangwooko@gmail.com
  RFC6531          ||      J. Yao, W. Mao         ||       yaojk@cnnic.cn, maowei_ietf@cnnic.cn
  RFC6532          ||      A. Yang, S. Steele, N. Freed         ||       abelyang@twnic.net.tw, Shawn.Steele@microsoft.com, ned+ietf@mrochek.com
  RFC6533          ||      T. Hansen, Ed., C. Newman, A. Melnikov         ||       tony+eaidsn@maillennium.att.com, chris.newman@oracle.com, Alexey.Melnikov@isode.com
  RFC6534          ||      N. Duffield, A. Morton, J. Sommers         ||       duffield@research.att.com, acmorton@att.com, jsommers@colgate.edu
  RFC6535          ||      B. Huang, H. Deng, T. Savolainen         ||       bill.huang@chinamobile.com, denghui@chinamobile.com, teemu.savolainen@nokia.com
  RFC6536          ||      A. Bierman, M. Bjorklund         ||       andy@yumaworks.com, mbj@tail-f.com
  RFC6537          ||      J. Ahrenholz         ||       jeffrey.m.ahrenholz@boeing.com
  RFC6538          ||      T. Henderson, A. Gurtov         ||       thomas.r.henderson@boeing.com, gurtov@ee.oulu.fi
  RFC6539          ||      V. Cakulev, G. Sundaram, I. Broustis         ||       violeta.cakulev@alcatel-lucent.com, ganesh.sundaram@alcatel-lucent.com, ioannis.broustis@alcatel-lucent.com
  RFC6540          ||      W. George, C. Donley, C. Liljenstolpe, L. Howard         ||       wesley.george@twcable.com, C.Donley@cablelabs.com, cdl@asgaard.org, lee.howard@twcable.com
  RFC6541          ||      M. Kucherawy         ||       msk@cloudmark.com
  RFC6542          ||      S. Emery         ||       shawn.emery@oracle.com
  RFC6543          ||      S. Gundavelli         ||       sgundave@cisco.com
  RFC6544          ||      J. Rosenberg, A. Keranen, B. B. Lowekamp, A. B. Roach         ||       jdrosen@jdrosen.net, ari.keranen@ericsson.com, bbl@lowekamp.net, adam@nostrum.com
  RFC6545          ||      K. Moriarty         ||       Kathleen.Moriarty@emc.com
  RFC6546          ||      B. Trammell         ||       trammell@tik.ee.ethz.ch
  RFC6547          ||      W. George         ||       wesley.george@twcable.com
  RFC6548          ||      N. Brownlee, Ed., IAB         ||       n.brownlee@auckland.ac.nz, iab@iab.org
  RFC6549          ||      A. Lindem, A. Roy, S. Mirtorabi         ||       acee.lindem@ericsson.com, akr@cisco.com, sina@cisco.com
  RFC6550          ||      T. Winter, Ed., P. Thubert, Ed., A. Brandt, J. Hui, R. Kelsey, P. Levis, K. Pister, R. Struik, JP. Vasseur, R. Alexander         ||       wintert@acm.org, pthubert@cisco.com, abr@sdesigns.dk, jhui@archrock.com, kelsey@ember.com, pal@cs.stanford.edu, kpister@dustnetworks.com, rstruik.ext@gmail.com, jpv@cisco.com, roger.alexander@cooperindustries.com
  RFC6551          ||      JP. Vasseur, Ed., M. Kim, Ed., K. Pister, N. Dejean, D. Barthel         ||       jpv@cisco.com, mjkim@kt.com, kpister@dustnetworks.com, nicolas.dejean@coronis.com, dominique.barthel@orange-ftgroup.com
  RFC6552          ||      P. Thubert, Ed.         ||       pthubert@cisco.com
  RFC6553          ||      J. Hui, JP. Vasseur         ||       jonhui@cisco.com, jpv@cisco.com
  RFC6554          ||      J. Hui, JP. Vasseur, D. Culler, V. Manral         ||       jonhui@cisco.com, jpv@cisco.com, culler@cs.berkeley.edu, vishwas.manral@hp.com
  RFC6555          ||      D. Wing, A. Yourtchenko         ||       dwing-ietf@fuggles.com, ayourtch@cisco.com
  RFC6556          ||      F. Baker         ||       fred@cisco.com
  RFC6557          ||      E. Lear, P. Eggert         ||       lear@cisco.com, eggert@cs.ucla.edu
  RFC6558          ||      A. Melnikov, B. Leiba, K. Li         ||       Alexey.Melnikov@isode.com, barryleiba@computer.org, likepeng@huawei.com
  RFC6559          ||      D. Farinacci, IJ. Wijnands, S. Venaas, M. Napierala         ||       dino@cisco.com, ice@cisco.com, stig@cisco.com, mnapierala@att.com
  RFC6560          ||      G. Richards         ||       gareth.richards@rsa.com
  RFC6561          ||      J. Livingood, N. Mody, M. O'Reirdan         ||       jason_livingood@cable.comcast.com, nirmal_mody@cable.comcast.com, michael_oreirdan@cable.comcast.com
  RFC6562          ||      C. Perkins, JM. Valin         ||       csp@csperkins.org, jmvalin@jmvalin.ca
  RFC6563          ||      S. Jiang, D. Conrad, B. Carpenter         ||       jiangsheng@huawei.com, drc@cloudflare.com, brian.e.carpenter@gmail.com
  RFC6564          ||      S. Krishnan, J. Woodyatt, E. Kline, J. Hoagland, M. Bhatia         ||       suresh.krishnan@ericsson.com, jhw@apple.com, ek@google.com, Jim_Hoagland@symantec.com, manav.bhatia@alcatel-lucent.com
  RFC6565          ||      P. Pillay-Esnault, P. Moyer, J. Doyle, E. Ertekin, M. Lundberg         ||       ppe@cisco.com, pete@pollere.net, jdoyle@doyleassociates.net, ertekin_emre@bah.com, lundberg_michael@bah.com
  RFC6566          ||      Y. Lee, Ed., G. Bernstein, Ed., D. Li, G. Martinelli         ||       leeyoung@huawei.com, gregb@grotto-networking.com, danli@huawei.com, giomarti@cisco.com
  RFC6567          ||      A. Johnston, L. Liess         ||       alan.b.johnston@gmail.com, laura.liess.dt@gmail.com
  RFC6568          ||      E. Kim, D. Kaspar, JP. Vasseur         ||       eunah.ietf@gmail.com, dokaspar.ietf@gmail.com, jpv@cisco.com
  RFC6569          ||      JM. Valin, S. Borilin, K. Vos, C. Montgomery, R. Chen         ||       jmvalin@jmvalin.ca, borilin@spiritdsp.net, koen.vos@skype.net, xiphmont@xiph.org, rchen@broadcom.com
  RFC6570          ||      J. Gregorio, R. Fielding, M. Hadley, M. Nottingham, D. Orchard         ||       joe@bitworking.org, fielding@gbiv.com, mhadley@mitre.org, mnot@mnot.net, orchard@pacificspirit.com
  RFC6571          ||      C. Filsfils, Ed., P. Francois, Ed., M. Shand, B. Decraene, J. Uttaro, N. Leymann, M. Horneffer         ||       cf@cisco.com, pierre.francois@imdea.org, imc.shand@googlemail.com, bruno.decraene@orange.com, uttaro@att.com, N.Leymann@telekom.de, Martin.Horneffer@telekom.de
  RFC6572          ||      F. Xia, B. Sarikaya, J. Korhonen, Ed., S. Gundavelli, D. Damic         ||       xiayangsong@huawei.com, sarikaya@ieee.org, jouni.nospam@gmail.com, sgundave@cisco.com, damjan.damic@siemens.com
  RFC6573          ||      M. Amundsen         ||       mca@amundsen.com
  RFC6574          ||      H. Tschofenig, J. Arkko         ||       Hannes.Tschofenig@gmx.net, jari.arkko@piuha.net
  RFC6575          ||      H. Shah, Ed., E. Rosen, Ed., G. Heron, Ed., V. Kompella, Ed.         ||       hshah@ciena.com, erosen@cisco.com, giheron@cisco.com, vach.kompella@alcatel-lucent.com
  RFC6576          ||      R. Geib, Ed., A. Morton, R. Fardid, A. Steinmitz         ||       Ruediger.Geib@telekom.de, acmorton@att.com, rfardid@cariden.com, Alexander.Steinmitz@telekom.de
  RFC6577          ||      M. Kucherawy         ||       msk@cloudmark.com
  RFC6578          ||      C. Daboo, A. Quillaud         ||       cyrus@daboo.name, arnaud.quillaud@oracle.com
  RFC6579          ||      M. Yevstifeyev         ||       evnikita2@gmail.com
  RFC6580          ||      M. Ko, D. Black         ||       mkosjc@gmail.com, david.black@emc.com
  RFC6581          ||      A. Kanevsky, Ed., C. Bestler, Ed., R. Sharp, S. Wise         ||       arkady.kanevsky@gmail.com, Caitlin.Bestler@nexenta.com, robert.o.sharp@intel.com, swise@opengridcomputing.com
  RFC6582          ||      T. Henderson, S. Floyd, A. Gurtov, Y. Nishida         ||       thomas.r.henderson@boeing.com, floyd@acm.org, gurtov@ee.oulu.fi, nishida@wide.ad.jp
  RFC6583          ||      I. Gashinsky, J. Jaeggli, W. Kumari         ||       igor@yahoo-inc.com, jjaeggli@zynga.com, warren@kumari.net
  RFC6584          ||      V. Roca         ||       vincent.roca@inria.fr
  RFC6585          ||      M. Nottingham, R. Fielding         ||       mnot@mnot.net, fielding@gbiv.com
  RFC6586          ||      J. Arkko, A. Keranen         ||       jari.arkko@piuha.net, ari.keranen@ericsson.com
  RFC6587          ||      R. Gerhards, C. Lonvick         ||       rgerhards@adiscon.com, clonvick@cisco.com
  RFC6588          ||      C. Ishikawa         ||       chiaki.ishikawa@ubin.jp
  RFC6589          ||      J. Livingood         ||       jason_livingood@cable.comcast.com
  RFC6590          ||      J. Falk, Ed., M. Kucherawy, Ed.         ||       ietf@cybernothing.org, msk@cloudmark.com
  RFC6591          ||      H. Fontana         ||       hilda@hfontana.com
  RFC6592          ||      C. Pignataro         ||       cpignata@cisco.com
  RFC6593          ||      C. Pignataro, J. Clarke, G. Salgueiro         ||       cpignata@cisco.com, jclarke@cisco.com, gsalguei@cisco.com
  RFC6594          ||      O. Sury         ||       ondrej.sury@nic.cz
  RFC6595          ||      K. Wierenga, E. Lear, S. Josefsson         ||       klaas@cisco.com, lear@cisco.com, simon@josefsson.org
  RFC6596          ||      M. Ohye, J. Kupke         ||       maileohye@gmail.com, joachim@kupke.za.net
  RFC6597          ||      J. Downs, Ed., J. Arbeiter, Ed.         ||       jeff_downs@partech.com, jimsgti@gmail.com
  RFC6598          ||      J. Weil, V. Kuarsingh, C. Donley, C. Liljenstolpe, M. Azinger         ||       jason.weil@twcable.com, victor.kuarsingh@gmail.com, c.donley@cablelabs.com, cdl@asgaard.org, marla.azinger@frontiercorp.com
  RFC6601          ||      G. Ash, Ed., D. McDysan         ||       gash5107@yahoo.com, dave.mcdysan@verizon.com
  RFC6602          ||      F. Abinader, Ed., S. Gundavelli, Ed., K. Leung, S. Krishnan, D. Premec         ||       fabinader@gmail.com, sgundave@cisco.com, kleung@cisco.com, suresh.krishnan@ericsson.com, domagoj.premec@gmail.com
  RFC6603          ||      J. Korhonen, Ed., T. Savolainen, S. Krishnan, O. Troan         ||       jouni.nospam@gmail.com, teemu.savolainen@nokia.com, suresh.krishnan@ericsson.com, ot@cisco.com
  RFC6604          ||      D. Eastlake 3rd         ||       d3e3e3@gmail.com
  RFC6605          ||      P. Hoffman, W.C.A. Wijngaards         ||       paul.hoffman@vpnc.org, wouter@nlnetlabs.nl
  RFC6606          ||      E. Kim, D. Kaspar, C. Gomez, C. Bormann         ||       eunah.ietf@gmail.com, dokaspar.ietf@gmail.com, carlesgo@entel.upc.edu, cabo@tzi.org
  RFC6607          ||      K. Kinnear, R. Johnson, M. Stapp         ||       kkinnear@cisco.com, raj@cisco.com, mjs@cisco.com
  RFC6608          ||      J. Dong, M. Chen, A. Suryanarayana         ||       jie.dong@huawei.com, mach.chen@huawei.com, asuryana@cisco.com
  RFC6609          ||      C. Daboo, A. Stone         ||       cyrus@daboo.name, aaron@serendipity.cx
  RFC6610          ||      H. Jang, A. Yegin, K. Chowdhury, J. Choi, T. Lemon         ||       heejin.jang@gmail.com, alper.yegin@yegin.org, kc@radiomobiles.com, jinchoe@gmail.com, Ted.Lemon@nominum.com
  RFC6611          ||      K. Chowdhury, Ed., A. Yegin         ||       kc@radiomobiles.com, alper.yegin@yegin.org
  RFC6612          ||      G. Giaretta, Ed.         ||       gerardog@qualcomm.com
  RFC6613          ||      A. DeKok         ||       aland@freeradius.org
  RFC6614          ||      S. Winter, M. McCauley, S. Venaas, K. Wierenga         ||       stefan.winter@restena.lu, mikem@open.com.au, stig@cisco.com, klaas@cisco.com
  RFC6615          ||      T. Dietz, Ed., A. Kobayashi, B. Claise, G. Muenz         ||       Thomas.Dietz@neclab.eu, akoba@nttv6.net, bclaise@cisco.com, muenz@net.in.tum.de
  RFC6616          ||      E. Lear, H. Tschofenig, H. Mauldin, S. Josefsson         ||       lear@cisco.com, Hannes.Tschofenig@gmx.net, hmauldin@cisco.com, simon@josefsson.org
  RFC6617          ||      D. Harkins         ||       dharkins@arubanetworks.com
  RFC6618          ||      J. Korhonen, Ed., B. Patil, H. Tschofenig, D. Kroeselberg         ||       jouni.nospam@gmail.com, basavaraj.patil@nokia.com, Hannes.Tschofenig@gmx.net, dirk.kroeselberg@siemens.com
  RFC6619          ||      J. Arkko, L. Eggert, M. Townsley         ||       jari.arkko@piuha.net, lars@netapp.com, townsley@cisco.com
  RFC6620          ||      E. Nordmark, M. Bagnulo, E. Levy-Abegnoli         ||       nordmark@acm.org, marcelo@it.uc3m.es, elevyabe@cisco.com
  RFC6621          ||      J. Macker, Ed.         ||       macker@itd.nrl.navy.mil
  RFC6622          ||      U. Herberg, T. Clausen         ||       ulrich@herberg.name, T.Clausen@computer.org
  RFC6623          ||      E. Burger         ||       eburger@standardstrack.com
  RFC6624          ||      K. Kompella, B. Kothari, R. Cherukuri         ||       kireeti@juniper.net, bhupesh@cisco.com, cherukuri@juniper.net
  RFC6625          ||      E. Rosen, Ed., Y. Rekhter, Ed., W. Hendrickx, R. Qiu         ||       erosen@cisco.com, yakov@juniper.net, wim.henderickx@alcatel-lucent.be, rayq@huawei.com
  RFC6626          ||      G. Tsirtsis, V. Park, V. Narayanan, K. Leung         ||       tsirtsis@googlemail.com, vpark@qualcomm.com, vidyan@qualcomm.com, kleung@cisco.com
  RFC6627          ||      G. Karagiannis, K. Chan, T. Moncaster, M. Menth, P. Eardley, B. Briscoe         ||       g.karagiannis@utwente.nl, khchan.work@gmail.com, Toby.Moncaster@cl.cam.ac.uk, menth@informatik.uni-tuebingen.de, philip.eardley@bt.com, bob.briscoe@bt.com
  RFC6628          ||      S. Shin, K. Kobara         ||       seonghan.shin@aist.go.jp, kobara_conf@m.aist.go.jp
  RFC6629          ||      J. Abley, M. Bagnulo, A. Garcia-Martinez         ||       joe.abley@icann.org, marcelo@it.uc3m.es, alberto@it.uc3m.es
  RFC6630          ||      Z. Cao, H. Deng, Q. Wu, G. Zorn, Ed.         ||       zehn.cao@gmail.com, denghui02@gmail.com, sunseawq@huawei.com, glenzorn@gmail.com
  RFC6631          ||      D. Kuegler, Y. Sheffer         ||       dennis.kuegler@bsi.bund.de, yaronf.ietf@gmail.com
  RFC6632          ||      M. Ersue, Ed., B. Claise         ||       mehmet.ersue@nsn.com, bclaise@cisco.com
  RFC6633          ||      F. Gont         ||       fgont@si6networks.com
  RFC6635          ||      O. Kolkman, Ed., J. Halpern, Ed., IAB         ||       olaf@nlnetlabs.nl, joel.halpern@ericsson.com, iab@iab.org
  RFC6636          ||      H. Asaeda, H. Liu, Q. Wu         ||       asaeda@wide.ad.jp, helen.liu@huawei.com, bill.wu@huawei.com
  RFC6637          ||      A. Jivsov         ||       Andrey_Jivsov@symantec.com
  RFC6638          ||      C. Daboo, B. Desruisseaux         ||       cyrus@daboo.name, bernard.desruisseaux@oracle.com
  RFC6639          ||      D. King, Ed., M. Venkatesan, Ed.         ||       daniel@olddog.co.uk, venkat.mahalingams@gmail.com
  RFC6640          ||      W. George         ||       wesley.george@twcable.com
  RFC6641          ||      C. Everhart, W. Adamson, J. Zhang         ||       everhart@netapp.com, andros@netapp.com, jiayingz@google.com
  RFC6642          ||      Q. Wu, Ed., F. Xia, R. Even         ||       sunseawq@huawei.com, xiayangsong@huawei.com, even.roni@huawei.com
  RFC6643          ||      J. Schoenwaelder         ||       j.schoenwaelder@jacobs-university.de
  RFC6644          ||      D. Evans, R. Droms, S. Jiang         ||       N7DR@ipfonix.com, rdroms@cisco.com, jiangsheng@huawei.com
  RFC6645          ||      J. Novak         ||       janovak@cisco.com
  RFC6646          ||      H. Song, N. Zong, Y. Yang, R. Alimi         ||       haibin.song@huawei.com, zongning@huawei.com, yry@cs.yale.edu, ralimi@google.com
  RFC6647          ||      M. Kucherawy, D. Crocker         ||       superuser@gmail.com, dcrocker@bbiw.net
  RFC6648          ||      P. Saint-Andre, D. Crocker, M. Nottingham         ||       ietf@stpeter.im, dcrocker@bbiw.net, mnot@mnot.net
  RFC6649          ||      L. Hornquist Astrand, T. Yu         ||       lha@apple.com, tlyu@mit.edu
  RFC6650          ||      J. Falk, M. Kucherawy, Ed.         ||       none, superuser@gmail.com
  RFC6651          ||      M. Kucherawy         ||       superuser@gmail.com
  RFC6652          ||      S. Kitterman         ||       scott@kitterman.com
  RFC6653          ||      B. Sarikaya, F. Xia, T. Lemon         ||       sarikaya@ieee.org, xiayangsong@huawei.com, mellon@nominum.com
  RFC6654          ||      T. Tsou, C. Zhou, T. Taylor, Q. Chen         ||       Tina.Tsou.Zouting@huawei.com, cathy.zhou@huawei.com, tom.taylor.stds@gmail.com, chenqi.0819@gmail.com
  RFC6655          ||      D. McGrew, D. Bailey         ||       mcgrew@cisco.com, dbailey@rsa.com
  RFC6656          ||      R. Johnson, K. Kinnear, M. Stapp         ||       raj@cisco.com, kkinnear@cisco.com, mjs@cisco.com
  RFC6657          ||      A. Melnikov, J. Reschke         ||       Alexey.Melnikov@isode.com, julian.reschke@greenbytes.de
  RFC6658          ||      S. Bryant, Ed., L. Martini, G. Swallow, A. Malis         ||       stbryant@cisco.com, lmartini@cisco.com, swallow@cisco.com, andrew.g.malis@verizon.com
  RFC6659          ||      A. Begen         ||       abegen@cisco.com
  RFC6660          ||      B. Briscoe, T. Moncaster, M. Menth         ||       bob.briscoe@bt.com, toby.moncaster@cl.cam.ac.uk, menth@uni-tuebingen.de
  RFC6661          ||      A. Charny, F. Huang, G. Karagiannis, M. Menth, T. Taylor, Ed.         ||       anna@mwsm.com, huangfuqing@huawei.com, g.karagiannis@utwente.nl, menth@uni-tuebingen.de, tom.taylor.stds@gmail.com
  RFC6662          ||      A. Charny, J. Zhang, G. Karagiannis, M. Menth, T. Taylor, Ed.         ||       anna@mwsm.com, joyzhang@cisco.com, g.karagiannis@utwente.nl, menth@uni-tuebingen.de, tom.taylor.stds@gmail.com
  RFC6663          ||      G. Karagiannis, T. Taylor, K. Chan, M. Menth, P. Eardley         ||       g.karagiannis@utwente.nl, tom.taylor.stds@gmail.com, khchan.work@gmail.com, menth@uni-tuebingen.de, philip.eardley@bt.com
  RFC6664          ||      J. Schaad         ||       ietf@augustcellars.com
  RFC6665          ||      A.B. Roach         ||       adam@nostrum.com
  RFC6666          ||      N. Hilliard, D. Freedman         ||       nick@inex.ie, david.freedman@uk.clara.net
  RFC6667          ||      K. Raza, S. Boutros, C. Pignataro         ||       skraza@cisco.com, sboutros@cisco.com, cpignata@cisco.com
  RFC6668          ||      D. Bider, M. Baushke         ||       ietf-ssh2@denisbider.com, mdb@juniper.net
  RFC6669          ||      N. Sprecher, L. Fang         ||       nurit.sprecher@nsn.com, lufang@cisco.com
  RFC6670          ||      N. Sprecher, KY. Hong         ||       nurit.sprecher@nsn.com, hongk@cisco.com
  RFC6671          ||      M. Betts         ||       malcolm.betts@zte.com.cn
  RFC6672          ||      S. Rose, W. Wijngaards         ||       scott.rose@nist.gov, wouter@nlnetlabs.nl
  RFC6673          ||      A. Morton         ||       acmorton@att.com
  RFC6674          ||      F. Brockners, S. Gundavelli, S. Speicher, D. Ward         ||       fbrockne@cisco.com, sgundave@cisco.com, sebastian.speicher@telekom.de, wardd@cisco.com
  RFC6675          ||      E. Blanton, M. Allman, L. Wang, I. Jarvinen, M. Kojo, Y. Nishida         ||       elb@psg.com, mallman@icir.org, liliw@juniper.net, ilpo.jarvinen@helsinki.fi, kojo@cs.helsinki.fi, nishida@wide.ad.jp
  RFC6676          ||      S. Venaas, R. Parekh, G. Van de Velde, T. Chown, M. Eubanks         ||       stig@cisco.com, riparekh@cisco.com, gvandeve@cisco.com, tjc@ecs.soton.ac.uk, marshall.eubanks@iformata.com
  RFC6677          ||      S. Hartman, Ed., T. Clancy, K. Hoeper         ||       hartmans-ietf@mit.edu, tcc@vt.edu, khoeper@motorolasolutions.com
  RFC6678          ||      K. Hoeper, S. Hanna, H. Zhou, J. Salowey, Ed.         ||       khoeper@motorolasolutions.com, shanna@juniper.net, hzhou@cisco.com, jsalowey@cisco.com
  RFC6679          ||      M. Westerlund, I. Johansson, C. Perkins, P. O'Hanlon, K. Carlberg         ||       magnus.westerlund@ericsson.com, ingemar.s.johansson@ericsson.com, csp@csperkins.org, piers.ohanlon@oii.ox.ac.uk, carlberg@g11.org.uk
  RFC6680          ||      N. Williams, L. Johansson, S. Hartman, S. Josefsson         ||       nico@cryptonector.com, leifj@sunet.se, hartmans-ietf@mit.edu, simon@josefsson.org
  RFC6681          ||      M. Watson, T. Stockhammer, M. Luby         ||       watsonm@netflix.com, stockhammer@nomor.de, luby@qti.qualcomm.com
  RFC6682          ||      M. Watson, T. Stockhammer, M. Luby         ||       watsonm@netflix.com, stockhammer@nomor.de, luby@qti.qualcomm.com
  RFC6683          ||      A. Begen, T. Stockhammer         ||       abegen@cisco.com, stockhammer@nomor.de
  RFC6684          ||      B. Trammell         ||       trammell@tik.ee.ethz.ch
  RFC6685          ||      B. Trammell         ||       trammell@tik.ee.ethz.ch
  RFC6686          ||      M. Kucherawy         ||       superuser@gmail.com
  RFC6687          ||      J. Tripathi, Ed., J. de Oliveira, Ed., JP. Vasseur, Ed.         ||       jt369@drexel.edu, jau@coe.drexel.edu, jpv@cisco.com
  RFC6688          ||      D. Black, Ed., J. Glasgow, S. Faibish         ||       david.black@emc.com, jglasgow@google.com, sfaibish@emc.com
  RFC6689          ||      L. Berger         ||       lberger@labn.net
  RFC6690          ||      Z. Shelby         ||       zach@sensinode.com
  RFC6691          ||      D. Borman         ||       david.borman@quantum.com
  RFC6692          ||      R. Clayton, M. Kucherawy         ||       richard.clayton@cl.cam.ac.uk, superuser@gmail.com
  RFC6693          ||      A. Lindgren, A. Doria, E. Davies, S. Grasic         ||       andersl@sics.se, avri@acm.org, elwynd@folly.org.uk, samo.grasic@ltu.se
  RFC6694          ||      S. Moonesamy, Ed.         ||       sm+ietf@elandsys.com
  RFC6695          ||      R. Asati         ||       rajiva@cisco.com
  RFC6696          ||      Z. Cao, B. He, Y. Shi, Q. Wu, Ed., G. Zorn, Ed.         ||       caozhen@chinamobile.com, hebaohong@catr.cn, shiyang1@huawei.com, bill.wu@huawei.com, glenzorn@gmail.com
  RFC6697          ||      G. Zorn, Ed., Q. Wu, T. Taylor, Y. Nir, K. Hoeper, S. Decugis         ||       glenzorn@gmail.com, bill.wu@huawei.com, tom.taylor.stds@gmail.com, ynir@checkpoint.com, khoeper@motorolasolutions.com, sdecugis@freediameter.net
  RFC6698          ||      P. Hoffman, J. Schlyter         ||       paul.hoffman@vpnc.org, jakob@kirei.se
  RFC6701          ||      A. Farrel, P. Resnick         ||       adrian@olddog.co.uk, presnick@qti.qualcomm.com
  RFC6702          ||      T. Polk, P. Saint-Andre         ||       tim.polk@nist.gov, ietf@stpeter.im
  RFC6703          ||      A. Morton, G. Ramachandran, G. Maguluri         ||       acmorton@att.com, gomathi@att.com, gmaguluri@att.com
  RFC6704          ||      D. Miles, W. Dec, J. Bristow, R. Maglione         ||       davidmiles@google.com, wdec@cisco.com, James.Bristow@swisscom.com, roberta.maglione@telecomitalia.it
  RFC6705          ||      S. Krishnan, R. Koodli, P. Loureiro, Q. Wu, A. Dutta         ||       suresh.krishnan@ericsson.com, rkoodli@cisco.com, loureiro@neclab.eu, Sunseawq@huawei.com, adutta@niksun.com
  RFC6706          ||      F. Templin, Ed.         ||       fltemplin@acm.org
  RFC6707          ||      B. Niven-Jenkins, F. Le Faucheur, N. Bitar         ||       ben@velocix.com, flefauch@cisco.com, nabil.n.bitar@verizon.com
  RFC6708          ||      S. Kiesel, Ed., S. Previdi, M. Stiemerling, R. Woundy, Y. Yang         ||       ietf-alto@skiesel.de, sprevidi@cisco.com, martin.stiemerling@neclab.eu, Richard_Woundy@cable.comcast.com, yry@cs.yale.edu
  RFC6709          ||      B. Carpenter, B. Aboba, Ed., S. Cheshire         ||       brian.e.carpenter@gmail.com, bernard_aboba@hotmail.com, cheshire@apple.com
  RFC6710          ||      A. Melnikov, K. Carlberg         ||       Alexey.Melnikov@isode.com, carlberg@g11.org.uk
  RFC6711          ||      L. Johansson         ||       leifj@nordu.net
  RFC6712          ||      T. Kause, M. Peylo         ||       toka@ssh.com, martin.peylo@nsn.com
  RFC6713          ||      J. Levine         ||       standards@taugh.com
  RFC6714          ||      C. Holmberg, S. Blau, E. Burger         ||       christer.holmberg@ericsson.com, staffan.blau@ericsson.com, eburger@standardstrack.com
  RFC6715          ||      D. Cauchie, B. Leiba, K. Li         ||       dany.cauchie@orange.com, barryleiba@computer.org, likepeng@huawei.com
  RFC6716          ||      JM. Valin, K. Vos, T. Terriberry         ||       jmvalin@jmvalin.ca, koenvos74@gmail.com, tterriberry@mozilla.com
  RFC6717          ||      H. Hotz, R. Allbery         ||       hotz@jpl.nasa.gov, rra@stanford.edu
  RFC6718          ||      P. Muley, M. Aissaoui, M. Bocci         ||       praveen.muley@alcatel-lucent.com, mustapha.aissaoui@alcatel-lucent.com, matthew.bocci@alcatel-lucent.com
  RFC6719          ||      O. Gnawali, P. Levis         ||       gnawali@cs.uh.edu, pal@cs.stanford.edu
  RFC6720          ||      C. Pignataro, R. Asati         ||       cpignata@cisco.com, rajiva@cisco.com
  RFC6721          ||      J. Snell         ||       jasnell@us.ibm.com
  RFC6722          ||      P. Hoffman, Ed.         ||       paul.hoffman@vpnc.org
  RFC6723          ||      L. Jin, Ed., R. Key, Ed., S. Delord, T. Nadeau, S. Boutros         ||       lizhong.jin@zte.com.cn, raymond.key@ieee.org, simon.delord@gmail.com, tnadeau@juniper.net, sboutros@cisco.com
  RFC6724          ||      D. Thaler, Ed., R. Draves, A. Matsumoto, T. Chown         ||       dthaler@microsoft.com, richdr@microsoft.com, arifumi@nttv6.net, tjc@ecs.soton.ac.uk
  RFC6725          ||      S. Rose         ||       scottr.nist@gmail.com
  RFC6726          ||      T. Paila, R. Walsh, M. Luby, V. Roca, R. Lehtonen         ||       toni.paila@gmail.com, roderick.walsh@tut.fi, luby@qti.qualcomm.com, vincent.roca@inria.fr, rami.lehtonen@teliasonera.com
  RFC6727          ||      T. Dietz, Ed., B. Claise, J. Quittek         ||       dietz@neclab.eu, bclaise@cisco.com, quittek@neclab.eu
  RFC6728          ||      G. Muenz, B. Claise, P. Aitken         ||       muenz@net.in.tum.de, bclaise@cisco.com, paitken@cisco.com
  RFC6729          ||      D. Crocker, M. Kucherawy         ||       dcrocker@bbiw.net, superuser@gmail.com
  RFC6730          ||      S. Krishnan, J. Halpern         ||       suresh.krishnan@ericsson.com, joel.halpern@ericsson.com
  RFC6731          ||      T. Savolainen, J. Kato, T. Lemon         ||       teemu.savolainen@nokia.com, kato@syce.net, Ted.Lemon@nominum.com
  RFC6732          ||      V. Kuarsingh, Ed., Y. Lee, O. Vautrin         ||       victor.kuarsingh@gmail.com, yiu_lee@cable.comcast.com, olivier@juniper.net
  RFC6733          ||      V. Fajardo, Ed., J. Arkko, J. Loughney, G. Zorn, Ed.         ||       vf0213@gmail.com, jari.arkko@ericsson.com, john.loughney@nokia.com, glenzorn@gmail.com
  RFC6734          ||      G. Zorn, Q. Wu, V. Cakulev         ||       glenzorn@gmail.com, sunseawq@huawei.com, violeta.cakulev@alcatel-lucent.com
  RFC6735          ||      K. Carlberg, Ed., T. Taylor         ||       carlberg@g11.org.uk, tom.taylor.stds@gmail.com
  RFC6736          ||      F. Brockners, S. Bhandari, V. Singh, V. Fajardo         ||       fbrockne@cisco.com, shwethab@cisco.com, vaneeta.singh@gmail.com, vf0213@gmail.com
  RFC6737          ||      K. Jiao, G. Zorn         ||       kangjiao@huawei.com, gwz@net-zen.net
  RFC6738          ||      V. Cakulev, A. Lior, S. Mizikovsky         ||       violeta.cakulev@alcatel-lucent.com, avi.ietf@lior.org, Simon.Mizikovsky@alcatel-lucent.com
  RFC6739          ||      H. Schulzrinne, H. Tschofenig         ||       hgs+ecrit@cs.columbia.edu, Hannes.Tschofenig@gmx.net
  RFC6740          ||      RJ Atkinson, SN Bhatti         ||       rja.lists@gmail.com, saleem@cs.st-andrews.ac.uk
  RFC6741          ||      RJ Atkinson, SN Bhatti         ||       rja.lists@gmail.com, saleem@cs.st-andrews.ac.uk
  RFC6742          ||      RJ Atkinson, SN Bhatti, S. Rose         ||       rja.lists@gmail.com, saleem@cs.st-andrews.ac.uk, scottr.nist@gmail.com
  RFC6743          ||      RJ Atkinson, SN Bhatti         ||       rja.lists@gmail.com, saleem@cs.st-andrews.ac.uk
  RFC6744          ||      RJ Atkinson, SN Bhatti         ||       rja.lists@gmail.com, saleem@cs.st-andrews.ac.uk
  RFC6745          ||      RJ Atkinson, SN Bhatti         ||       rja.lists@gmail.com, saleem@cs.st-andrews.ac.uk
  RFC6746          ||      RJ Atkinson, SN Bhatti         ||       rja.lists@gmail.com, saleem@cs.st-andrews.ac.uk
  RFC6747          ||      RJ Atkinson, SN Bhatti         ||       rja.lists@gmail.com, saleem@cs.st-andrews.ac.uk
  RFC6748          ||      RJ Atkinson, SN Bhatti         ||       rja.lists@gmail.com, saleem@cs.st-andrews.ac.uk
  RFC6749          ||      D. Hardt, Ed.         ||       dick.hardt@gmail.com
  RFC6750          ||      M. Jones, D. Hardt         ||       mbj@microsoft.com, dick.hardt@gmail.com
  RFC6751          ||      R. Despres, Ed., B. Carpenter, D. Wing, S. Jiang         ||       despres.remi@laposte.net, brian.e.carpenter@gmail.com, dwing-ietf@fuggles.com, shengjiang@huawei.com
  RFC6752          ||      A. Kirkham         ||       tkirkham@paloaltonetworks.com
  RFC6753          ||      J. Winterbottom, H. Tschofenig, H. Schulzrinne, M. Thomson         ||       james.winterbottom@commscope.com, Hannes.Tschofenig@gmx.net, hgs@cs.columbia.edu, martin.thomson@skype.net
  RFC6754          ||      Y. Cai, L. Wei, H. Ou, V. Arya, S. Jethwani         ||       yiqunc@microsoft.com, lwei@cisco.com, hou@cisco.com, varya@directv.com, sjethwani@directv.com
  RFC6755          ||      B. Campbell, H. Tschofenig         ||       brian.d.campbell@gmail.com, hannes.tschofenig@gmx.net
  RFC6756          ||      S. Trowbridge, Ed., E. Lear, Ed., G. Fishman, Ed., S. Bradner, Ed.         ||       steve.trowbridge@alcatel-lucent.com, lear@cisco.com, gryfishman@aol.com, sob@harvard.edu
  RFC6757          ||      S. Gundavelli, Ed., J. Korhonen, Ed., M. Grayson, K. Leung, R. Pazhyannur         ||       sgundave@cisco.com, jouni.nospam@gmail.com, mgrayson@cisco.com, kleung@cisco.com, rpazhyan@cisco.com
  RFC6758          ||      A. Melnikov, K. Carlberg         ||       Alexey.Melnikov@isode.com, carlberg@g11.org.uk
  RFC6759          ||      B. Claise, P. Aitken, N. Ben-Dvora         ||       bclaise@cisco.com, paitken@cisco.com, nirbd@cisco.com
  RFC6760          ||      S. Cheshire, M. Krochmal         ||       cheshire@apple.com, marc@apple.com
  RFC6761          ||      S. Cheshire, M. Krochmal         ||       cheshire@apple.com, marc@apple.com
  RFC6762          ||      S. Cheshire, M. Krochmal         ||       cheshire@apple.com, marc@apple.com
  RFC6763          ||      S. Cheshire, M. Krochmal         ||       cheshire@apple.com, marc@apple.com
  RFC6764          ||      C. Daboo         ||       cyrus@daboo.name
  RFC6765          ||      E. Beili, M. Morgenstern         ||       edward.beili@actelis.com, moti.morgenstern@ecitele.com
  RFC6766          ||      E. Beili         ||       edward.beili@actelis.com
  RFC6767          ||      E. Beili, M. Morgenstern         ||       edward.beili@actelis.com, moti.morgenstern@ecitele.com
  RFC6768          ||      E. Beili         ||       edward.beili@actelis.com
  RFC6769          ||      R. Raszuk, J. Heitz, A. Lo, L. Zhang, X. Xu         ||       robert@raszuk.net, jakob.heitz@ericsson.com, altonlo@aristanetworks.com, lixia@cs.ucla.edu, xuxh@huawei.com
  RFC6770          ||      G. Bertrand, Ed., E. Stephan, T. Burbridge, P. Eardley, K. Ma, G. Watson         ||       gilles.bertrand@orange.com, emile.stephan@orange.com, trevor.burbridge@bt.com, philip.eardley@bt.com, kevin.ma@azukisystems.com, gwatson@velocix.com
  RFC6771          ||      L. Eggert, G. Camarillo         ||       lars@netapp.com, Gonzalo.Camarillo@ericsson.com
  RFC6772          ||      H. Schulzrinne, Ed., H. Tschofenig, Ed., J. Cuellar, J. Polk, J. Morris, M. Thomson         ||       schulzrinne@cs.columbia.edu, Hannes.Tschofenig@gmx.net, Jorge.Cuellar@siemens.com, jmpolk@cisco.com, ietf@jmorris.org, martin.thomson@gmail.com
  RFC6773          ||      T. Phelan, G. Fairhurst, C. Perkins         ||       tphelan@sonusnet.com, gorry@erg.abdn.ac.uk, csp@csperkins.org
  RFC6774          ||      R. Raszuk, Ed., R. Fernando, K. Patel, D. McPherson, K. Kumaki         ||       robert@raszuk.net, rex@cisco.com, keyupate@cisco.com, dmcpherson@verisign.com, ke-kumaki@kddi.com
  RFC6775          ||      Z. Shelby, Ed., S. Chakrabarti, E. Nordmark, C. Bormann         ||       zach@sensinode.com, samita.chakrabarti@ericsson.com, nordmark@cisco.com, cabo@tzi.org
  RFC6776          ||      A. Clark, Q. Wu         ||       alan.d.clark@telchemy.com, sunseawq@huawei.com
  RFC6777          ||      W. Sun, Ed., G. Zhang, Ed., J. Gao, G. Xie, R. Papneja         ||       sun.weiqiang@gmail.com, zhangguoying@catr.cn, gjhhit@huawei.com, xieg@cs.ucr.edu, rajiv.papneja@huawei.com
  RFC6778          ||      R. Sparks         ||       RjS@nostrum.com
  RFC6779          ||      U. Herberg, R. Cole, I. Chakeres         ||       ulrich@herberg.name, robert.g.cole@us.army.mil, ian.chakeres@gmail.com
  RFC6780          ||      L. Berger, F. Le Faucheur, A. Narayanan         ||       lberger@labn.net, flefauch@cisco.com, ashokn@cisco.com
  RFC6781          ||      O. Kolkman, W. Mekking, R. Gieben         ||       olaf@nlnetlabs.nl, matthijs@nlnetlabs.nl, miek.gieben@sidn.nl
  RFC6782          ||      V. Kuarsingh, Ed., L. Howard         ||       victor.kuarsingh@gmail.com, lee.howard@twcable.com
  RFC6783          ||      J. Levine, R. Gellens         ||       standards@taugh.com, rg+ietf@qti.qualcomm.com
  RFC6784          ||      S. Sakane, M. Ishiyama         ||       ssakane@cisco.com, masahiro.ishiyama@toshiba.co.jp
  RFC6785          ||      B. Leiba         ||       barryleiba@computer.org
  RFC6786          ||      A. Yegin, R. Cragie         ||       alper.yegin@yegin.org, robert.cragie@gridmerge.com
  RFC6787          ||      D. Burnett, S. Shanmugham         ||       dburnett@voxeo.com, sarvi@cisco.com
  RFC6788          ||      S. Krishnan, A. Kavanagh, B. Varga, S. Ooghe, E. Nordmark         ||       suresh.krishnan@ericsson.com, alan.kavanagh@ericsson.com, balazs.a.varga@ericsson.com, sven.ooghe@alcatel-lucent.com, nordmark@cisco.com
  RFC6789          ||      B. Briscoe, Ed., R. Woundy, Ed., A. Cooper, Ed.         ||       bob.briscoe@bt.com, richard_woundy@cable.comcast.com, acooper@cdt.org
  RFC6790          ||      K. Kompella, J. Drake, S. Amante, W. Henderickx, L. Yong         ||       kireeti.kompella@gmail.com, jdrake@juniper.net, shane@level3.net, wim.henderickx@alcatel-lucent.com, lucy.yong@huawei.com
  RFC6791          ||      X. Li, C. Bao, D. Wing, R. Vaithianathan, G. Huston         ||       xing@cernet.edu.cn, congxiao@cernet.edu.cn, dwing-ietf@fuggles.com, rvaithia@cisco.com, gih@apnic.net
  RFC6792          ||      Q. Wu, Ed., G. Hunt, P. Arden         ||       sunseawq@huawei.com, r.geoff.hunt@gmail.com, philip.arden@bt.com
  RFC6793          ||      Q. Vohra, E. Chen         ||       quaizar.vohra@gmail.com, enkechen@cisco.com
  RFC6794          ||      V. Hilt, G. Camarillo, J. Rosenberg         ||       volker.hilt@bell-labs.com, Gonzalo.Camarillo@ericsson.com, jdrosen@jdrosen.net
  RFC6795          ||      V. Hilt, G. Camarillo         ||       volker.hilt@bell-labs.com, Gonzalo.Camarillo@ericsson.com
  RFC6796          ||      V. Hilt, G. Camarillo, J. Rosenberg, D. Worley         ||       volker.hilt@bell-labs.com, Gonzalo.Camarillo@ericsson.com, jdrosen@jdrosen.net, worley@ariadne.com
  RFC6797          ||      J. Hodges, C. Jackson, A. Barth         ||       Jeff.Hodges@PayPal.com, collin.jackson@sv.cmu.edu, ietf@adambarth.com
  RFC6798          ||      A. Clark, Q. Wu         ||       alan.d.clark@telchemy.com, sunseawq@huawei.com
  RFC6801          ||      U. Kozat, A. Begen         ||       kozat@docomolabs-usa.com, abegen@cisco.com
  RFC6802          ||      S. Baillargeon, C. Flinta, A. Johnsson         ||       steve.baillargeon@ericsson.com, christofer.flinta@ericsson.com, andreas.a.johnsson@ericsson.com
  RFC6803          ||      G. Hudson         ||       ghudson@mit.edu
  RFC6804          ||      B. Manning         ||       bmanning@sfc.keio.ac.jp
  RFC6805          ||      D. King, Ed., A. Farrel, Ed.         ||       daniel@olddog.co.uk, adrian@olddog.co.uk
  RFC6806          ||      S. Hartman, Ed., K. Raeburn, L. Zhu         ||       hartmans-ietf@mit.edu, raeburn@mit.edu, lzhu@microsoft.com
  RFC6807          ||      D. Farinacci, G. Shepherd, S. Venaas, Y. Cai         ||       dino@cisco.com, gjshep@gmail.com, stig@cisco.com, yiqunc@microsoft.com
  RFC6808          ||      L. Ciavattone, R. Geib, A. Morton, M. Wieser         ||       lencia@att.com, Ruediger.Geib@telekom.de, acmorton@att.com, matthias_michael.wieser@stud.tu-darmstadt.de
  RFC6809          ||      C. Holmberg, I. Sedlacek, H. Kaplan         ||       christer.holmberg@ericsson.com, ivo.sedlacek@ericsson.com, hkaplan@acmepacket.com
  RFC6810          ||      R. Bush, R. Austein         ||       randy@psg.com, sra@hactrn.net
  RFC6811          ||      P. Mohapatra, J. Scudder, D. Ward, R. Bush, R. Austein         ||       pmohapat@cisco.com, jgs@juniper.net, dward@cisco.com, randy@psg.com, sra@hactrn.net
  RFC6812          ||      M. Chiba, A. Clemm, S. Medley, J. Salowey, S. Thombare, E. Yedavalli         ||       mchiba@cisco.com, alex@cisco.com, stmedley@cisco.com, jsalowey@cisco.com, thombare@cisco.com, eshwar@cisco.com
  RFC6813          ||      J. Salowey, S. Hanna         ||       jsalowey@cisco.com, shanna@juniper.net
  RFC6814          ||      C. Pignataro, F. Gont         ||       cpignata@cisco.com, fgont@si6networks.com
  RFC6815          ||      S. Bradner, K. Dubray, J. McQuaid, A. Morton         ||       sob@harvard.edu, kdubray@juniper.net, jim@turnipvideo.com, acmorton@att.com
  RFC6816          ||      V. Roca, M. Cunche, J. Lacan         ||       vincent.roca@inria.fr, mathieu.cunche@inria.fr, jerome.lacan@isae.fr
  RFC6817          ||      S. Shalunov, G. Hazel, J. Iyengar, M. Kuehlewind         ||       shalunov@shlang.com, greg@bittorrent.com, jiyengar@fandm.edu, mirja.kuehlewind@ikr.uni-stuttgart.de
  RFC6818          ||      P. Yee         ||       peter@akayla.com
  RFC6819          ||      T. Lodderstedt, Ed., M. McGloin, P. Hunt         ||       torsten@lodderstedt.net, mark.mcgloin@ie.ibm.com, phil.hunt@yahoo.com
  RFC6820          ||      T. Narten, M. Karir, I. Foo         ||       narten@us.ibm.com, mkarir@merit.edu, Ian.Foo@huawei.com
  RFC6821          ||      E. Marocco, A. Fusco, I. Rimac, V. Gurbani         ||       enrico.marocco@telecomitalia.it, antonio2.fusco@telecomitalia.it, rimac@bell-labs.com, vkg@bell-labs.com
  RFC6822          ||      S. Previdi, Ed., L. Ginsberg, M. Shand, A. Roy, D. Ward         ||       sprevidi@cisco.com, ginsberg@cisco.com, imc.shand@gmail.com, akr@cisco.com, wardd@cisco.com
  RFC6823          ||      L. Ginsberg, S. Previdi, M. Shand         ||       ginsberg@cisco.com, sprevidi@cisco.com, imc.shand@gmail.com
  RFC6824          ||      A. Ford, C. Raiciu, M. Handley, O. Bonaventure         ||       alanford@cisco.com, costin.raiciu@cs.pub.ro, m.handley@cs.ucl.ac.uk, olivier.bonaventure@uclouvain.be
  RFC6825          ||      M. Miyazawa, T. Otani, K. Kumaki, T. Nadeau         ||       ma-miyazawa@kddilabs.jp, Tm-otani@kddi.com, ke-kumaki@kddi.com, tnadeau@juniper.net
  RFC6826          ||      IJ. Wijnands, Ed., T. Eckert, N. Leymann, M. Napierala         ||       ice@cisco.com, eckert@cisco.com, n.leymann@telekom.de, mnapierala@att.com
  RFC6827          ||      A. Malis, Ed., A. Lindem, Ed., D. Papadimitriou, Ed.         ||       andrew.g.malis@verizon.com, acee.lindem@ericsson.com, dimitri.papadimitriou@alcatel-lucent.com
  RFC6828          ||      J. Xia         ||       xiajinwei@huawei.com
  RFC6829          ||      M. Chen, P. Pan, C. Pignataro, R. Asati         ||       mach@huawei.com, ppan@infinera.com, cpignata@cisco.com, rajiva@cisco.com
  RFC6830          ||      D. Farinacci, V. Fuller, D. Meyer, D. Lewis         ||       farinacci@gmail.com, vaf@vaf.net, dmm@1-4-5.net, darlewis@cisco.com
  RFC6831          ||      D. Farinacci, D. Meyer, J. Zwiebel, S. Venaas         ||       farinacci@gmail.com, dmm@cisco.com, jzwiebel@cruzio.com, stig@cisco.com
  RFC6832          ||      D. Lewis, D. Meyer, D. Farinacci, V. Fuller         ||       darlewis@cisco.com, dmm@1-4-5.net, farinacci@gmail.com, vaf@vaf.net
  RFC6833          ||      V. Fuller, D. Farinacci         ||       vaf@vaf.net, farinacci@gmail.com
  RFC6834          ||      L. Iannone, D. Saucez, O. Bonaventure         ||       luigi.iannone@telecom-paristech.fr, damien.saucez@inria.fr, olivier.bonaventure@uclouvain.be
  RFC6835          ||      D. Farinacci, D. Meyer         ||       farinacci@gmail.com, dmm@cisco.com
  RFC6836          ||      V. Fuller, D. Farinacci, D. Meyer, D. Lewis         ||       vaf@vaf.net, farinacci@gmail.com, dmm@1-4-5.net, darlewis@cisco.com
  RFC6837          ||      E. Lear         ||       lear@cisco.com
  RFC6838          ||      N. Freed, J. Klensin, T. Hansen         ||       ned+ietf@mrochek.com, john+ietf@jck.com, tony+mtsuffix@maillennium.att.com
  RFC6839          ||      T. Hansen, A. Melnikov         ||       tony+sss@maillennium.att.com, Alexey.Melnikov@isode.com
  RFC6840          ||      S. Weiler, Ed., D. Blacka, Ed.         ||       weiler@tislabs.com, davidb@verisign.com
  RFC6841          ||      F. Ljunggren, AM. Eklund Lowinder, T. Okubo         ||       fredrik@kirei.se, amel@iis.se, tomofumi.okubo@icann.org
  RFC6842          ||      N. Swamy, G. Halwasia, P. Jhingran         ||       nn.swamy@samsung.com, ghalwasi@cisco.com, pjhingra@cisco.com
  RFC6843          ||      A. Clark, K. Gross, Q. Wu         ||       alan.d.clark@telchemy.com, kevin.gross@avanw.com, sunseawq@huawei.com
  RFC6844          ||      P. Hallam-Baker, R. Stradling         ||       philliph@comodo.com, rob.stradling@comodo.com
  RFC6845          ||      N. Sheth, L. Wang, J. Zhang         ||       nsheth@contrailsystems.com, liliw@juniper.net, zzhang@juniper.net
  RFC6846          ||      G. Pelletier, K. Sandlund, L-E. Jonsson, M. West         ||       ghyslain.pelletier@interdigital.com, kristofer.sandlund@ericsson.com, lars-erik@lejonsson.com, mark.a.west@roke.co.uk
  RFC6847          ||      D. Melman, T. Mizrahi, D. Eastlake 3rd         ||       davidme@marvell.com, talmi@marvell.com, d3e3e3@gmail.com
  RFC6848          ||      J. Winterbottom, M. Thomson, R. Barnes, B. Rosen, R. George         ||       james.winterbottom@commscope.com, martin.thomson@gmail.com, rbarnes@bbn.com, br@brianrosen.net, robinsgv@gmail.com
  RFC6849          ||      H. Kaplan, Ed., K. Hedayat, N. Venna, P. Jones, N. Stratton         ||       hkaplan@acmepacket.com, kh274@cornell.edu, vnagarjuna@saperix.com, paulej@packetizer.com, nathan@robotics.net
  RFC6850          ||      A. Rijhsinghani, K. Zebrose         ||       anil@charter.net, zebrose@alum.mit.edu
  RFC6851          ||      A. Gulbrandsen, N. Freed, Ed.         ||       arnt@gulbrandsen.priv.no, ned+ietf@mrochek.com
  RFC6852          ||      R. Housley, S. Mills, J. Jaffe, B. Aboba, L. St.Amour         ||       housley@vigilsec.com, s.mills@ieee.org, jeff@w3.org, bernard_aboba@hotmail.com, st.amour@isoc.org
  RFC6853          ||      J. Brzozowski, J. Tremblay, J. Chen, T. Mrugalski         ||       john_brzozowski@cable.comcast.com, jf@jftremblay.com, jack.chen@twcable.com, tomasz.mrugalski@gmail.com
  RFC6854          ||      B. Leiba         ||       barryleiba@computer.org
  RFC6855          ||      P. Resnick, Ed., C. Newman, Ed., S. Shen, Ed.         ||       presnick@qti.qualcomm.com, chris.newman@oracle.com, shenshuo@cnnic.cn
  RFC6856          ||      R. Gellens, C. Newman, J. Yao, K. Fujiwara         ||       rg+ietf@qualcomm.com, chris.newman@oracle.com, yaojk@cnnic.cn, fujiwara@jprs.co.jp
  RFC6857          ||      K. Fujiwara         ||       fujiwara@jprs.co.jp
  RFC6858          ||      A. Gulbrandsen         ||       arnt@gulbrandsen.priv.no
  RFC6859          ||      B. Leiba         ||       barryleiba@computer.org
  RFC6860          ||      Y. Yang, A. Retana, A. Roy         ||       yiya@cisco.com, aretana@cisco.com, akr@cisco.com
  RFC6861          ||      I. Dzmanashvili         ||       ioseb.dzmanashvili@gmail.com
  RFC6862          ||      G. Lebovitz, M. Bhatia, B. Weis         ||       gregory.ietf@gmail.com, manav.bhatia@alcatel-lucent.com, bew@cisco.com
  RFC6863          ||      S. Hartman, D. Zhang         ||       hartmans-ietf@mit.edu, zhangdacheng@huawei.com
  RFC6864          ||      J. Touch         ||       touch@isi.edu
  RFC6865          ||      V. Roca, M. Cunche, J. Lacan, A. Bouabdallah, K. Matsuzono         ||       vincent.roca@inria.fr, mathieu.cunche@inria.fr, jerome.lacan@isae.fr, abouabdallah@cdta.dz, kazuhisa@sfc.wide.ad.jp
  RFC6866          ||      B. Carpenter, S. Jiang         ||       brian.e.carpenter@gmail.com, jiangsheng@huawei.com
  RFC6867          ||      Y. Nir, Q. Wu         ||       ynir@checkpoint.com, sunseawq@huawei.com
  RFC6868          ||      C. Daboo         ||       cyrus@daboo.name
  RFC6869          ||      G. Salgueiro, J. Clarke, P. Saint-Andre         ||       gsalguei@cisco.com, jclarke@cisco.com, ietf@stpeter.im
  RFC6870          ||      P. Muley, Ed., M. Aissaoui, Ed.         ||       praveen.muley@alcatel-lucent.com, mustapha.aissaoui@alcatel-lucent.com
  RFC6871          ||      R. Gilman, R. Even, F. Andreasen         ||       bob_gilman@comcast.net, roni.even@mail01.huawei.com, fandreas@cisco.com
  RFC6872          ||      V. Gurbani, Ed., E. Burger, Ed., T. Anjali, H. Abdelnur, O. Festor         ||       vkg@bell-labs.com, eburger@standardstrack.com, tricha@ece.iit.edu, humbol@gmail.com, Olivier.Festor@loria.fr
  RFC6873          ||      G. Salgueiro, V. Gurbani, A. B. Roach         ||       gsalguei@cisco.com, vkg@bell-labs.com, adam@nostrum.com
  RFC6874          ||      B. Carpenter, S. Cheshire, R. Hinden         ||       brian.e.carpenter@gmail.com, cheshire@apple.com, bob.hinden@gmail.com
  RFC6875          ||      S. Kamei, T. Momose, T. Inoue, T. Nishitani         ||       skame@nttv6.jp, tmomose@cisco.com, inoue@jp.ntt.net, tomohiro.nishitani@ntt.com
  RFC6876          ||      P. Sangster, N. Cam-Winget, J. Salowey         ||       paul_sangster@symantec.com, ncamwing@cisco.com, jsalowey@cisco.com
  RFC6877          ||      M. Mawatari, M. Kawashima, C. Byrne         ||       mawatari@jpix.ad.jp, kawashimam@vx.jp.nec.com, cameron.byrne@t-mobile.com
  RFC6878          ||      A.B. Roach         ||       adam@nostrum.com
  RFC6879          ||      S. Jiang, B. Liu, B. Carpenter         ||       jiangsheng@huawei.com, leo.liubing@huawei.com, brian.e.carpenter@gmail.com
  RFC6880          ||      L. Johansson         ||       leifj@sunet.se
  RFC6881          ||      B. Rosen, J. Polk         ||       br@brianrosen.net, jmpolk@cisco.com
  RFC6882          ||      K. Kumaki, Ed., T. Murai, D. Cheng, S. Matsushima, P. Jiang         ||       ke-kumaki@kddi.com, murai@fnsc.co.jp, dean.cheng@huawei.com, satoru.matsushima@g.softbank.co.jp, pe-jiang@kddi.com
  RFC6883          ||      B. Carpenter, S. Jiang         ||       brian.e.carpenter@gmail.com, jiangsheng@huawei.com
  RFC6884          ||      Z. Fang         ||       zfang@qualcomm.com
  RFC6885          ||      M. Blanchet, A. Sullivan         ||       Marc.Blanchet@viagenie.ca, asullivan@dyn.com
  RFC6886          ||      S. Cheshire, M. Krochmal         ||       cheshire@apple.com, marc@apple.com
  RFC6887          ||      D. Wing, Ed., S. Cheshire, M. Boucadair, R. Penno, P. Selkirk         ||       dwing-ietf@fuggles.com, cheshire@apple.com, mohamed.boucadair@orange.com, repenno@cisco.com, pselkirk@isc.org
  RFC6888          ||      S. Perreault, Ed., I. Yamagata, S. Miyakawa, A. Nakagawa, H. Ashida         ||       simon.perreault@viagenie.ca, ikuhei@nttv6.jp, miyakawa@nttv6.jp, a-nakagawa@jpix.ad.jp, hiashida@cisco.com
  RFC6889          ||      R. Penno, T. Saxena, M. Boucadair, S. Sivakumar         ||       rpenno@juniper.net, tasaxena@cisco.com, mohamed.boucadair@orange.com, ssenthil@cisco.com
  RFC6890          ||      M. Cotton, L. Vegoda, R. Bonica, Ed., B. Haberman         ||       michelle.cotton@icann.org, leo.vegoda@icann.org, rbonica@juniper.net, brian@innovationslab.net
  RFC6891          ||      J. Damas, M. Graff, P. Vixie         ||       joao@bondis.org, explorer@flame.org, vixie@isc.org
  RFC6892          ||      E. Wilde         ||       erik.wilde@emc.com
  RFC6893          ||      P. Higgs, P. Szucs         ||       paul.higgs@ericsson.com, paul.szucs@eu.sony.com
  RFC6894          ||      R. Papneja, S. Vapiwala, J. Karthik, S. Poretsky, S. Rao, JL. Le Roux         ||       rajiv.papneja@huawei.com, svapiwal@cisco.com, jkarthik@cisco.com, sporetsky@allot.com, shankar.rao@du.edu, jeanlouis.leroux@orange.com
  RFC6895          ||      D. Eastlake 3rd         ||       d3e3e3@gmail.com
  RFC6896          ||      S. Barbato, S. Dorigotti, T. Fossati, Ed.         ||       tat@koanlogic.com, stewy@koanlogic.com, tho@koanlogic.com
  RFC6897          ||      M. Scharf, A. Ford         ||       michael.scharf@alcatel-lucent.com, alanford@cisco.com
  RFC6898          ||      D. Li, D. Ceccarelli, L. Berger         ||       huawei.danli@huawei.com, daniele.ceccarelli@ericsson.com, lberger@labn.net
  RFC6901          ||      P. Bryan, Ed., K. Zyp, M. Nottingham, Ed.         ||       pbryan@anode.ca, kris@sitepen.com, mnot@mnot.net
  RFC6902          ||      P. Bryan, Ed., M. Nottingham, Ed.         ||       pbryan@anode.ca, mnot@mnot.net
  RFC6903          ||      J. Snell         ||       jasnell@gmail.com
  RFC6904          ||      J. Lennox         ||       jonathan@vidyo.com
  RFC6905          ||      T. Senevirathne, D. Bond, S. Aldrin, Y. Li, R. Watve         ||       tsenevir@cisco.com, mokon@mokon.net, aldrin.ietf@gmail.com, liyizhou@huawei.com, rwatve@cisco.com
  RFC6906          ||      E. Wilde         ||       erik.wilde@emc.com
  RFC6907          ||      T. Manderson, K. Sriram, R. White         ||       terry.manderson@icann.org, ksriram@nist.gov, russ@riw.us
  RFC6908          ||      Y. Lee, R. Maglione, C. Williams, C. Jacquenet, M. Boucadair         ||       yiu_lee@cable.comcast.com, robmgl@cisco.com, carlw@mcsr-labs.org, christian.jacquenet@orange.com, mohamed.boucadair@orange.com
  RFC6909          ||      S. Gundavelli, Ed., X. Zhou, J. Korhonen, G. Feige, R. Koodli         ||       sgundave@cisco.com, zhou.xingyue@zte.com.cn, jouni.nospam@gmail.com, gfeige@cisco.com, rkoodli@cisco.com
  RFC6910          ||      D. Worley, M. Huelsemann, R. Jesske, D. Alexeitsev         ||       worley@ariadne.com, martin.huelsemann@telekom.de, r.jesske@telekom.de, alexeitsev@teleflash.com
  RFC6911          ||      W. Dec, Ed., B. Sarikaya, G. Zorn, Ed., D. Miles, B. Lourdelet         ||       wdec@cisco.com, sarikaya@ieee.org, glenzorn@gmail.com, davidmiles@google.com, blourdel@juniper.net
  RFC6912          ||      A. Sullivan, D. Thaler, J. Klensin, O. Kolkman         ||       asullivan@dyn.com, dthaler@microsoft.com, john-ietf@jck.com, olaf@NLnetLabs.nl
  RFC6913          ||      D. Hanes, G. Salgueiro, K. Fleming         ||       dhanes@cisco.com, gsalguei@cisco.com, kevin@kpfleming.us
  RFC6914          ||      J. Rosenberg         ||       jdrosen@jdrosen.net
  RFC6915          ||      R. Bellis         ||       ray.bellis@nominet.org.uk
  RFC6916          ||      R. Gagliano, S. Kent, S. Turner         ||       rogaglia@cisco.com, kent@bbn.com, turners@ieca.com
  RFC6917          ||      C. Boulton, L. Miniero, G. Munson         ||       chris@ns-technologies.com, lorenzo@meetecho.com, gamunson@gmail.com
  RFC6918          ||      F. Gont, C. Pignataro         ||       fgont@si6networks.com, cpignata@cisco.com
  RFC6919          ||      R. Barnes, S. Kent, E. Rescorla         ||       rlb@ipv.sx, kent@bbn.com, ekr@rtfm.com
  RFC6920          ||      S. Farrell, D. Kutscher, C. Dannewitz, B. Ohlman, A. Keranen, P. Hallam-Baker         ||       stephen.farrell@cs.tcd.ie, kutscher@neclab.eu, cdannewitz@googlemail.com, Borje.Ohlman@ericsson.com, ari.keranen@ericsson.com, philliph@comodo.com
  RFC6921          ||      R. Hinden         ||       bob.hinden@gmail.com
  RFC6922          ||      Y. Shafranovich         ||       ietf@shaftek.org
  RFC6923          ||      R. Winter, E. Gray, H. van Helvoort, M. Betts         ||       rolf.winter@neclab.eu, eric.gray@ericsson.com, huub.van.helvoort@huawei.com, malcolm.betts@zte.com.cn
  RFC6924          ||      B. Leiba         ||       barryleiba@computer.org
  RFC6925          ||      B. Joshi, R. Desetti, M. Stapp         ||       bharat_joshi@infosys.com, ramakrishnadtv@infosys.com, mjs@cisco.com
  RFC6926          ||      K. Kinnear, M. Stapp, R. Desetti, B. Joshi, N. Russell, P. Kurapati, B. Volz         ||       kkinnear@cisco.com, mjs@cisco.com, ramakrishnadtv@infosys.com, bharat_joshi@infosys.com, neil.e.russell@gmail.com, kurapati@juniper.net, volz@cisco.com
  RFC6927          ||      J. Levine, P. Hoffman         ||       standards@taugh.com, paul.hoffman@vpnc.org
  RFC6928          ||      J. Chu, N. Dukkipati, Y. Cheng, M. Mathis         ||       hkchu@google.com, nanditad@google.com, ycheng@google.com, mattmathis@google.com
  RFC6929          ||      A. DeKok, A. Lior         ||       aland@networkradius.com, avi.ietf@lior.org
  RFC6930          ||      D. Guo, S. Jiang, Ed., R. Despres, R. Maglione         ||       guoseu@huawei.com, jiangsheng@huawei.com, despres.remi@laposte.net, robmgl@cisco.com
  RFC6931          ||      D. Eastlake 3rd         ||       d3e3e3@gmail.com
  RFC6932          ||      D. Harkins, Ed.         ||       dharkins@arubanetworks.com
  RFC6933          ||      A. Bierman, D. Romascanu, J. Quittek, M. Chandramouli         ||       andy@yumaworks.com, dromasca@gmail.com , quittek@neclab.eu, moulchan@cisco.com
  RFC6934          ||      N. Bitar, Ed., S. Wadhwa, Ed., T. Haag, H. Li         ||       nabil.n.bitar@verizon.com, sanjay.wadhwa@alcatel-lucent.com, HaagT@telekom.de, hongyu.lihongyu@huawei.com
  RFC6935          ||      M. Eubanks, P. Chimento, M. Westerlund         ||       marshall.eubanks@gmail.com, Philip.Chimento@jhuapl.edu, magnus.westerlund@ericsson.com
  RFC6936          ||      G. Fairhurst, M. Westerlund         ||       gorry@erg.abdn.ac.uk, magnus.westerlund@ericsson.com
  RFC6937          ||      M. Mathis, N. Dukkipati, Y. Cheng         ||       mattmathis@google.com, nanditad@google.com, ycheng@google.com
  RFC6938          ||      J. Scudder         ||       jgs@juniper.net
  RFC6939          ||      G. Halwasia, S. Bhandari, W. Dec         ||       ghalwasi@cisco.com, shwethab@cisco.com, wdec@cisco.com
  RFC6940          ||      C. Jennings, B. Lowekamp, Ed., E. Rescorla, S. Baset, H. Schulzrinne         ||       fluffy@cisco.com, bbl@lowekamp.net, ekr@rtfm.com, salman@cs.columbia.edu, hgs@cs.columbia.edu
  RFC6941          ||      L. Fang, Ed., B. Niven-Jenkins, Ed., S. Mansfield, Ed., R. Graveman, Ed.         ||       lufang@cisco.com, ben@niven-jenkins.co.uk, scott.mansfield@ericsson.com, rfg@acm.org
  RFC6942          ||      J. Bournelle, L. Morand, S. Decugis, Q. Wu, G. Zorn         ||       julien.bournelle@orange.com, lionel.morand@orange.com, sdecugis@freediameter.net, sunseawq@huawei.com, glenzorn@gmail.com
  RFC6943          ||      D. Thaler, Ed.         ||       dthaler@microsoft.com
  RFC6944          ||      S. Rose         ||       scottr.nist@gmail.com
  RFC6945          ||      R. Bush, B. Wijnen, K. Patel, M. Baer         ||       randy@psg.com, bertietf@bwijnen.net, keyupate@cisco.com, baerm@tislabs.com
  RFC6946          ||      F. Gont         ||       fgont@si6networks.com
  RFC6947          ||      M. Boucadair, H. Kaplan, R. Gilman, S. Veikkolainen         ||       mohamed.boucadair@orange.com, hkaplan@acmepacket.com, bob_gilman@comcast.net, Simo.Veikkolainen@nokia.com
  RFC6948          ||      A. Keranen, J. Arkko         ||       ari.keranen@ericsson.com, jari.arkko@piuha.net
  RFC6949          ||      H. Flanagan, N. Brownlee         ||       rse@rfc-editor.org, rfc-ise@rfc-editor.org
  RFC6950          ||      J. Peterson, O. Kolkman, H. Tschofenig, B. Aboba         ||       jon.peterson@neustar.biz, olaf@nlnetlabs.nl, Hannes.Tschofenig@gmx.net, Bernard_aboba@hotmail.com
  RFC6951          ||      M. Tuexen, R. Stewart         ||       tuexen@fh-muenster.de, randall@lakerest.net
  RFC6952          ||      M. Jethanandani, K. Patel, L. Zheng         ||       mjethanandani@gmail.com, keyupate@cisco.com, vero.zheng@huawei.com
  RFC6953          ||      A. Mancuso, Ed., S. Probasco, B. Patil         ||       amancuso@google.com, scott@probasco.me, basavpat@cisco.com
  RFC6954          ||      J. Merkle, M. Lochter         ||       johannes.merkle@secunet.com, manfred.lochter@bsi.bund.de
  RFC6955          ||      J. Schaad, H. Prafullchandra         ||       ietf@augustcellars.com, HPrafullchandra@hytrust.com
  RFC6956          ||      W. Wang, E. Haleplidis, K. Ogawa, C. Li, J. Halpern         ||       wmwang@zjsu.edu.cn, ehalep@ece.upatras.gr, ogawa.kentaro@lab.ntt.co.jp, chuanhuang_li@zjsu.edu.cn, joel.halpern@ericsson.com
  RFC6957          ||      F. Costa, J-M. Combes, Ed., X. Pougnard, H. Li         ||       fabio.costa@orange.com, jeanmichel.combes@orange.com, xavier.pougnard@orange.com, lihy@huawei.com
  RFC6958          ||      A. Clark, S. Zhang, J. Zhao, Q. Wu, Ed.         ||       alan.d.clark@telchemy.com, zhangyx@sttri.com.cn, zhaojing@sttri.com.cn, sunseawq@huawei.com
  RFC6959          ||      D. McPherson, F. Baker, J. Halpern         ||       dmcpherson@verisign.com, fred@cisco.com, joel.halpern@ericsson.com
  RFC6960          ||      S. Santesson, M. Myers, R. Ankney, A. Malpani, S. Galperin, C. Adams         ||       sts@aaa-sec.com, mmyers@fastq.com, none, ambarish@gmail.com, slava.galperin@gmail.com, cadams@eecs.uottawa.ca
  RFC6961          ||      Y. Pettersen         ||       yngve@spec-work.net
  RFC6962          ||      B. Laurie, A. Langley, E. Kasper         ||       benl@google.com, agl@google.com, ekasper@google.com
  RFC6963          ||      P. Saint-Andre         ||       ietf@stpeter.im
  RFC6964          ||      F. Templin         ||       fltemplin@acm.org
  RFC6965          ||      L. Fang, Ed., N. Bitar, R. Zhang, M. Daikoku, P. Pan         ||       lufang@cisco.com, nabil.bitar@verizon.com, raymond.zhang@alcatel-lucent.com, ms-daikoku@kddi.com, ppan@infinera.com
  RFC6967          ||      M. Boucadair, J. Touch, P. Levis, R. Penno         ||       mohamed.boucadair@orange.com, touch@isi.edu, pierre.levis@orange.com, repenno@cisco.com
  RFC6968          ||      V. Roca, B. Adamson         ||       vincent.roca@inria.fr, adamson@itd.nrl.navy.mil
  RFC6969          ||      A. Retana, D. Cheng         ||       aretana@cisco.com, dean.cheng@huawei.com
  RFC6970          ||      M. Boucadair, R. Penno, D. Wing         ||       mohamed.boucadair@orange.com, repenno@cisco.com, dwing-ietf@fuggles.com
  RFC6971          ||      U. Herberg, Ed., A. Cardenas, T. Iwao, M. Dow, S. Cespedes         ||       ulrich.herberg@us.fujitsu.com, alvaro.cardenas@me.com, smartnetpro-iwao_std@ml.css.fujitsu.com, m.dow@freescale.com, scespedes@icesi.edu.co
  RFC6972          ||      Y. Zhang, N. Zong         ||       hishigh@gmail.com, zongning@huawei.com
  RFC6973          ||      A. Cooper, H. Tschofenig, B. Aboba, J. Peterson, J. Morris, M. Hansen, R. Smith         ||       acooper@cdt.org, Hannes.Tschofenig@gmx.net, bernard_aboba@hotmail.com, jon.peterson@neustar.biz, ietf@jmorris.org, marit.hansen@datenschutzzentrum.de, rhys.smith@ja.net
  RFC6974          ||      Y. Weingarten, S. Bryant, D. Ceccarelli, D. Caviglia, F. Fondelli, M. Corsi, B. Wu, X. Dai         ||       wyaacov@gmail.com, stbryant@cisco.com, daniele.ceccarelli@ericsson.com, diego.caviglia@ericsson.com, francesco.fondelli@ericsson.com, corsi.marco@gmail.com, wu.bo@zte.com.cn, dai.xuehui@zte.com.cn
  RFC6975          ||      S. Crocker, S. Rose         ||       steve@shinkuro.com, scottr.nist@gmail.com
  RFC6976          ||      M. Shand, S. Bryant, S. Previdi, C. Filsfils, P. Francois, O. Bonaventure         ||       imc.shand@googlemail.com, stbryant@cisco.com, sprevidi@cisco.com, cfilsfil@cisco.com, pierre.francois@imdea.org, Olivier.Bonaventure@uclouvain.be
  RFC6977          ||      M. Boucadair, X. Pougnard         ||       mohamed.boucadair@orange.com, xavier.pougnard@orange.com
  RFC6978          ||      J. Touch         ||       touch@isi.edu
  RFC6979          ||      T. Pornin         ||       pornin@bolet.org
  RFC6980          ||      F. Gont         ||       fgont@si6networks.com
  RFC6981          ||      S. Bryant, S. Previdi, M. Shand         ||       stbryant@cisco.com, sprevidi@cisco.com, imc.shand@googlemail.com
  RFC6982          ||      Y. Sheffer, A. Farrel         ||       yaronf.ietf@gmail.com, adrian@olddog.co.uk
  RFC6983          ||      R. van Brandenburg, O. van Deventer, F. Le Faucheur, K. Leung         ||       ray.vanbrandenburg@tno.nl, oskar.vandeventer@tno.nl, flefauch@cisco.com, kleung@cisco.com
  RFC6984          ||      W. Wang, K. Ogawa, E. Haleplidis, M. Gao, J. Hadi Salim         ||       wmwang@zjsu.edu.cn, ogawa.kentaro@lab.ntt.co.jp, ehalep@ece.upatras.gr, gaoming@mail.zjgsu.edu.cn, hadi@mojatatu.com
  RFC6985          ||      A. Morton         ||       acmorton@att.com
  RFC6986          ||      V. Dolmatov, Ed., A. Degtyarev         ||       dol@cryptocom.ru, alexey@renatasystems.org
  RFC6987          ||      A. Retana, L. Nguyen, A. Zinin, R. White, D. McPherson         ||       aretana@cisco.com, lhnguyen@cisco.com, alex.zinin@gmail.com, Russ.White@vce.com, dmcpherson@verisign.com
  RFC6988          ||      J. Quittek, Ed., M. Chandramouli, R. Winter, T. Dietz, B. Claise         ||       quittek@neclab.eu, moulchan@cisco.com, Rolf.Winter@neclab.eu, Thomas.Dietz@neclab.eu, bclaise@cisco.com
  RFC6989          ||      Y. Sheffer, S. Fluhrer         ||       yaronf.ietf@gmail.com, sfluhrer@cisco.com
  RFC6990          ||      R. Huang, Q. Wu, H. Asaeda, G. Zorn         ||       rachel.huang@huawei.com, bill.wu@huawei.com, asaeda@nict.go.jp, glenzorn@gmail.com
  RFC6991          ||      J. Schoenwaelder, Ed.         ||       j.schoenwaelder@jacobs-university.de
  RFC6992          ||      D. Cheng, M. Boucadair, A. Retana         ||       dean.cheng@huawei.com, mohamed.boucadair@orange.com, aretana@cisco.com
  RFC6993          ||      P. Saint-Andre         ||       ietf@stpeter.im
  RFC6994          ||      J. Touch         ||       touch@isi.edu
  RFC6996          ||      J. Mitchell         ||       Jon.Mitchell@microsoft.com
  RFC6997          ||      M. Goyal, Ed., E. Baccelli, M. Philipp, A. Brandt, J. Martocci         ||       mukul@uwm.edu, Emmanuel.Baccelli@inria.fr, matthias-philipp@gmx.de, abr@sdesigns.dk, jerald.p.martocci@jci.com
  RFC6998          ||      M. Goyal, Ed., E. Baccelli, A. Brandt, J. Martocci         ||       mukul@uwm.edu, Emmanuel.Baccelli@inria.fr, abr@sdesigns.dk, jerald.p.martocci@jci.com
  RFC7001          ||      M. Kucherawy         ||       superuser@gmail.com
  RFC7002          ||      A. Clark, G. Zorn, Q. Wu         ||       alan.d.clark@telchemy.com, glenzorn@gmail.com, sunseawq@huawei.com
  RFC7003          ||      A. Clark, R. Huang, Q. Wu, Ed.         ||       alan.d.clark@telchemy.com, Rachel@huawei.com, sunseawq@huawei.com
  RFC7004          ||      G. Zorn, R. Schott, Q. Wu, Ed., R. Huang         ||       glenzorn@gmail.com, Roland.Schott@telekom.de, sunseawq@huawei.com, Rachel@huawei.com
  RFC7005          ||      A. Clark, V. Singh, Q. Wu         ||       alan.d.clark@telchemy.com, varun@comnet.tkk.fi, sunseawq@huawei.com
  RFC7006          ||      M. Garcia-Martin, S. Veikkolainen, R. Gilman         ||       miguel.a.garcia@ericsson.com, simo.veikkolainen@nokia.com, bob_gilman@comcast.net
  RFC7007          ||      T. Terriberry         ||       tterribe@xiph.org
  RFC7008          ||      S. Kiyomoto, W. Shin         ||       kiyomoto@kddilabs.jp, ohpato@hanmail.net
  RFC7009          ||      T. Lodderstedt, Ed., S. Dronia, M. Scurtescu         ||       torsten@lodderstedt.net, sdronia@gmx.de, mscurtescu@google.com
  RFC7010          ||      B. Liu, S. Jiang, B. Carpenter, S. Venaas, W. George         ||       leo.liubing@huawei.com, jiangsheng@huawei.com, brian.e.carpenter@gmail.com, stig@cisco.com, wesley.george@twcable.com
  RFC7011          ||      B. Claise, Ed., B. Trammell, Ed., P. Aitken         ||       bclaise@cisco.com, trammell@tik.ee.ethz.ch, paitken@cisco.com
  RFC7012          ||      B. Claise, Ed., B. Trammell, Ed.         ||       bclaise@cisco.com, trammell@tik.ee.ethz.ch
  RFC7013          ||      B. Trammell, B. Claise         ||       trammell@tik.ee.ethz.ch, bclaise@cisco.com
  RFC7014          ||      S. D'Antonio, T. Zseby, C. Henke, L. Peluso         ||       salvatore.dantonio@uniparthenope.it, tanja@caida.org, christian.henke@tektronix.com, lorenzo.peluso@unina.it
  RFC7015          ||      B. Trammell, A. Wagner, B. Claise         ||       trammell@tik.ee.ethz.ch, arno@wagner.name, bclaise@cisco.com
  RFC7016          ||      M. Thornburgh         ||       mthornbu@adobe.com
  RFC7017          ||      R. Sparks         ||       rjsparks@nostrum.com
  RFC7018          ||      V. Manral, S. Hanna         ||       vishwas.manral@hp.com, shanna@juniper.net
  RFC7019          ||      J. Buford, M. Kolberg, Ed.         ||       buford@avaya.com, mkolberg@ieee.org
  RFC7020          ||      R. Housley, J. Curran, G. Huston, D. Conrad         ||       housley@vigilsec.com, jcurran@arin.net, gih@apnic.net, drc@virtualized.org
  RFC7021          ||      C. Donley, Ed., L. Howard, V. Kuarsingh, J. Berg, J. Doshi         ||       c.donley@cablelabs.com, william.howard@twcable.com, victor@jvknet.com, j.berg@cablelabs.com, jineshd@juniper.net
  RFC7022          ||      A. Begen, C. Perkins, D. Wing, E. Rescorla         ||       abegen@cisco.com, csp@csperkins.org, dwing-ietf@fuggles.com, ekr@rtfm.com
  RFC7023          ||      D. Mohan, Ed., N. Bitar, Ed., A. Sajassi, Ed., S. DeLord, P. Niger, R. Qiu         ||       dinmohan@hotmail.com, nabil.n.bitar@verizon.com, sajassi@cisco.com, simon.delord@gmail.com, philippe.niger@orange.com, rqiu@juniper.net
  RFC7024          ||      H. Jeng, J. Uttaro, L. Jalil, B. Decraene, Y. Rekhter, R. Aggarwal         ||       hj2387@att.com, ju1738@att.com, luay.jalil@verizon.com, bruno.decraene@orange.com, yakov@juniper.net, raggarwa_1@yahoo.com
  RFC7025          ||      T. Otani, K. Ogaki, D. Caviglia, F. Zhang, C. Margaria         ||       tm-otani@kddi.com, ke-oogaki@kddi.com, diego.caviglia@ericsson.com, zhangfatai@huawei.com, cyril.margaria@coriant.com
  RFC7026          ||      A. Farrel, S. Bryant         ||       adrian@olddog.co.uk, stbryant@cisco.com
  RFC7027          ||      J. Merkle, M. Lochter         ||       johannes.merkle@secunet.com, manfred.lochter@bsi.bund.de
  RFC7028          ||      JC. Zuniga, LM. Contreras, CJ. Bernardos, S. Jeon, Y. Kim         ||       JuanCarlos.Zuniga@InterDigital.com, lmcm@tid.es, cjbc@it.uc3m.es, seiljeon@av.it.pt, yhkim@dcn.ssu.ac.kr
  RFC7029          ||      S. Hartman, M. Wasserman, D. Zhang         ||       hartmans-ietf@mit.edu, mrw@painless-security.com, zhangdacheng@huawei.com
  RFC7030          ||      M. Pritikin, Ed., P. Yee, Ed., D. Harkins, Ed.         ||       pritikin@cisco.com, peter@akayla.com, dharkins@arubanetworks.com
  RFC7031          ||      T. Mrugalski, K. Kinnear         ||       tomasz.mrugalski@gmail.com, kkinnear@cisco.com
  RFC7032          ||      T. Beckhaus, Ed., B. Decraene, K. Tiruveedhula, M. Konstantynowicz, Ed., L. Martini         ||       thomas.beckhaus@telekom.de, bruno.decraene@orange.com, kishoret@juniper.net, maciek@cisco.com, lmartini@cisco.com
  RFC7033          ||      P. Jones, G. Salgueiro, M. Jones, J. Smarr         ||       paulej@packetizer.com, gsalguei@cisco.com, mbj@microsoft.com, jsmarr@google.com
  RFC7034          ||      D. Ross, T. Gondrom         ||       dross@microsoft.com, tobias.gondrom@gondrom.org
  RFC7035          ||      M. Thomson, B. Rosen, D. Stanley, G. Bajko, A. Thomson         ||       martin.thomson@skype.net, br@brianrosen.net, dstanley@arubanetworks.com, Gabor.Bajko@nokia.com, athomson@lgscout.com
  RFC7036          ||      R. Housley         ||       housley@vigilsec.com
  RFC7037          ||      L. Yeh, M. Boucadair         ||       leaf.yeh.sdo@gmail.com, mohamed.boucadair@orange.com
  RFC7038          ||      R. Ogier         ||       ogier@earthlink.net
  RFC7039          ||      J. Wu, J. Bi, M. Bagnulo, F. Baker, C. Vogt, Ed.         ||       jianping@cernet.edu.cn, junbi@tsinghua.edu.cn, marcelo@it.uc3m.es, fred@cisco.com, mail@christianvogt.net
  RFC7040          ||      Y. Cui, J. Wu, P. Wu, O. Vautrin, Y. Lee         ||       yong@csnet1.cs.tsinghua.edu.cn, jianping@cernet.edu.cn, pengwu.thu@gmail.com, Olivier@juniper.net, yiu_lee@cable.comcast.com
  RFC7041          ||      F. Balus, Ed., A. Sajassi, Ed., N. Bitar, Ed.         ||       florin.balus@alcatel-lucent.com, sajassi@cisco.com, nabil.n.bitar@verizon.com
  RFC7042          ||      D. Eastlake 3rd, J. Abley         ||       d3e3e3@gmail.com, jabley@dyn.com
  RFC7043          ||      J. Abley         ||       jabley@dyn.com
  RFC7044          ||      M. Barnes, F. Audet, S. Schubert, J. van Elburg, C. Holmberg         ||       mary.ietf.barnes@gmail.com, francois.audet@skype.net, shida@ntt-at.com, ietf.hanserik@gmail.com, christer.holmberg@ericsson.com
  RFC7045          ||      B. Carpenter, S. Jiang         ||       brian.e.carpenter@gmail.com, jiangsheng@huawei.com
  RFC7046          ||      M. Waehlisch, T. Schmidt, S. Venaas         ||       mw@link-lab.net, Schmidt@informatik.haw-hamburg.de, stig@cisco.com
  RFC7047          ||      B. Pfaff, B. Davie, Ed.         ||       blp@nicira.com, bsd@nicira.com
  RFC7048          ||      E. Nordmark, I. Gashinsky         ||       nordmark@acm.org, igor@yahoo-inc.com
  RFC7049          ||      C. Bormann, P. Hoffman         ||       cabo@tzi.org, paul.hoffman@vpnc.org
  RFC7050          ||      T. Savolainen, J. Korhonen, D. Wing         ||       teemu.savolainen@nokia.com, jouni.nospam@gmail.com, dwing-ietf@fuggles.com
  RFC7051          ||      J. Korhonen, Ed., T. Savolainen, Ed.         ||       jouni.nospam@gmail.com, teemu.savolainen@nokia.com
  RFC7052          ||      G. Schudel, A. Jain, V. Moreno         ||       gschudel@cisco.com, atjain@juniper.net, vimoreno@cisco.com
  RFC7053          ||      M. Tuexen, I. Ruengeler, R. Stewart         ||       tuexen@fh-muenster.de, i.ruengeler@fh-muenster.de, randall@lakerest.net
  RFC7054          ||      A. Farrel, H. Endo, R. Winter, Y. Koike, M. Paul         ||       adrian@olddog.co.uk, hideki.endo.es@hitachi.com, rolf.winter@neclab.eu, koike.yoshinori@lab.ntt.co.jp, Manuel.Paul@telekom.de
  RFC7055          ||      S. Hartman, Ed., J. Howlett         ||       hartmans-ietf@mit.edu, josh.howlett@ja.net
  RFC7056          ||      S. Hartman, J. Howlett         ||       hartmans-ietf@mit.edu, josh.howlett@ja.net
  RFC7057          ||      S. Winter, J. Salowey         ||       stefan.winter@restena.lu, jsalowey@cisco.com
  RFC7058          ||      A. Amirante, T. Castaldi, L. Miniero, S P. Romano         ||       alessandro.amirante@unina.it, tcastaldi@meetecho.com, lorenzo@meetecho.com, spromano@unina.it
  RFC7059          ||      S. Steffann, I. van Beijnum, R. van Rein         ||       sander@steffann.nl, iljitsch@muada.com, rick@openfortress.nl
  RFC7060          ||      M. Napierala, E. Rosen, IJ. Wijnands         ||       mnapierala@att.com, erosen@cisco.com, ice@cisco.com
  RFC7061          ||      R. Sinnema, E. Wilde         ||       remon.sinnema@emc.com, erik.wilde@emc.com
  RFC7062          ||      F. Zhang, Ed., D. Li, H. Li, S. Belotti, D. Ceccarelli         ||       zhangfatai@huawei.com, huawei.danli@huawei.com, lihan@chinamobile.com, sergio.belotti@alcatel-lucent.it, daniele.ceccarelli@ericsson.com
  RFC7063          ||      L. Zheng, J. Zhang, R. Parekh         ||       vero.zheng@huawei.com, zzhang@juniper.net, riparekh@cisco.com
  RFC7064          ||      S. Nandakumar, G. Salgueiro, P. Jones, M. Petit-Huguenin         ||       snandaku@cisco.com, gsalguei@cisco.com, paulej@packetizer.com, petithug@acm.org
  RFC7065          ||      M. Petit-Huguenin, S. Nandakumar, G. Salgueiro, P. Jones         ||       petithug@acm.org, snandaku@cisco.com, gsalguei@cisco.com, paulej@packetizer.com
  RFC7066          ||      J. Korhonen, Ed., J. Arkko, Ed., T. Savolainen, S. Krishnan         ||       jouni.nospam@gmail.com, jari.arkko@piuha.net, teemu.savolainen@nokia.com, suresh.krishnan@ericsson.com
  RFC7067          ||      L. Dunbar, D. Eastlake 3rd, R. Perlman, I. Gashinsky         ||       ldunbar@huawei.com, d3e3e3@gmail.com, Radia@alum.mit.edu, igor@yahoo-inc.com
  RFC7068          ||      E. McMurry, B. Campbell         ||       emcmurry@computer.org, ben@nostrum.com
  RFC7069          ||      R. Alimi, A. Rahman, D. Kutscher, Y. Yang, H. Song, K. Pentikousis         ||       ralimi@google.com, Akbar.Rahman@InterDigital.com, dirk.kutscher@neclab.eu, yry@cs.yale.edu, haibin.song@huawei.com, k.pentikousis@eict.de
  RFC7070          ||      N. Borenstein, M. Kucherawy         ||       nsb@guppylake.com, superuser@gmail.com
  RFC7071          ||      N. Borenstein, M. Kucherawy         ||       nsb@guppylake.com, superuser@gmail.com
  RFC7072          ||      N. Borenstein, M. Kucherawy         ||       nsb@guppylake.com, superuser@gmail.com
  RFC7073          ||      N. Borenstein, M. Kucherawy         ||       nsb@guppylake.com, superuser@gmail.com
  RFC7074          ||      L. Berger, J. Meuric         ||       lberger@labn.net, julien.meuric@orange.com
  RFC7075          ||      T. Tsou, R. Hao, T. Taylor, Ed.         ||       tina.tsou.zouting@huawei.com, ruibing_hao@cable.comcast.com, tom.taylor.stds@gmail.com
  RFC7076          ||      M. Joseph, J. Susoy         ||       mark@p6r.com, jim@p6r.com
  RFC7077          ||      S. Krishnan, S. Gundavelli, M. Liebsch, H. Yokota, J. Korhonen         ||       suresh.krishnan@ericsson.com, sgundave@cisco.com, marco.liebsch@neclab.eu, yokota@kddilabs.jp, jouni.nospam@gmail.com
  RFC7078          ||      A. Matsumoto, T. Fujisaki, T. Chown         ||       arifumi@nttv6.net, fujisaki@nttv6.net, tjc@ecs.soton.ac.uk
  RFC7079          ||      N. Del Regno, Ed., A. Malis, Ed.         ||       nick.delregno@verizon.com, amalis@gmail.com
  RFC7080          ||      A. Sajassi, S. Salam, N. Bitar, F. Balus         ||       sajassi@cisco.com, ssalam@cisco.com, nabil.n.bitar@verizon.com, florin.balus@nuagenetworks.net
  RFC7081          ||      E. Ivov, P. Saint-Andre, E. Marocco         ||       emcho@jitsi.org, ietf@stpeter.im, enrico.marocco@telecomitalia.it
  RFC7082          ||      R. Shekh-Yusef, M. Barnes         ||       rifaat.ietf@gmail.com, mary.ietf.barnes@gmail.com
  RFC7083          ||      R. Droms         ||       rdroms@cisco.com
  RFC7084          ||      H. Singh, W. Beebee, C. Donley, B. Stark         ||       shemant@cisco.com, wbeebee@cisco.com, c.donley@cablelabs.com, barbara.stark@att.com
  RFC7085          ||      J. Levine, P. Hoffman         ||       standards@taugh.com, paul.hoffman@cybersecurity.org
  RFC7086          ||      A. Keranen, G. Camarillo, J. Maenpaa         ||       Ari.Keranen@ericsson.com, Gonzalo.Camarillo@ericsson.com, Jouni.Maenpaa@ericsson.com
  RFC7087          ||      H. van Helvoort, Ed., L. Andersson, Ed., N. Sprecher, Ed.         ||       Huub.van.Helvoort@huawei.com, loa@mail01.huawei.com, nurit.sprecher@nsn.com
  RFC7088          ||      D. Worley         ||       worley@ariadne.com
  RFC7089          ||      H. Van de Sompel, M. Nelson, R. Sanderson         ||       hvdsomp@gmail.com, mln@cs.odu.edu, azaroth42@gmail.com
  RFC7090          ||      H. Schulzrinne, H. Tschofenig, C. Holmberg, M. Patel         ||       hgs+ecrit@cs.columbia.edu, Hannes.Tschofenig@gmx.net, christer.holmberg@ericsson.com, Milan.Patel@huawei.com
  RFC7091          ||      V. Dolmatov, Ed., A. Degtyarev         ||       dol@cryptocom.ru, alexey@renatasystems.org
  RFC7092          ||      H. Kaplan, V. Pascual         ||       hadriel.kaplan@oracle.com, victor.pascual@quobis.com
  RFC7093          ||      S. Turner, S. Kent, J. Manger         ||       turners@ieca.com, kent@bbn.com, james.h.manger@team.telstra.com
  RFC7094          ||      D. McPherson, D. Oran, D. Thaler, E. Osterweil         ||       dmcpherson@verisign.com, oran@cisco.com, dthaler@microsoft.com, eosterweil@verisign.com
  RFC7095          ||      P. Kewisch         ||       mozilla@kewis.ch
  RFC7096          ||      S. Belotti, Ed., P. Grandi, D. Ceccarelli, Ed., D. Caviglia, F. Zhang, D. Li         ||       sergio.belotti@alcatel-lucent.com, pietro_vittorio.grandi@alcatel-lucent.com, daniele.ceccarelli@ericsson.com, diego.caviglia@ericsson.com, zhangfatai@huawei.com, danli@huawei.com
  RFC7097          ||      J. Ott, V. Singh, Ed., I. Curcio         ||       jo@comnet.tkk.fi, varun@comnet.tkk.fi, igor.curcio@nokia.com
  RFC7098          ||      B. Carpenter, S. Jiang, W. Tarreau         ||       brian.e.carpenter@gmail.com, jiangsheng@huawei.com, willy@haproxy.com
  RFC7100          ||      P. Resnick         ||       presnick@qti.qualcomm.com
  RFC7101          ||      S. Ginoza         ||       sginoza@amsl.com
  RFC7102          ||      JP. Vasseur         ||       jpv@cisco.com
  RFC7103          ||      M. Kucherawy, G. Shapiro, N. Freed         ||       superuser@gmail.com, gshapiro@proofpoint.com, ned.freed@mrochek.com
  RFC7104          ||      A. Begen, Y. Cai, H. Ou         ||       abegen@cisco.com, yiqunc@microsoft.com, hou@cisco.com
  RFC7105          ||      M. Thomson, J. Winterbottom         ||       martin.thomson@gmail.com, a.james.winterbottom@gmail.com
  RFC7106          ||      E. Ivov         ||       emcho@jitsi.org
  RFC7107          ||      R. Housley         ||       housley@vigilsec.com
  RFC7108          ||      J. Abley, T. Manderson         ||       jabley@dyn.com, terry.manderson@icann.org
  RFC7109          ||      H. Yokota, D. Kim, B. Sarikaya, F. Xia         ||       yokota@kddilabs.jp, dskim@jejutp.or.kr, sarikaya@ieee.org, xiayangsong@huawei.com
  RFC7110          ||      M. Chen, W. Cao, S. Ning, F. Jounay, S. Delord         ||       mach.chen@huawei.com, wayne.caowei@huawei.com, ning.so@tatacommunications.com, frederic.jounay@orange.ch, simon.delord@alcatel-lucent.com
  RFC7111          ||      M. Hausenblas, E. Wilde, J. Tennison         ||       mhausenblas@maprtech.com, dret@berkeley.edu, jeni@jenitennison.com
  RFC7112          ||      F. Gont, V. Manral, R. Bonica         ||       fgont@si6networks.com, vishwas@ionosnetworks.com, rbonica@juniper.net
  RFC7113          ||      F. Gont         ||       fgont@si6networks.com
  RFC7114          ||      B. Leiba         ||       barryleiba@computer.org
  RFC7115          ||      R. Bush         ||       randy@psg.com
  RFC7116          ||      K. Scott, M. Blanchet         ||       kscott@mitre.org, marc.blanchet@viagenie.ca
  RFC7117          ||      R. Aggarwal, Ed., Y. Kamite, L. Fang, Y. Rekhter, C. Kodeboniya         ||       raggarwa_1@yahoo.com, y.kamite@ntt.com, lufang@microsoft.com, yakov@juniper.net, chaitk@yahoo.com
  RFC7118          ||      I. Baz Castillo, J. Millan Villegas, V. Pascual         ||       ibc@aliax.net, jmillan@aliax.net, victor.pascual@quobis.com
  RFC7119          ||      B. Claise, A. Kobayashi, B. Trammell         ||       bclaise@cisco.com, akoba@nttv6.net, trammell@tik.ee.ethz.ch
  RFC7120          ||      M. Cotton         ||       michelle.cotton@icann.org
  RFC7121          ||      K. Ogawa, W. Wang, E. Haleplidis, J. Hadi Salim         ||       k.ogawa@ntt.com, wmwang@mail.zjgsu.edu.cn, ehalep@ece.upatras.gr, hadi@mojatatu.com
  RFC7122          ||      H. Kruse, S. Jero, S. Ostermann         ||       kruse@ohio.edu, sjero@purdue.edu, ostermann@eecs.ohiou.edu
  RFC7123          ||      F. Gont, W. Liu         ||       fgont@si6networks.com, liushucheng@huawei.com
  RFC7124          ||      E. Beili         ||       edward.beili@actelis.com
  RFC7125          ||      B. Trammell, P. Aitken         ||       trammell@tik.ee.ethz.ch, paitken@cisco.com
  RFC7126          ||      F. Gont, R. Atkinson, C. Pignataro         ||       fgont@si6networks.com, rja.lists@gmail.com, cpignata@cisco.com
  RFC7127          ||      O. Kolkman, S. Bradner, S. Turner         ||       olaf@nlnetlabs.nl, sob@harvard.edu, turners@ieca.com
  RFC7128          ||      R. Bush, R. Austein, K. Patel, H. Gredler, M. Waehlisch         ||       randy@psg.com, sra@hactrn.net, keyupate@cisco.com, hannes@juniper.net, waehlisch@ieee.org
  RFC7129          ||      R. Gieben, W. Mekking         ||       miek@google.com, matthijs@nlnetlabs.nl
  RFC7130          ||      M. Bhatia, Ed., M. Chen, Ed., S. Boutros, Ed., M. Binderberger, Ed., J. Haas, Ed.         ||       manav.bhatia@alcatel-lucent.com, mach@huawei.com, sboutros@cisco.com, mbinderb@cisco.com, jhaas@juniper.net
  RFC7131          ||      M. Barnes, F. Audet, S. Schubert, H. van Elburg, C. Holmberg         ||       mary.ietf.barnes@gmail.com, francois.audet@skype.net, shida@ntt-at.com, ietf.hanserik@gmail.com, christer.holmberg@ericsson.com
  RFC7132          ||      S. Kent, A. Chi         ||       kent@bbn.com, achi@cs.unc.edu
  RFC7133          ||      S. Kashima, A. Kobayashi, Ed., P. Aitken         ||       kashima@nttv6.net, akoba@nttv6.net, paitken@cisco.com
  RFC7134          ||      B. Rosen         ||       br@brianrosen.net
  RFC7135          ||      J. Polk         ||       jmpolk@cisco.com
  RFC7136          ||      B. Carpenter, S. Jiang         ||       brian.e.carpenter@gmail.com, jiangsheng@huawei.com
  RFC7137          ||      A. Retana, S. Ratliff         ||       aretana@cisco.com, sratliff@cisco.com
  RFC7138          ||      D. Ceccarelli, Ed., F. Zhang, S. Belotti, R. Rao, J. Drake         ||       daniele.ceccarelli@ericsson.com, zhangfatai@huawei.com, sergio.belotti@alcatel-lucent.com, rrao@infinera.com, jdrake@juniper.net
  RFC7139          ||      F. Zhang, Ed., G. Zhang, S. Belotti, D. Ceccarelli, K. Pithewan         ||       zhangfatai@huawei.com, zhangguoying@mail.ritt.com.cn, sergio.belotti@alcatel-lucent.it, daniele.ceccarelli@ericsson.com, kpithewan@infinera.com
  RFC7140          ||      L. Jin, F. Jounay, IJ. Wijnands, N. Leymann         ||       lizho.jin@gmail.com, frederic.jounay@orange.ch, ice@cisco.com, n.leymann@telekom.de
  RFC7141          ||      B. Briscoe, J. Manner         ||       bob.briscoe@bt.com, jukka.manner@aalto.fi
  RFC7142          ||      M. Shand, L. Ginsberg         ||       imc.shand@googlemail.com, ginsberg@cisco.com
  RFC7143          ||      M. Chadalapaka, J. Satran, K. Meth, D. Black         ||       cbm@chadalapaka.com, julians@infinidat.com, meth@il.ibm.com, david.black@emc.com
  RFC7144          ||      F. Knight, M. Chadalapaka         ||       knight@netapp.com, cbm@chadalapaka.com
  RFC7145          ||      M. Ko, A. Nezhinsky         ||       mkosjc@gmail.com, alexandern@mellanox.com
  RFC7146          ||      D. Black, P. Koning         ||       david.black@emc.com, paul_koning@Dell.com
  RFC7147          ||      M. Bakke, P. Venkatesen         ||       mark_bakke@dell.com, prakashvn@hcl.com
  RFC7148          ||      X. Zhou, J. Korhonen, C. Williams, S. Gundavelli, CJ. Bernardos         ||       zhou.xingyue@zte.com.cn, jouni.nospam@gmail.com, carlw@mcsr-labs.org, sgundave@cisco.com, cjbc@it.uc3m.es
  RFC7149          ||      M. Boucadair, C. Jacquenet         ||       mohamed.boucadair@orange.com, christian.jacquenet@orange.com
  RFC7150          ||      F. Zhang, A. Farrel         ||       zhangfatai@huawei.com, adrian@olddog.co.uk
  RFC7151          ||      P. Hethmon, R. McMurray         ||       phethmon@hethmon.com, robmcm@microsoft.com
  RFC7152          ||      R. Key, Ed., S. DeLord, F. Jounay, L. Huang, Z. Liu, M. Paul         ||       raymond.key@ieee.org, simon.delord@gmail.com, frederic.jounay@orange.ch, huanglu@chinamobile.com, zhliu@gsta.com, manuel.paul@telekom.de
  RFC7153          ||      E. Rosen, Y. Rekhter         ||       erosen@cisco.com, yakov@juniper.net
  RFC7154          ||      S. Moonesamy, Ed.         ||       sm+ietf@elandsys.com
  RFC7155          ||      G. Zorn, Ed.         ||       glenzorn@gmail.com
  RFC7156          ||      G. Zorn, Q. Wu, J. Korhonen         ||       glenzorn@gmail.com, bill.wu@huawei.com, jouni.nospam@gmail.com
  RFC7157          ||      O. Troan, Ed., D. Miles, S. Matsushima, T. Okimoto, D. Wing         ||       ot@cisco.com, davidmiles@google.com, satoru.matsushima@g.softbank.co.jp, t.okimoto@west.ntt.co.jp, dwing-ietf@fuggles.com
  RFC7158          ||      T. Bray, Ed.         ||       tbray@textuality.com
  RFC7159          ||      T. Bray, Ed.         ||       tbray@textuality.com
  RFC7160          ||      M. Petit-Huguenin, G. Zorn, Ed.         ||       petithug@acm.org, glenzorn@gmail.com
  RFC7161          ||      LM. Contreras, CJ. Bernardos, I. Soto         ||       lmcm@tid.es, cjbc@it.uc3m.es, isoto@it.uc3m.es
  RFC7162          ||      A. Melnikov, D. Cridland         ||       Alexey.Melnikov@isode.com, dave.cridland@surevine.com
  RFC7163          ||      C. Holmberg, I. Sedlacek         ||       christer.holmberg@ericsson.com, ivo.sedlacek@ericsson.com
  RFC7164          ||      K. Gross, R. Brandenburg         ||       kevin.gross@avanw.com, ray.vanbrandenburg@tno.nl
  RFC7165          ||      R. Barnes         ||       rlb@ipv.sx
  RFC7166          ||      M. Bhatia, V. Manral, A. Lindem         ||       manav.bhatia@alcatel-lucent.com, vishwas@ionosnetworks.com, acee.lindem@ericsson.com
  RFC7167          ||      D. Frost, S. Bryant, M. Bocci, L. Berger         ||       frost@mm.st, stbryant@cisco.com, matthew.bocci@alcatel-lucent.com, lberger@labn.net
  RFC7168          ||      I. Nazar         ||       inazar@deviantart.com
  RFC7169          ||      S. Turner         ||       turners@ieca.com
  RFC7170          ||      H. Zhou, N. Cam-Winget, J. Salowey, S. Hanna         ||       hzhou@cisco.com, ncamwing@cisco.com, jsalowey@cisco.com, steve.hanna@infineon.com
  RFC7171          ||      N. Cam-Winget, P. Sangster         ||       ncamwing@cisco.com, paul_sangster@symantec.com
  RFC7172          ||      D. Eastlake 3rd, M. Zhang, P. Agarwal, R. Perlman, D. Dutt         ||       d3e3e3@gmail.com, zhangmingui@huawei.com, pagarwal@broadcom.com, Radia@alum.mit.edu, ddutt.ietf@hobbesdutt.com
  RFC7173          ||      L. Yong, D. Eastlake 3rd, S. Aldrin, J. Hudson         ||       lucy.yong@huawei.com, d3e3e3@gmail.com, sam.aldrin@huawei.com, jon.hudson@gmail.com
  RFC7174          ||      S. Salam, T. Senevirathne, S. Aldrin, D. Eastlake 3rd         ||       ssalam@cisco.com, tsenevir@cisco.com, sam.aldrin@gmail.com, d3e3e3@gmail.com
  RFC7175          ||      V. Manral, D. Eastlake 3rd, D. Ward, A. Banerjee         ||       vishwas@ionosnetworks.com, d3e3e3@gmail.com, dward@cisco.com, ayabaner@gmail.com
  RFC7176          ||      D. Eastlake 3rd, T. Senevirathne, A. Ghanwani, D. Dutt, A. Banerjee         ||       d3e3e3@gmail.com, tsenevir@cisco.com, anoop@alumni.duke.edu, ddutt.ietf@hobbesdutt.com, ayabaner@gmail.com
  RFC7177          ||      D. Eastlake 3rd, R. Perlman, A. Ghanwani, H. Yang, V. Manral         ||       d3e3e3@gmail.com, radia@alum.mit.edu, anoop@alumni.duke.edu, howardy@cisco.com, vishwas@ionosnetworks.com
  RFC7178          ||      D. Eastlake 3rd, V. Manral, Y. Li, S. Aldrin, D. Ward         ||       d3e3e3@gmail.com, vishwas@ionosnetworks.com, liyizhou@huawei.com, sam.aldrin@huawei.com, dward@cisco.com
  RFC7179          ||      D. Eastlake 3rd, A. Ghanwani, V. Manral, Y. Li, C. Bestler         ||       d3e3e3@gmail.com, anoop@alumni.duke.edu, vishwas@ionosnetworks.com, liyizhou@huawei.com, caitlin.bestler@nexenta.com
  RFC7180          ||      D. Eastlake 3rd, M. Zhang, A. Ghanwani, V. Manral, A. Banerjee         ||       d3e3e3@gmail.com, zhangmingui@huawei.com, anoop@alumni.duke.edu, vishwas@ionosnetworks.com, ayabaner@gmail.com
  RFC7181          ||      T. Clausen, C. Dearlove, P. Jacquet, U. Herberg         ||       T.Clausen@computer.org, chris.dearlove@baesystems.com, philippe.jacquet@alcatel-lucent.com, ulrich@herberg.name
  RFC7182          ||      U. Herberg, T. Clausen, C. Dearlove         ||       ulrich@herberg.name, T.Clausen@computer.org, chris.dearlove@baesystems.com
  RFC7183          ||      U. Herberg, C. Dearlove, T. Clausen         ||       ulrich@herberg.name, chris.dearlove@baesystems.com, T.Clausen@computer.org
  RFC7184          ||      U. Herberg, R. Cole, T. Clausen         ||       ulrich@herberg.name, robert.g.cole@us.army.mil, T.Clausen@computer.org
  RFC7185          ||      C. Dearlove, T. Clausen, P. Jacquet         ||       chris.dearlove@baesystems.com, T.Clausen@computer.org, philippe.jacquet@alcatel-lucent.com
  RFC7186          ||      J. Yi, U. Herberg, T. Clausen         ||       jiazi@jiaziyi.com, ulrich@herberg.name, T.Clausen@computer.org
  RFC7187          ||      C. Dearlove, T. Clausen         ||       chris.dearlove@baesystems.com, T.Clausen@computer.org
  RFC7188          ||      C. Dearlove, T. Clausen         ||       chris.dearlove@baesystems.com, T.Clausen@computer.org
  RFC7189          ||      G. Mirsky         ||       gregory.mirsky@ericsson.com
  RFC7190          ||      C. Villamizar         ||       curtis@occnc.com
  RFC7191          ||      R. Housley         ||       housley@vigilsec.com
  RFC7192          ||      S. Turner         ||       turners@ieca.com
  RFC7193          ||      S. Turner, R. Housley, J. Schaad         ||       turners@ieca.com, housley@vigilsec.com, ietf@augustcellars.com
  RFC7194          ||      R. Hartmann         ||       richih.mailinglist@gmail.com
  RFC7195          ||      M. Garcia-Martin, S. Veikkolainen         ||       miguel.a.garcia@ericsson.com, simo.veikkolainen@nokia.com
  RFC7196          ||      C. Pelsser, R. Bush, K. Patel, P. Mohapatra, O. Maennel         ||       cristel@iij.ad.jp, randy@psg.com, keyupate@cisco.com, mpradosh@yahoo.com, o@maennel.net
  RFC7197          ||      A. Begen, Y. Cai, H. Ou         ||       abegen@cisco.com, yiqunc@microsoft.com, hou@cisco.com
  RFC7198          ||      A. Begen, C. Perkins         ||       abegen@cisco.com, csp@csperkins.org
  RFC7199          ||      R. Barnes, M. Thomson, J. Winterbottom, H. Tschofenig         ||       rlb@ipv.sx, martin.thomson@gmail.com, a.james.winterbottom@gmail.com, Hannes.Tschofenig@gmx.net
  RFC7200          ||      C. Shen, H. Schulzrinne, A. Koike         ||       charles@cs.columbia.edu, schulzrinne@cs.columbia.edu, koike.arata@lab.ntt.co.jp
  RFC7201          ||      M. Westerlund, C. Perkins         ||       magnus.westerlund@ericsson.com, csp@csperkins.org
  RFC7202          ||      C. Perkins, M. Westerlund         ||       csp@csperkins.org, magnus.westerlund@ericsson.com
  RFC7203          ||      T. Takahashi, K. Landfield, Y. Kadobayashi         ||       takeshi_takahashi@nict.go.jp, kent_landfield@mcafee.com, youki-k@is.aist-nara.ac.jp
  RFC7204          ||      T. Haynes         ||       tdh@excfb.com
  RFC7205          ||      A. Romanow, S. Botzko, M. Duckworth, R. Even, Ed.         ||       allyn@cisco.com, stephen.botzko@polycom.com, mark.duckworth@polycom.com, roni.even@mail01.huawei.com
  RFC7206          ||      P. Jones, G. Salgueiro, J. Polk, L. Liess, H. Kaplan         ||       paulej@packetizer.com, gsalguei@cisco.com, jmpolk@cisco.com, laura.liess.dt@gmail.com, hadriel.kaplan@oracle.com
  RFC7207          ||      M. Ortseifen, G. Dickfeld         ||       iso20022@bundesbank.de, iso20022@bundesbank.de
  RFC7208          ||      S. Kitterman         ||       scott@kitterman.com
  RFC7209          ||      A. Sajassi, R. Aggarwal, J. Uttaro, N. Bitar, W. Henderickx, A. Isaac         ||       sajassi@cisco.com, raggarwa_1@yahoo.com, uttaro@att.com, nabil.n.bitar@verizon.com, wim.henderickx@alcatel-lucent.com, aisaac71@bloomberg.net
  RFC7210          ||      R. Housley, T. Polk, S. Hartman, D. Zhang         ||       housley@vigilsec.com, tim.polk@nist.gov, hartmans-ietf@mit.edu, zhangdacheng@huawei.com
  RFC7211          ||      S. Hartman, D. Zhang         ||       hartmans-ietf@mit.edu, zhangdacheng@huawei.com
  RFC7212          ||      D. Frost, S. Bryant, M. Bocci         ||       frost@mm.st, stbryant@cisco.com, matthew.bocci@alcatel-lucent.com
  RFC7213          ||      D. Frost, S. Bryant, M. Bocci         ||       frost@mm.st, stbryant@cisco.com, matthew.bocci@alcatel-lucent.com
  RFC7214          ||      L. Andersson, C. Pignataro         ||       loa@mail01.huawei.com, cpignata@cisco.com
  RFC7215          ||      L. Jakab, A. Cabellos-Aparicio, F. Coras, J. Domingo-Pascual, D. Lewis         ||       lojakab@cisco.com, acabello@ac.upc.edu, fcoras@ac.upc.edu, jordi.domingo@ac.upc.edu, darlewis@cisco.com
  RFC7216          ||      M. Thomson, R. Bellis         ||       martin.thomson@gmail.com, ray.bellis@nominet.org.uk
  RFC7217          ||      F. Gont         ||       fgont@si6networks.com
  RFC7218          ||      O. Gudmundsson         ||       ogud@ogud.com
  RFC7219          ||      M. Bagnulo, A. Garcia-Martinez         ||       marcelo@it.uc3m.es, alberto@it.uc3m.es
  RFC7220          ||      M. Boucadair, R. Penno, D. Wing         ||       mohamed.boucadair@orange.com, repenno@cisco.com, dwing-ietf@fuggles.com
  RFC7221          ||      A. Farrel, D. Crocker, Ed.         ||       adrian@olddog.co.uk, dcrocker@bbiw.net
  RFC7222          ||      M. Liebsch, P. Seite, H. Yokota, J. Korhonen, S. Gundavelli         ||       liebsch@neclab.eu, pierrick.seite@orange.com, yokota@kddilabs.jp, jouni.nospam@gmail.com, sgundave@cisco.com
  RFC7223          ||      M. Bjorklund         ||       mbj@tail-f.com
  RFC7224          ||      M. Bjorklund         ||       mbj@tail-f.com
  RFC7225          ||      M. Boucadair         ||       mohamed.boucadair@orange.com
  RFC7226          ||      C. Villamizar, Ed., D. McDysan, Ed., S. Ning, A. Malis, L. Yong         ||       curtis@occnc.com, dave.mcdysan@verizon.com, ning.so@tatacommunications.com, agmalis@gmail.com, lucy.yong@huawei.com
  RFC7227          ||      D. Hankins, T. Mrugalski, M. Siodelski, S. Jiang, S. Krishnan         ||       dhankins@google.com, tomasz.mrugalski@gmail.com, msiodelski@gmail.com, jiangsheng@huawei.com, suresh.krishnan@ericsson.com
  RFC7228          ||      C. Bormann, M. Ersue, A. Keranen         ||       cabo@tzi.org, mehmet.ersue@nsn.com, ari.keranen@ericsson.com
  RFC7229          ||      R. Housley         ||       housley@vigilsec.com
  RFC7230          ||      R. Fielding, Ed., J. Reschke, Ed.         ||       fielding@gbiv.com, julian.reschke@greenbytes.de
  RFC7231          ||      R. Fielding, Ed., J. Reschke, Ed.         ||       fielding@gbiv.com, julian.reschke@greenbytes.de
  RFC7232          ||      R. Fielding, Ed., J. Reschke, Ed.         ||       fielding@gbiv.com, julian.reschke@greenbytes.de
  RFC7233          ||      R. Fielding, Ed., Y. Lafon, Ed., J. Reschke, Ed.         ||       fielding@gbiv.com, ylafon@w3.org, julian.reschke@greenbytes.de
  RFC7234          ||      R. Fielding, Ed., M. Nottingham, Ed., J. Reschke, Ed.         ||       fielding@gbiv.com, mnot@mnot.net, julian.reschke@greenbytes.de
  RFC7235          ||      R. Fielding, Ed., J. Reschke, Ed.         ||       fielding@gbiv.com, julian.reschke@greenbytes.de
  RFC7236          ||      J. Reschke         ||       julian.reschke@greenbytes.de
  RFC7237          ||      J. Reschke         ||       julian.reschke@greenbytes.de
  RFC7238          ||      J. Reschke         ||       julian.reschke@greenbytes.de
  RFC7239          ||      A. Petersson, M. Nilsson         ||       andreas@sbin.se, nilsson@opera.com
  RFC7240          ||      J. Snell         ||       jasnell@gmail.com
  RFC7241          ||      S. Dawkins, P. Thaler, D. Romascanu, B. Aboba, Ed.         ||       spencerdawkins.ietf@gmail.com, pthaler@broadcom.com, dromasca@gmail.com , bernard_aboba@hotmail.com
  RFC7242          ||      M. Demmer, J. Ott, S. Perreault         ||       demmer@cs.berkeley.edu, jo@netlab.tkk.fi, simon@per.reau.lt
  RFC7243          ||      V. Singh, Ed., J. Ott, I. Curcio         ||       varun@comnet.tkk.fi, jo@comnet.tkk.fi, igor.curcio@nokia.com
  RFC7244          ||      H. Asaeda, Q. Wu, R. Huang         ||       asaeda@nict.go.jp, bill.wu@huawei.com, Rachel@huawei.com
  RFC7245          ||      A. Hutton, Ed., L. Portman, Ed., R. Jain, K. Rehor         ||       andrew.hutton@unify.com, leon.portman@gmail.com, rajnish.jain@outlook.com, krehor@cisco.com
  RFC7246          ||      IJ. Wijnands, Ed., P. Hitchen, N. Leymann, W. Henderickx, A. Gulko, J. Tantsura         ||       ice@cisco.com, paul.hitchen@bt.com, n.leymann@telekom.de, wim.henderickx@alcatel-lucent.com, arkadiy.gulko@thomsonreuters.com, jeff.tantsura@ericsson.com
  RFC7247          ||      P. Saint-Andre, A. Houri, J. Hildebrand         ||       ietf@stpeter.im, avshalom@il.ibm.com, jhildebr@cisco.com
  RFC7248          ||      P. Saint-Andre, A. Houri, J. Hildebrand         ||       ietf@stpeter.im, avshalom@il.ibm.com, jhildebr@cisco.com
  RFC7249          ||      R. Housley         ||       housley@vigilsec.com
  RFC7250          ||      P. Wouters, Ed., H. Tschofenig, Ed., J. Gilmore, S. Weiler, T. Kivinen         ||       pwouters@redhat.com, Hannes.Tschofenig@gmx.net, gnu@toad.com, weiler@tislabs.com, kivinen@iki.fi
  RFC7251          ||      D. McGrew, D. Bailey, M. Campagna, R. Dugal         ||       mcgrew@cisco.com, danbailey@sth.rub.de, mcampagna@gmail.com, rdugal@certicom.com
  RFC7252          ||      Z. Shelby, K. Hartke, C. Bormann         ||       zach.shelby@arm.com, hartke@tzi.org, cabo@tzi.org
  RFC7253          ||      T. Krovetz, P. Rogaway         ||       ted@krovetz.net, rogaway@cs.ucdavis.edu
  RFC7254          ||      M. Montemurro, Ed., A. Allen, D. McDonald, P. Gosden         ||       mmontemurro@blackberry.com, aallen@blackberry.com, david.mcdonald@meteor.ie, pgosden@gsma.com
  RFC7255          ||      A. Allen, Ed.         ||       aallen@blackberry.com
  RFC7256          ||      F. Le Faucheur, R. Maglione, T. Taylor         ||       flefauch@cisco.com, robmgl@cisco.com, tom.taylor.stds@gmail.com
  RFC7257          ||      T. Nadeau, Ed., A. Kiran Koushik, Ed., R. Mediratta, Ed.         ||       tnadeau@lucidvision.com, kkoushik@brocade.com, romedira@cisco.com
  RFC7258          ||      S. Farrell, H. Tschofenig         ||       stephen.farrell@cs.tcd.ie, Hannes.Tschofenig@gmx.net
  RFC7259          ||      P. Saint-Andre         ||       ietf@stpeter.im
  RFC7260          ||      A. Takacs, D. Fedyk, J. He         ||       attila.takacs@ericsson.com, don.fedyk@hp.com, hejia@huawei.com
  RFC7261          ||      M. Perumal, P. Ravindran         ||       mperumal@cisco.com, partha@parthasarathi.co.in
  RFC7262          ||      A. Romanow, S. Botzko, M. Barnes         ||       allyn@cisco.com, stephen.botzko@polycom.com, mary.ietf.barnes@gmail.com
  RFC7263          ||      N. Zong, X. Jiang, R. Even, Y. Zhang         ||       zongning@huawei.com, jiang.x.f@huawei.com, roni.even@mail01.huawei.com, hishigh@gmail.com
  RFC7264          ||      N. Zong, X. Jiang, R. Even, Y. Zhang         ||       zongning@huawei.com, jiang.x.f@huawei.com, roni.even@mail01.huawei.com, hishigh@gmail.com
  RFC7265          ||      P. Kewisch, C. Daboo, M. Douglass         ||       mozilla@kewis.ch, cyrus@daboo.name, douglm@rpi.edu
  RFC7266          ||      A. Clark, Q. Wu, R. Schott, G. Zorn         ||       alan.d.clark@telchemy.com, sunseawq@huawei.com, Roland.Schott@telekom.de, gwz@net-zen.net
  RFC7267          ||      L. Martini, Ed., M. Bocci, Ed., F. Balus, Ed.         ||       lmartini@cisco.com, matthew.bocci@alcatel-lucent.com, florin@nuagenetworks.net
  RFC7268          ||      B. Aboba, J. Malinen, P. Congdon, J. Salowey, M. Jones         ||       Bernard_Aboba@hotmail.com, j@w1.fi, paul.congdon@tallac.com, jsalowey@cisco.com, mark@azu.ca
  RFC7269          ||      G. Chen, Z. Cao, C. Xie, D. Binet         ||       chengang@chinamobile.com, caozhen@chinamobile.com, xiechf@ctbri.com.cn, david.binet@orange.com
  RFC7270          ||      A. Yourtchenko, P. Aitken, B. Claise         ||       ayourtch@cisco.com, paitken@cisco.com, bclaise@cisco.com
  RFC7271          ||      J. Ryoo, Ed., E. Gray, Ed., H. van Helvoort, A. D'Alessandro, T. Cheung, E. Osborne         ||       ryoo@etri.re.kr, eric.gray@ericsson.com, huub.van.helvoort@huawei.com, alessandro.dalessandro@telecomitalia.it, cts@etri.re.kr, eric.osborne@notcom.com
  RFC7272          ||      R. van Brandenburg, H. Stokking, O. van Deventer, F. Boronat, M. Montagud, K. Gross         ||       ray.vanbrandenburg@tno.nl, hans.stokking@tno.nl, oskar.vandeventer@tno.nl, fboronat@dcom.upv.es, mamontor@posgrado.upv.es, kevin.gross@avanw.com
  RFC7273          ||      A. Williams, K. Gross, R. van Brandenburg, H. Stokking         ||       aidan.williams@audinate.com, kevin.gross@avanw.com, ray.vanbrandenburg@tno.nl, hans.stokking@tno.nl
  RFC7274          ||      K. Kompella, L. Andersson, A. Farrel         ||       kireeti.kompella@gmail.com, loa@mail01.huawei.com, adrian@olddog.co.uk
  RFC7275          ||      L. Martini, S. Salam, A. Sajassi, M. Bocci, S. Matsushima, T. Nadeau         ||       lmartini@cisco.com, ssalam@cisco.com, sajassi@cisco.com, matthew.bocci@alcatel-lucent.com, satoru.matsushima@gmail.com, tnadeau@brocade.com
  RFC7276          ||      T. Mizrahi, N. Sprecher, E. Bellagamba, Y. Weingarten         ||       talmi@marvell.com, nurit.sprecher@nsn.com, elisa.bellagamba@ericsson.com, wyaacov@gmail.com
  RFC7277          ||      M. Bjorklund         ||       mbj@tail-f.com
  RFC7278          ||      C. Byrne, D. Drown, A. Vizdal         ||       cameron.byrne@t-mobile.com, dan@drown.org, ales.vizdal@t-mobile.cz
  RFC7279          ||      M. Shore, C. Pignataro         ||       melinda.shore@nomountain.net, cpignata@cisco.com
  RFC7280          ||      G. Fairhurst         ||       gorry@erg.abdn.ac.uk
  RFC7281          ||      A. Melnikov         ||       Alexey.Melnikov@isode.com
  RFC7282          ||      P. Resnick         ||       presnick@qti.qualcomm.com
  RFC7283          ||      Y. Cui, Q. Sun, T. Lemon         ||       yong@csnet1.cs.tsinghua.edu.cn, sunqi@csnet1.cs.tsinghua.edu.cn, Ted.Lemon@nominum.com
  RFC7284          ||      M. Lanthaler         ||       mail@markus-lanthaler.com
  RFC7285          ||      R. Alimi, Ed., R. Penno, Ed., Y. Yang, Ed., S. Kiesel, S. Previdi, W. Roome, S. Shalunov, R. Woundy         ||       ralimi@google.com, repenno@cisco.com, yry@cs.yale.edu, ietf-alto@skiesel.de, sprevidi@cisco.com, w.roome@alcatel-lucent.com, shalunov@shlang.com, Richard_Woundy@cable.comcast.com
  RFC7286          ||      S. Kiesel, M. Stiemerling, N. Schwan, M. Scharf, H. Song         ||       ietf-alto@skiesel.de, mls.ietf@gmail.com, ietf@nico-schwan.de, michael.scharf@alcatel-lucent.com, haibin.song@huawei.com
  RFC7287          ||      T. Schmidt, Ed., S. Gao, H. Zhang, M. Waehlisch         ||       Schmidt@informatik.haw-hamburg.de, shgao@bjtu.edu.cn, hkzhang@bjtu.edu.cn, mw@link-lab.net
  RFC7288          ||      D. Thaler         ||       dthaler@microsoft.com
  RFC7289          ||      V. Kuarsingh, Ed., J. Cianfarani         ||       victor@jvknet.com, john.cianfarani@rci.rogers.com
  RFC7290          ||      L. Ciavattone, R. Geib, A. Morton, M. Wieser         ||       lencia@att.com, Ruediger.Geib@telekom.de, acmorton@att.com, matthias_michael.wieser@stud.tu-darmstadt.de
  RFC7291          ||      M. Boucadair, R. Penno, D. Wing         ||       mohamed.boucadair@orange.com, repenno@cisco.com, dwing-ietf@fuggles.com
  RFC7292          ||      K. Moriarty, Ed., M. Nystrom, S. Parkinson, A. Rusch, M. Scott         ||       Kathleen.Moriarty@emc.com, mnystrom@microsoft.com, sean.parkinson@rsa.com, andreas.rusch@rsa.com, michael2.scott@rsa.com
  RFC7293          ||      W. Mills, M. Kucherawy         ||       wmills_92105@yahoo.com, msk@fb.com
  RFC7294          ||      A. Clark, G. Zorn, C. Bi, Q. Wu         ||       alan.d.clark@telchemy.com, gwz@net-zen.net, bijy@sttri.com.cn, sunseawq@huawei.com
  RFC7295          ||      H. Tschofenig, L. Eggert, Z. Sarker         ||       Hannes.Tschofenig@gmx.net, lars@netapp.com, Zaheduzzaman.Sarker@ericsson.com
  RFC7296          ||      C. Kaufman, P. Hoffman, Y. Nir, P. Eronen, T. Kivinen         ||       charliekaufman@outlook.com, paul.hoffman@vpnc.org, nir.ietf@gmail.com, pe@iki.fi, kivinen@iki.fi
  RFC7297          ||      M. Boucadair, C. Jacquenet, N. Wang         ||       mohamed.boucadair@orange.com, christian.jacquenet@orange.com, n.wang@surrey.ac.uk
  RFC7298          ||      D. Ovsienko         ||       infrastation@yandex.ru
  RFC7299          ||      R. Housley         ||       housley@vigilsec.com
  RFC7300          ||      J. Haas, J. Mitchell         ||       jhaas@juniper.net, jon.mitchell@microsoft.com
  RFC7301          ||      S. Friedl, A. Popov, A. Langley, E. Stephan         ||       sfriedl@cisco.com, andreipo@microsoft.com, agl@google.com, emile.stephan@orange.com
  RFC7302          ||      P. Lemieux         ||       pal@sandflow.com
  RFC7303          ||      H. Thompson, C. Lilley         ||       ht@inf.ed.ac.uk, chris@w3.org
  RFC7304          ||      W. Kumari         ||       warren@kumari.net
  RFC7305          ||      E. Lear, Ed.         ||       lear@cisco.com
  RFC7306          ||      H. Shah, F. Marti, W. Noureddine, A. Eiriksson, R. Sharp         ||       hemal@broadcom.com, felix@chelsio.com, asgeir@chelsio.com, wael@chelsio.com, robert.o.sharp@intel.com
  RFC7307          ||      Q. Zhao, K. Raza, C. Zhou, L. Fang, L. Li, D. King         ||       quintin.zhao@huawei.com, skraza@cisco.com, czhou@cisco.com, lufang@microsoft.com, lilianyuan@chinamobile.com, daniel@olddog.co.uk
  RFC7308          ||      E. Osborne         ||       none
  RFC7309          ||      Z. Liu, L. Jin, R. Chen, D. Cai, S. Salam         ||       zhliu@gsta.com, lizho.jin@gmail.com, chen.ran@zte.com.cn, dcai@cisco.com, ssalam@cisco.com
  RFC7310          ||      J. Lindsay, H. Foerster         ||       lindsay@worldcastsystems.com, foerster@worldcastsystems.com
  RFC7311          ||      P. Mohapatra, R. Fernando, E. Rosen, J. Uttaro         ||       mpradosh@yahoo.com, rex@cisco.com, erosen@cisco.com, uttaro@att.com
  RFC7312          ||      J. Fabini, A. Morton         ||       joachim.fabini@tuwien.ac.at, acmorton@att.com
  RFC7313          ||      K. Patel, E. Chen, B. Venkatachalapathy         ||       keyupate@cisco.com, enkechen@cisco.com, balaji_pv@hotmail.com
  RFC7314          ||      M. Andrews         ||       marka@isc.org
  RFC7315          ||      R. Jesske, K. Drage, C. Holmberg         ||       r.jesske@telekom.de, drage@alcatel-lucent.com, christer.holmberg@ericsson.com
  RFC7316          ||      J. van Elburg, K. Drage, M. Ohsugi, S. Schubert, K. Arai         ||       ietf.hanserik@gmail.com, drage@alcatel-lucent.com, mayumi.ohsugi@ntt-at.co.jp, shida@ntt-at.com, arai.kenjiro@lab.ntt.co.jp
  RFC7317          ||      A. Bierman, M. Bjorklund         ||       andy@yumaworks.com, mbj@tail-f.com
  RFC7318          ||      A. Newton, G. Huston         ||       andy@arin.net, gih@apnic.net
  RFC7319          ||      D. Eastlake 3rd         ||       d3e3e3@gmail.com
  RFC7320          ||      M. Nottingham         ||       mnot@mnot.net
  RFC7321          ||      D. McGrew, P. Hoffman         ||       mcgrew@cisco.com, paul.hoffman@vpnc.org
  RFC7322          ||      H. Flanagan, S. Ginoza         ||       rse@rfc-editor.org, rfc-editor@rfc-editor.org
  RFC7323          ||      D. Borman, B. Braden, V. Jacobson, R. Scheffenegger, Ed.         ||       david.borman@quantum.com, braden@isi.edu, vanj@google.com, rs@netapp.com
  RFC7324          ||      E. Osborne         ||       eric.osborne@notcom.com
  RFC7325          ||      C. Villamizar, Ed., K. Kompella, S. Amante, A. Malis, C. Pignataro         ||       curtis@occnc.com, kireeti@juniper.net, amante@apple.com, agmalis@gmail.com, cpignata@cisco.com
  RFC7326          ||      J. Parello, B. Claise, B. Schoening, J. Quittek         ||       jparello@cisco.com, bclaise@cisco.com, brad.schoening@verizon.net, quittek@netlab.nec.de
  RFC7328          ||      R. Gieben         ||       miek@google.com
  RFC7329          ||      H. Kaplan         ||       hadrielk@yahoo.com
  RFC7330          ||      T. Nadeau, Z. Ali, N. Akiya         ||       tnadeau@lucidvision.com, zali@cisco.com, nobo@cisco.com
  RFC7331          ||      T. Nadeau, Z. Ali, N. Akiya         ||       tnadeau@lucidvision.com, zali@cisco.com, nobo@cisco.com
  RFC7332          ||      H. Kaplan, V. Pascual         ||       hadrielk@yahoo.com, victor.pascual@quobis.com
  RFC7333          ||      H. Chan, Ed., D. Liu, P. Seite, H. Yokota, J. Korhonen         ||       h.a.chan@ieee.org, liudapeng@chinamobile.com, pierrick.seite@orange.com, hidetoshi.yokota@landisgyr.com, jouni.nospam@gmail.com
  RFC7334          ||      Q. Zhao, D. Dhody, D. King, Z. Ali, R. Casellas         ||       quintin.zhao@huawei.com, dhruv.dhody@huawei.com, daniel@olddog.co.uk, zali@cisco.com, ramon.casellas@cttc.es
  RFC7335          ||      C. Byrne         ||       cameron.byrne@t-mobile.com
  RFC7336          ||      L. Peterson, B. Davie, R. van Brandenburg, Ed.         ||       lapeters@akamai.com, bdavie@vmware.com, ray.vanbrandenburg@tno.nl
  RFC7337          ||      K. Leung, Ed., Y. Lee, Ed.         ||       kleung@cisco.com, yiu_lee@cable.comcast.com
  RFC7338          ||      F. Jounay, Ed., Y. Kamite, Ed., G. Heron, M. Bocci         ||       frederic.jounay@orange.ch, y.kamite@ntt.com, giheron@cisco.com, Matthew.Bocci@alcatel-lucent.com
  RFC7339          ||      V. Gurbani, Ed., V. Hilt, H. Schulzrinne         ||       vkg@bell-labs.com, volker.hilt@bell-labs.com, hgs@cs.columbia.edu
  RFC7340          ||      J. Peterson, H. Schulzrinne, H. Tschofenig         ||       jon.peterson@neustar.biz, hgs@cs.columbia.edu, Hannes.Tschofenig@gmx.net
  RFC7341          ||      Q. Sun, Y. Cui, M. Siodelski, S. Krishnan, I. Farrer         ||       sunqi@csnet1.cs.tsinghua.edu.cn, yong@csnet1.cs.tsinghua.edu.cn, msiodelski@gmail.com, suresh.krishnan@ericsson.com, ian.farrer@telekom.de
  RFC7342          ||      L. Dunbar, W. Kumari, I. Gashinsky         ||       ldunbar@huawei.com, warren@kumari.net, igor@yahoo-inc.com
  RFC7343          ||      J. Laganier, F. Dupont         ||       julien.ietf@gmail.com, fdupont@isc.org
  RFC7344          ||      W. Kumari, O. Gudmundsson, G. Barwood         ||       warren@kumari.net, ogud@ogud.com, george.barwood@blueyonder.co.uk
  RFC7345          ||      C. Holmberg, I. Sedlacek, G. Salgueiro         ||       christer.holmberg@ericsson.com, ivo.sedlacek@ericsson.com, gsalguei@cisco.com
  RFC7346          ||      R. Droms         ||       rdroms.ietf@gmail.com
  RFC7347          ||      H. van Helvoort, Ed., J. Ryoo, Ed., H. Zhang, F. Huang, H. Li, A. D'Alessandro         ||       huub@van-helvoort.eu, ryoo@etri.re.kr, zhanghaiyan@huawei.com, feng.huang@philips.com, lihan@chinamobile.com, alessandro.dalessandro@telecomitalia.it
  RFC7348          ||      M. Mahalingam, D. Dutt, K. Duda, P. Agarwal, L. Kreeger, T. Sridhar, M. Bursell, C. Wright         ||       mallik_mahalingam@yahoo.com, ddutt.ietf@hobbesdutt.com, kduda@arista.com, pagarwal@broadcom.com, kreeger@cisco.com, tsridhar@vmware.com, mike.bursell@intel.com, chrisw@redhat.com
  RFC7349          ||      L. Zheng, M. Chen, M. Bhatia         ||       vero.zheng@huawei.com, mach.chen@huawei.com, manav@ionosnetworks.com
  RFC7350          ||      M. Petit-Huguenin, G. Salgueiro         ||       marcph@getjive.com, gsalguei@cisco.com
  RFC7351          ||      E. Wilde         ||       dret@berkeley.edu
  RFC7352          ||      S. Bosch         ||       stephan@rename-it.nl
  RFC7353          ||      S. Bellovin, R. Bush, D. Ward         ||       bellovin@acm.org, randy@psg.com, dward@cisco.com
  RFC7354          ||      A. Adolf, P. Siebert         ||       alexander.adolf@condition-alpha.com, dvb@dvb.org
  RFC7355          ||      G. Salgueiro, V. Pascual, A. Roman, S. Garcia         ||       gsalguei@cisco.com, victor.pascual@quobis.com, anton.roman@quobis.com, sergio.garcia@quobis.com
  RFC7356          ||      L. Ginsberg, S. Previdi, Y. Yang         ||       ginsberg@cisco.com, sprevidi@cisco.com, yiya@cisco.com
  RFC7357          ||      H. Zhai, F. Hu, R. Perlman, D. Eastlake 3rd, O. Stokes         ||       zhai.hongjun@zte.com.cn, hu.fangwei@zte.com.cn, Radia@alum.mit.edu, d3e3e3@gmail.com, ostokes@extremenetworks.com
  RFC7358          ||      K. Raza, S. Boutros, L. Martini, N. Leymann         ||       skraza@cisco.com, sboutros@cisco.com, lmartini@cisco.com, n.leymann@telekom.de
  RFC7359          ||      F. Gont         ||       fgont@si6networks.com
  RFC7360          ||      A. DeKok         ||       aland@freeradius.org
  RFC7361          ||      P. Dutta, F. Balus, O. Stokes, G. Calvignac, D. Fedyk         ||       pranjal.dutta@alcatel-lucent.com, florin.balus@alcatel-lucent.com, ostokes@extremenetworks.com, geraldine.calvignac@orange.com, don.fedyk@hp.com
  RFC7362          ||      E. Ivov, H. Kaplan, D. Wing         ||       emcho@jitsi.org, hadrielk@yahoo.com, dwing-ietf@fuggles.com
  RFC7363          ||      J. Maenpaa, G. Camarillo         ||       Jouni.Maenpaa@ericsson.com, Gonzalo.Camarillo@ericsson.com
  RFC7364          ||      T. Narten, Ed., E. Gray, Ed., D. Black, L. Fang, L. Kreeger, M. Napierala         ||       narten@us.ibm.com, Eric.Gray@Ericsson.com, david.black@emc.com, lufang@microsoft.com, kreeger@cisco.com, mnapierala@att.com
  RFC7365          ||      M. Lasserre, F. Balus, T. Morin, N. Bitar, Y. Rekhter         ||       marc.lasserre@alcatel-lucent.com, florin.balus@alcatel-lucent.com, thomas.morin@orange.com, nabil.n.bitar@verizon.com, yakov@juniper.net
  RFC7366          ||      P. Gutmann         ||       pgut001@cs.auckland.ac.nz
  RFC7367          ||      R. Cole, J. Macker, B. Adamson         ||       robert.g.cole@us.army.mil, macker@itd.nrl.navy.mil, adamson@itd.nrl.navy.mil
  RFC7368          ||      T. Chown, Ed., J. Arkko, A. Brandt, O. Troan, J. Weil         ||       tjc@ecs.soton.ac.uk, jari.arkko@piuha.net, Anders_Brandt@sigmadesigns.com, ot@cisco.com, jason.weil@twcable.com
  RFC7369          ||      A. Takacs, B. Gero, H. Long         ||       attila.takacs@ericsson.com, balazs.peter.gero@ericsson.com, lonho@huawei.com
  RFC7370          ||      L. Ginsberg         ||       ginsberg@cisco.com
  RFC7371          ||      M. Boucadair, S. Venaas         ||       mohamed.boucadair@orange.com, stig@cisco.com
  RFC7372          ||      M. Kucherawy         ||       superuser@gmail.com
  RFC7373          ||      B. Trammell         ||       ietf@trammell.ch
  RFC7374          ||      J. Maenpaa, G. Camarillo         ||       Jouni.Maenpaa@ericsson.com, gonzalo.camarillo@ericsson.com
  RFC7375          ||      J. Peterson         ||       jon.peterson@neustar.biz
  RFC7376          ||      T. Reddy, R. Ravindranath, M. Perumal, A. Yegin         ||       tireddy@cisco.com, rmohanr@cisco.com, muthu.arul@gmail.com, alper.yegin@yegin.org
  RFC7377          ||      B. Leiba, A. Melnikov         ||       barryleiba@computer.org, alexey.melnikov@isode.com
  RFC7378          ||      H. Tschofenig, H. Schulzrinne, B. Aboba, Ed.         ||       Hannes.Tschofenig@gmx.net, hgs@cs.columbia.edu, Bernard_Aboba@hotmail.com
  RFC7379          ||      Y. Li, W. Hao, R. Perlman, J. Hudson, H. Zhai         ||       liyizhou@huawei.com, haoweiguo@huawei.com, radia@alum.mit.edu, jon.hudson@gmail.com, honjun.zhai@tom.com
  RFC7380          ||      J. Tong, C. Bi, Ed., R. Even, Q. Wu, Ed., R. Huang         ||       tongjg@sttri.com.cn, bijy@sttri.com.cn, roni.even@mail01.huawei.com, bill.wu@huawei.com, rachel.huang@huawei.com
  RFC7381          ||      K. Chittimaneni, T. Chown, L. Howard, V. Kuarsingh, Y. Pouffary, E. Vyncke         ||       kk@dropbox.com, tjc@ecs.soton.ac.uk, lee.howard@twcable.com, victor@jvknet.com, yanick.pouffary@hp.com, evyncke@cisco.com
  RFC7382          ||      S. Kent, D. Kong, K. Seo         ||       skent@bbn.com, dkong@bbn.com, kseo@bbn.com
  RFC7383          ||      V. Smyslov         ||       svan@elvis.ru
  RFC7384          ||      T. Mizrahi         ||       talmi@marvell.com
  RFC7385          ||      L. Andersson, G. Swallow         ||       loa@mail01.huawei.com, swallow@cisco.com
  RFC7386          ||      P. Hoffman, J. Snell         ||       paul.hoffman@vpnc.org, jasnell@gmail.com
  RFC7387          ||      R. Key, Ed., L. Yong, Ed., S. Delord, F. Jounay, L. Jin         ||       raymond.key@ieee.org, lucy.yong@huawei.com, simon.delord@gmail.com, frederic.jounay@orange.ch, lizho.jin@gmail.com
  RFC7388          ||      J. Schoenwaelder, A. Sehgal, T. Tsou, C. Zhou         ||       j.schoenwaelder@jacobs-university.de, s.anuj@jacobs-university.de, tina.tsou.zouting@huawei.com, cathyzhou@huawei.com
  RFC7389          ||      R. Wakikawa, R. Pazhyannur, S. Gundavelli, C. Perkins         ||       ryuji.wakikawa@gmail.com, rpazhyan@cisco.com, sgundave@cisco.com, charliep@computer.org
  RFC7390          ||      A. Rahman, Ed., E. Dijk, Ed.         ||       Akbar.Rahman@InterDigital.com, esko.dijk@philips.com
  RFC7391          ||      J. Hadi Salim         ||       hadi@mojatatu.com
  RFC7392          ||      P. Dutta, M. Bocci, L. Martini         ||       pranjal.dutta@alcatel-lucent.com, matthew.bocci@alcatel-lucent.com, lmartini@cisco.com
  RFC7393          ||      X. Deng, M. Boucadair, Q. Zhao, J. Huang, C. Zhou         ||       dxhbupt@gmail.com, mohamed.boucadair@orange.com, zhaoqin.bupt@gmail.com, james.huang@huawei.com, cathy.zhou@huawei.com
  RFC7394          ||      S. Boutros, S. Sivabalan, G. Swallow, S. Saxena, V. Manral, S. Aldrin         ||       sboutros@cisco.com, msiva@cisco.com, swallow@cisco.com, ssaxena@cisco.com, vishwas@ionosnetworks.com, aldrin.ietf@gmail.com
  RFC7395          ||      L. Stout, Ed., J. Moffitt, E. Cestari         ||       lance@andyet.net, jack@metajack.im, eric@cstar.io
  RFC7396          ||      P. Hoffman, J. Snell         ||       paul.hoffman@vpnc.org, jasnell@gmail.com
  RFC7397          ||      J. Gilger, H. Tschofenig         ||       Gilger@ITSec.RWTH-Aachen.de, Hannes.tschofenig@gmx.net
  RFC7398          ||      M. Bagnulo, T. Burbridge, S. Crawford, P. Eardley, A. Morton         ||       marcelo@it.uc3m.es, trevor.burbridge@bt.com, sam@samknows.com, philip.eardley@bt.com, acmorton@att.com
  RFC7399          ||      A. Farrel, D. King         ||       adrian@olddog.co.uk, daniel@olddog.co.uk
  RFC7400          ||      C. Bormann         ||       cabo@tzi.org
  RFC7401          ||      R. Moskowitz, Ed., T. Heer, P. Jokela, T. Henderson         ||       rgm@labs.htt-consult.com, tobias.heer@belden.com, petri.jokela@nomadiclab.com, tomhend@u.washington.edu
  RFC7402          ||      P. Jokela, R. Moskowitz, J. Melen         ||       petri.jokela@nomadiclab.com, rgm@labs.htt-consult.com, jan.melen@nomadiclab.com
  RFC7403          ||      H. Kaplan         ||       hadrielk@yahoo.com
  RFC7404          ||      M. Behringer, E. Vyncke         ||       mbehring@cisco.com, evyncke@cisco.com
  RFC7405          ||      P. Kyzivat         ||       pkyzivat@alum.mit.edu
  RFC7406          ||      H. Schulzrinne, S. McCann, G. Bajko, H. Tschofenig, D. Kroeselberg         ||       hgs+ecrit@cs.columbia.edu, smccann@blackberry.com, gabor.bajko@mediatek.com, Hannes.Tschofenig@gmx.net, dirk.kroeselberg@siemens.com
  RFC7407          ||      M. Bjorklund, J. Schoenwaelder         ||       mbj@tail-f.com, j.schoenwaelder@jacobs-university.de
  RFC7408          ||      E. Haleplidis         ||       ehalep@ece.upatras.gr
  RFC7409          ||      E. Haleplidis, J. Halpern         ||       ehalep@ece.upatras.gr, joel.halpern@ericsson.com
  RFC7410          ||      M. Kucherawy         ||       superuser@gmail.com
  RFC7411          ||      T. Schmidt, Ed., M. Waehlisch, R. Koodli, G. Fairhurst, D. Liu         ||       t.schmidt@haw-hamburg.de, mw@link-lab.net, rajeev.koodli@intel.com, gorry@erg.abdn.ac.uk, liudapeng@chinamobile.com
  RFC7412          ||      Y. Weingarten, S. Aldrin, P. Pan, J. Ryoo, G. Mirsky         ||       wyaacov@gmail.com, aldrin.ietf@gmail.com, ppan@infinera.com, ryoo@etri.re.kr, gregory.mirsky@ericsson.com
  RFC7413          ||      Y. Cheng, J. Chu, S. Radhakrishnan, A. Jain         ||       ycheng@google.com, hkchu@google.com, sivasankar@cs.ucsd.edu, arvind@google.com
  RFC7414          ||      M. Duke, R. Braden, W. Eddy, E. Blanton, A. Zimmermann         ||       m.duke@f5.com, braden@isi.edu, wes@mti-systems.com, elb@interruptsciences.com, alexander.zimmermann@netapp.com
  RFC7415          ||      E. Noel, P. Williams         ||       ecnoel@att.com, phil.m.williams@bt.com
  RFC7416          ||      T. Tsao, R. Alexander, M. Dohler, V. Daza, A. Lozano, M. Richardson, Ed.         ||       tzetatsao@eaton.com, rogeralexander@eaton.com, mischa.dohler@kcl.ac.uk, vanesa.daza@upf.edu, angel.lozano@upf.edu, mcr+ietf@sandelman.ca
  RFC7417          ||      G. Karagiannis, A. Bhargava         ||       georgios.karagiannis@huawei.com, anuragb@cisco.com
  RFC7418          ||      S. Dawkins, Ed.         ||       spencerdawkins.ietf@gmail.com
  RFC7419          ||      N. Akiya, M. Binderberger, G. Mirsky         ||       nobo@cisco.com, mbinderb@cisco.com, gregory.mirsky@ericsson.com
  RFC7420          ||      A. Koushik, E. Stephan, Q. Zhao, D. King, J. Hardwick         ||       kkoushik@brocade.com, emile.stephan@orange.com, qzhao@huawei.com, daniel@olddog.co.uk, jonathan.hardwick@metaswitch.com
  RFC7421          ||      B. Carpenter, Ed., T. Chown, F. Gont, S. Jiang, A. Petrescu, A. Yourtchenko         ||       brian.e.carpenter@gmail.com, tjc@ecs.soton.ac.uk, fgont@si6networks.com, jiangsheng@huawei.com, alexandru.petrescu@cea.fr, ayourtch@cisco.com
  RFC7422          ||      C. Donley, C. Grundemann, V. Sarawat, K. Sundaresan, O. Vautrin         ||       c.donley@cablelabs.com, cgrundemann@gmail.com, v.sarawat@cablelabs.com, k.sundaresan@cablelabs.com, Olivier@juniper.net
  RFC7423          ||      L. Morand, Ed., V. Fajardo, H. Tschofenig         ||       lionel.morand@orange.com, vf0213@gmail.com, Hannes.Tschofenig@gmx.net
  RFC7424          ||      R. Krishnan, L. Yong, A. Ghanwani, N. So, B. Khasnabish         ||       ramkri123@gmail.com, lucy.yong@huawei.com, anoop@alumni.duke.edu, ningso@yahoo.com, vumip1@gmail.com
  RFC7425          ||      M. Thornburgh         ||       mthornbu@adobe.com
  RFC7426          ||      E. Haleplidis, Ed., K. Pentikousis, Ed., S. Denazis, J. Hadi Salim, D. Meyer, O. Koufopavlou         ||       ehalep@ece.upatras.gr, k.pentikousis@eict.de, sdena@upatras.gr, hadi@mojatatu.com, dmm@1-4-5.net, odysseas@ece.upatras.gr
  RFC7427          ||      T. Kivinen, J. Snyder         ||       kivinen@iki.fi, jms@opus1.com
  RFC7428          ||      A. Brandt, J. Buron         ||       anders_brandt@sigmadesigns.com, jakob_buron@sigmadesigns.com
  RFC7429          ||      D. Liu, Ed., JC. Zuniga, Ed., P. Seite, H. Chan, CJ. Bernardos         ||       liudapeng@chinamobile.com, JuanCarlos.Zuniga@InterDigital.com, pierrick.seite@orange.com, h.a.chan@ieee.org, cjbc@it.uc3m.es
  RFC7430          ||      M. Bagnulo, C. Paasch, F. Gont, O. Bonaventure, C. Raiciu         ||       marcelo@it.uc3m.es, christoph.paasch@gmail.com, fgont@si6networks.com, Olivier.Bonaventure@uclouvain.be, costin.raiciu@cs.pub.ro
  RFC7431          ||      A. Karan, C. Filsfils, IJ. Wijnands, Ed., B. Decraene         ||       apoorva@cisco.com, cfilsfil@cisco.com, ice@cisco.com, bruno.decraene@orange.com
  RFC7432          ||      A. Sajassi, Ed., R. Aggarwal, N. Bitar, A. Isaac, J. Uttaro, J. Drake, W. Henderickx         ||       sajassi@cisco.com, raggarwa_1@yahoo.com, nabil.n.bitar@verizon.com, aisaac71@bloomberg.net, uttaro@att.com, jdrake@juniper.net, wim.henderickx@alcatel-lucent.com
  RFC7433          ||      A. Johnston, J. Rafferty         ||       alan.b.johnston@gmail.com, jay@humancomm.com
  RFC7434          ||      K. Drage, Ed., A. Johnston         ||       keith.drage@alcatel-lucent.com, alan.b.johnston@gmail.com
  RFC7435          ||      V. Dukhovni         ||       ietf-dane@dukhovni.org
  RFC7436          ||      H. Shah, E. Rosen, F. Le Faucheur, G. Heron         ||       hshah@ciena.com, erosen@juniper.net, flefauch@cisco.com, giheron@cisco.com
  RFC7437          ||      M. Kucherawy, Ed.         ||       superuser@gmail.com
  RFC7438          ||      IJ. Wijnands, Ed., E. Rosen, A. Gulko, U. Joorde, J. Tantsura         ||       ice@cisco.com, erosen@juniper.net, arkadiy.gulko@thomsonreuters.com, uwe.joorde@telekom.de, jeff.tantsura@ericsson.com
  RFC7439          ||      W. George, Ed., C. Pignataro, Ed.         ||       wesley.george@twcable.com, cpignata@cisco.com
  RFC7440          ||      P. Masotta         ||       patrick.masotta.ietf@vercot.com
  RFC7441          ||      IJ. Wijnands, E. Rosen, U. Joorde         ||       ice@cisco.com, erosen@juniper.net, uwe.joorde@telekom.de
  RFC7442          ||      Y. Rekhter, R. Aggarwal, N. Leymann, W. Henderickx, Q. Zhao, R. Li         ||       yakov@juniper.net, raggarwa_1@yahoo.com, N.Leymann@telekom.de, wim.henderickx@alcatel-lucent.com, quintin.zhao@huawei.com, renwei.li@huawei.com
  RFC7443          ||      P. Patil, T. Reddy, G. Salgueiro, M. Petit-Huguenin         ||       praspati@cisco.com, tireddy@cisco.com, gsalguei@cisco.com, marc@petit-huguenin.org
  RFC7444          ||      K. Zeilenga, A. Melnikov         ||       kurt.zeilenga@isode.com, alexey.melnikov@isode.com
  RFC7445          ||      G. Chen, H. Deng, D. Michaud, J. Korhonen, M. Boucadair         ||       phdgang@gmail.com, denghui@chinamobile.com, dave.michaud@rci.rogers.com, jouni.nospam@gmail.com, mohamed.boucadair@orange.com
  RFC7446          ||      Y. Lee, Ed., G. Bernstein, Ed., D. Li, W. Imajuku         ||       leeyoung@huawei.com, gregb@grotto-networking.com, danli@huawei.com, imajuku.wataru@lab.ntt.co.jp
  RFC7447          ||      J. Scudder, K. Kompella         ||       jgs@juniper.net, kireeti@juniper.net
  RFC7448          ||      T. Taylor, Ed., D. Romascanu         ||       tom.taylor.stds@gmail.com, dromasca@gmail.com 
  RFC7449          ||      Y. Lee, Ed., G. Bernstein, Ed., J. Martensson, T. Takeda, T. Tsuritani, O. Gonzalez de Dios         ||       leeyoung@huawei.com, gregb@grotto-networking.com, jonas.martensson@acreo.se, tomonori.takeda@ntt.com, tsuri@kddilabs.jp, oscar.gonzalezdedios@telefonica.com
  RFC7450          ||      G. Bumgardner         ||       gbumgard@gmail.com
  RFC7451          ||      S. Hollenbeck         ||       shollenbeck@verisign.com
  RFC7452          ||      H. Tschofenig, J. Arkko, D. Thaler, D. McPherson         ||       Hannes.Tschofenig@gmx.net, jari.arkko@piuha.net, dthaler@microsoft.com, dmcpherson@verisign.com
  RFC7453          ||      V. Mahalingam, K. Sampath, S. Aldrin, T. Nadeau         ||       venkat.mahalingams@gmail.com, kannankvs@gmail.com, aldrin.ietf@gmail.com, tnadeau@lucidvision.com
  RFC7454          ||      J. Durand, I. Pepelnjak, G. Doering         ||       jerduran@cisco.com, ip@ipspace.net, gert@space.net
  RFC7455          ||      T. Senevirathne, N. Finn, S. Salam, D. Kumar, D. Eastlake 3rd, S. Aldrin, Y. Li         ||       tsenevir@cisco.com, nfinn@cisco.com, ssalam@cisco.com, dekumar@cisco.com, d3e3e3@gmail.com, aldrin.ietf@gmail.com, liyizhou@huawei.com
  RFC7456          ||      T. Mizrahi, T. Senevirathne, S. Salam, D. Kumar, D. Eastlake 3rd         ||       talmi@marvell.com, tsenevir@cisco.com, ssalam@cisco.com, dekumar@cisco.com, d3e3e3@gmail.com
  RFC7457          ||      Y. Sheffer, R. Holz, P. Saint-Andre         ||       yaronf.ietf@gmail.com, holz@net.in.tum.de, peter@andyet.com
  RFC7458          ||      R. Valmikam, R. Koodli         ||       valmikam@gmail.com, rajeev.koodli@intel.com
  RFC7459          ||      M. Thomson, J. Winterbottom         ||       martin.thomson@gmail.com, a.james.winterbottom@gmail.com
  RFC7460          ||      M. Chandramouli, B. Claise, B. Schoening, J. Quittek, T. Dietz         ||       moulchan@cisco.com, bclaise@cisco.com, brad.schoening@verizon.net, quittek@neclab.eu, Thomas.Dietz@neclab.eu
  RFC7461          ||      J. Parello, B. Claise, M. Chandramouli         ||       jparello@cisco.com, bclaise@cisco.com, moulchan@cisco.com
  RFC7462          ||      L. Liess, Ed., R. Jesske, A. Johnston, D. Worley, P. Kyzivat         ||       laura.liess.dt@gmail.com, r.jesske@telekom.de, alan.b.johnston@gmail.com, worley@ariadne.com, pkyzivat@alum.mit.edu
  RFC7463          ||      A. Johnston, Ed., M. Soroushnejad, Ed., V. Venkataramanan         ||       alan.b.johnston@gmail.com, msoroush@gmail.com, vvenkatar@gmail.com
  RFC7464          ||      N. Williams         ||       nico@cryptonector.com
  RFC7465          ||      A. Popov         ||       andreipo@microsoft.com
  RFC7466          ||      C. Dearlove, T. Clausen         ||       chris.dearlove@baesystems.com, T.Clausen@computer.org
  RFC7467          ||      A. Murdock         ||       Aidan.murdock@ncia.nato.int
  RFC7468          ||      S. Josefsson, S. Leonard         ||       simon@josefsson.org, dev+ietf@seantek.com
  RFC7469          ||      C. Evans, C. Palmer, R. Sleevi         ||       cevans@google.com, palmer@google.com, sleevi@google.com
  RFC7470          ||      F. Zhang, A. Farrel         ||       zhangfatai@huawei.com, adrian@olddog.co.uk
  RFC7471          ||      S. Giacalone, D. Ward, J. Drake, A. Atlas, S. Previdi         ||       spencer.giacalone@gmail.com, dward@cisco.com, jdrake@juniper.net, akatlas@juniper.net, sprevidi@cisco.com
  RFC7472          ||      I. McDonald, M. Sweet         ||       blueroofmusic@gmail.com, msweet@apple.com
  RFC7473          ||      K. Raza, S. Boutros         ||       skraza@cisco.com, sboutros@cisco.com
  RFC7474          ||      M. Bhatia, S. Hartman, D. Zhang, A. Lindem, Ed.         ||       manav@ionosnetworks.com, hartmans-ietf@mit.edu, dacheng.zhang@gmail.com, acee@cisco.com
  RFC7475          ||      S. Dawkins         ||       spencerdawkins.ietf@gmail.com
  RFC7476          ||      K. Pentikousis, Ed., B. Ohlman, D. Corujo, G. Boggia, G. Tyson, E. Davies, A. Molinaro, S. Eum         ||       k.pentikousis@eict.de, Borje.Ohlman@ericsson.com, dcorujo@av.it.pt, g.boggia@poliba.it, gareth.tyson@eecs.qmul.ac.uk, davieseb@scss.tcd.ie, antonella.molinaro@unirc.it, suyong@nict.go.jp
  RFC7477          ||      W. Hardaker         ||       ietf@hardakers.net
  RFC7478          ||      C. Holmberg, S. Hakansson, G. Eriksson         ||       christer.holmberg@ericsson.com, stefan.lk.hakansson@ericsson.com, goran.ap.eriksson@ericsson.com
  RFC7479          ||      S. Moonesamy         ||       sm+ietf@elandsys.com
  RFC7480          ||      A. Newton, B. Ellacott, N. Kong         ||       andy@arin.net, bje@apnic.net, nkong@cnnic.cn
  RFC7481          ||      S. Hollenbeck, N. Kong         ||       shollenbeck@verisign.com, nkong@cnnic.cn
  RFC7482          ||      A. Newton, S. Hollenbeck         ||       andy@arin.net, shollenbeck@verisign.com
  RFC7483          ||      A. Newton, S. Hollenbeck         ||       andy@arin.net, shollenbeck@verisign.com
  RFC7484          ||      M. Blanchet         ||       Marc.Blanchet@viagenie.ca
  RFC7485          ||      L. Zhou, N. Kong, S. Shen, S. Sheng, A. Servin         ||       zhoulinlin@cnnic.cn, nkong@cnnic.cn, shenshuo@cnnic.cn, steve.sheng@icann.org, arturo.servin@gmail.com
  RFC7486          ||      S. Farrell, P. Hoffman, M. Thomas         ||       stephen.farrell@cs.tcd.ie, paul.hoffman@vpnc.org, mike@phresheez.com
  RFC7487          ||      E. Bellagamba, A. Takacs, G. Mirsky, L. Andersson, P. Skoldstrom, D. Ward         ||       elisa.bellagamba@ericsson.com, attila.takacs@ericsson.com, gregory.mirsky@ericsson.com, loa@mail01.huawei.com, pontus.skoldstrom@acreo.se, dward@cisco.com
  RFC7488          ||      M. Boucadair, R. Penno, D. Wing, P. Patil, T. Reddy         ||       mohamed.boucadair@orange.com, repenno@cisco.com, dwing-ietf@fuggles.com, praspati@cisco.com, tireddy@cisco.com
  RFC7489          ||      M. Kucherawy, Ed., E. Zwicky, Ed.         ||       superuser@gmail.com, zwicky@yahoo-inc.com
  RFC7490          ||      S. Bryant, C. Filsfils, S. Previdi, M. Shand, N. So         ||       stbryant@cisco.com, cfilsfil@cisco.com, sprevidi@cisco.com, imc.shand@gmail.com, ningso@vinci-systems.com
  RFC7491          ||      D. King, A. Farrel         ||       daniel@olddog.co.uk, adrian@olddog.co.uk
  RFC7492          ||      M. Bhatia, D. Zhang, M. Jethanandani         ||       manav@ionosnetworks.com, dacheng.zhang@gmail.com, mjethanandani@gmail.com
  RFC7493          ||      T. Bray, Ed.         ||       tbray@textuality.com
  RFC7494          ||      C. Shao, H. Deng, R. Pazhyannur, F. Bari, R. Zhang, S. Matsushima         ||       shaochunju@chinamobile.com, denghui@chinamobile.com, rpazhyan@cisco.com, farooq.bari@att.com, zhangr@gsta.com, satoru.matsushima@g.softbank.co.jp
  RFC7495          ||      A. Montville, D. Black         ||       adam.w.montville@gmail.com, david.black@emc.com
  RFC7496          ||      M. Tuexen, R. Seggelmann, R. Stewart, S. Loreto         ||       tuexen@fh-muenster.de, rfc@robin-seggelmann.com, randall@lakerest.net, Salvatore.Loreto@ericsson.com
  RFC7497          ||      A. Morton         ||       acmorton@att.com
  RFC7498          ||      P. Quinn, Ed., T. Nadeau, Ed.         ||       paulq@cisco.com, tnadeau@lucidvision.com
  RFC7499          ||      A. Perez-Mendez, Ed., R. Marin-Lopez, F. Pereniguez-Garcia, G. Lopez-Millan, D. Lopez, A. DeKok         ||       alex@um.es, rafa@um.es, pereniguez@um.es, gabilm@um.es, diego@tid.es, aland@networkradius.com
  RFC7500          ||      R. Housley, Ed., O. Kolkman, Ed.         ||       housley@vigilsec.com, kolkman@isoc.org
  RFC7501          ||      C. Davids, V. Gurbani, S. Poretsky         ||       davids@iit.edu, vkg@bell-labs.com, sporetsky@allot.com
  RFC7502          ||      C. Davids, V. Gurbani, S. Poretsky         ||       davids@iit.edu, vkg@bell-labs.com, sporetsky@allot.com
  RFC7503          ||      A. Lindem, J. Arkko         ||       acee@cisco.com, jari.arkko@piuha.net
  RFC7504          ||      J. Klensin         ||       john-ietf@jck.com
  RFC7505          ||      J. Levine, M. Delany         ||       standards@taugh.com, mx0dot@yahoo.com
  RFC7506          ||      K. Raza, N. Akiya, C. Pignataro         ||       skraza@cisco.com, nobo.akiya.dev@gmail.com, cpignata@cisco.com
  RFC7507          ||      B. Moeller, A. Langley         ||       bmoeller@acm.org, agl@google.com
  RFC7508          ||      L. Cailleux, C. Bonatti         ||       laurent.cailleux@intradef.gouv.fr, bonatti252@ieca.com
  RFC7509          ||      R. Huang, V. Singh         ||       rachel.huang@huawei.com, varun@comnet.tkk.fi
  RFC7510          ||      X. Xu, N. Sheth, L. Yong, R. Callon, D. Black         ||       xuxiaohu@huawei.com, nsheth@juniper.net, lucy.yong@huawei.com, rcallon@juniper.net, david.black@emc.com
  RFC7511          ||      M. Wilhelm         ||       max@rfc2324.org
  RFC7512          ||      J. Pechanec, D. Moffat         ||       Jan.Pechanec@Oracle.COM, Darren.Moffat@Oracle.COM
  RFC7513          ||      J. Bi, J. Wu, G. Yao, F. Baker         ||       junbi@tsinghua.edu.cn, jianping@cernet.edu.cn, yaoguang@cernet.edu.cn, fred@cisco.com
  RFC7514          ||      M. Luckie         ||       mjl@caida.org
  RFC7515          ||      M. Jones, J. Bradley, N. Sakimura         ||       mbj@microsoft.com, ve7jtb@ve7jtb.com, n-sakimura@nri.co.jp
  RFC7516          ||      M. Jones, J. Hildebrand         ||       mbj@microsoft.com, jhildebr@cisco.com
  RFC7517          ||      M. Jones         ||       mbj@microsoft.com
  RFC7518          ||      M. Jones         ||       mbj@microsoft.com
  RFC7519          ||      M. Jones, J. Bradley, N. Sakimura         ||       mbj@microsoft.com, ve7jtb@ve7jtb.com, n-sakimura@nri.co.jp
  RFC7520          ||      M. Miller         ||       mamille2@cisco.com
  RFC7521          ||      B. Campbell, C. Mortimore, M. Jones, Y. Goland         ||       brian.d.campbell@gmail.com, cmortimore@salesforce.com, mbj@microsoft.com, yarong@microsoft.com
  RFC7522          ||      B. Campbell, C. Mortimore, M. Jones         ||       brian.d.campbell@gmail.com, cmortimore@salesforce.com, mbj@microsoft.com
  RFC7523          ||      M. Jones, B. Campbell, C. Mortimore         ||       mbj@microsoft.com, brian.d.campbell@gmail.com, cmortimore@salesforce.com
  RFC7524          ||      Y. Rekhter, E. Rosen, R. Aggarwal, T. Morin, I. Grosclaude, N. Leymann, S. Saad         ||       yakov@juniper.net, erosen@juniper.net, raggarwa_1@yahoo.com, thomas.morin@orange.com, irene.grosclaude@orange.com, n.leymann@telekom.de, samirsaad1@outlook.com
  RFC7525          ||      Y. Sheffer, R. Holz, P. Saint-Andre         ||       yaronf.ietf@gmail.com, ralph.ietf@gmail.com, peter@andyet.com
  RFC7526          ||      O. Troan, B. Carpenter, Ed.         ||       ot@cisco.com, brian.e.carpenter@gmail.com
  RFC7527          ||      R. Asati, H. Singh, W. Beebee, C. Pignataro, E. Dart, W. George         ||       rajiva@cisco.com, shemant@cisco.com, wbeebee@cisco.com, cpignata@cisco.com, dart@es.net, wesley.george@twcable.com
  RFC7528          ||      P. Higgs, J. Piesing         ||       paul.higgs@ericsson.com, jon.piesing@tpvision.com
  RFC7529          ||      C. Daboo, G. Yakushev         ||       cyrus@daboo.name, gyakushev@yahoo.com
  RFC7530          ||      T. Haynes, Ed., D. Noveck, Ed.         ||       thomas.haynes@primarydata.com, dave_noveck@dell.com
  RFC7531          ||      T. Haynes, Ed., D. Noveck, Ed.         ||       thomas.haynes@primarydata.com, dave_noveck@dell.com
  RFC7532          ||      J. Lentini, R. Tewari, C. Lever, Ed.         ||       jlentini@netapp.com, tewarir@us.ibm.com, chuck.lever@oracle.com
  RFC7533          ||      J. Lentini, R. Tewari, C. Lever, Ed.         ||       jlentini@netapp.com, tewarir@us.ibm.com, chuck.lever@oracle.com
  RFC7534          ||      J. Abley, W. Sotomayor         ||       jabley@dyn.com, wfms@ottix.net
  RFC7535          ||      J. Abley, B. Dickson, W. Kumari, G. Michaelson         ||       jabley@dyn.com, bdickson@twitter.com, warren@kumari.net, ggm@apnic.net
  RFC7536          ||      M. Linsner, P. Eardley, T. Burbridge, F. Sorensen         ||       mlinsner@cisco.com, philip.eardley@bt.com, trevor.burbridge@bt.com, frode.sorensen@nkom.no
  RFC7537          ||      B. Decraene, N. Akiya, C. Pignataro, L. Andersson, S. Aldrin         ||       bruno.decraene@orange.com, nobo.akiya.dev@gmail.com, cpignata@cisco.com, loa@mail01.huawei.com, aldrin.ietf@gmail.com
  RFC7538          ||      J. Reschke         ||       julian.reschke@greenbytes.de
  RFC7539          ||      Y. Nir, A. Langley         ||       ynir.ietf@gmail.com, agl@google.com
  RFC7540          ||      M. Belshe, R. Peon, M. Thomson, Ed.         ||       mike@belshe.com, fenix@google.com, martin.thomson@gmail.com
  RFC7541          ||      R. Peon, H. Ruellan         ||       fenix@google.com, herve.ruellan@crf.canon.fr
  RFC7542          ||      A. DeKok         ||       aland@freeradius.org
  RFC7543          ||      H. Jeng, L. Jalil, R. Bonica, K. Patel, L. Yong         ||       hj2387@att.com, luay.jalil@verizon.com, rbonica@juniper.net, keyupate@cisco.com, lucy.yong@huawei.com
  RFC7544          ||      M. Mohali         ||       marianne.mohali@orange.com
  RFC7545          ||      V. Chen, Ed., S. Das, L. Zhu, J. Malyar, P. McCann         ||       vchen@google.com, sdas@appcomsci.com, lei.zhu@huawei.com, jmalyar@iconectiv.com, peter.mccann@huawei.com
  RFC7546          ||      B. Kaduk         ||       kaduk@mit.edu
  RFC7547          ||      M. Ersue, Ed., D. Romascanu, J. Schoenwaelder, U. Herberg         ||       mehmet.ersue@nsn.com, dromasca@gmail.com , j.schoenwaelder@jacobs-university.de, ulrich@herberg.name
  RFC7548          ||      M. Ersue, Ed., D. Romascanu, J. Schoenwaelder, A. Sehgal         ||       mehmet.ersue@nsn.com, dromasca@gmail.com , j.schoenwaelder@jacobs-university.de, s.anuj@jacobs-university.de
  RFC7549          ||      C. Holmberg, J. Holm, R. Jesske, M. Dolly         ||       christer.holmberg@ericsson.com, jan.holm@ericsson.com, r.jesske@telekom.de, md3135@att.com
  RFC7550          ||      O. Troan, B. Volz, M. Siodelski         ||       ot@cisco.com, volz@cisco.com, msiodelski@gmail.com
  RFC7551          ||      F. Zhang, Ed., R. Jing, R. Gandhi, Ed.         ||       zhangfei7@huawei.com, jingrq@ctbri.com.cn, rgandhi@cisco.com
  RFC7552          ||      R. Asati, C. Pignataro, K. Raza, V. Manral, R. Papneja         ||       rajiva@cisco.com, cpignata@cisco.com, skraza@cisco.com, vishwas@ionosnetworks.com, rajiv.papneja@huawei.com
  RFC7553          ||      P. Faltstrom, O. Kolkman         ||       paf@netnod.se, kolkman@isoc.org
  RFC7554          ||      T. Watteyne, Ed., M. Palattella, L. Grieco         ||       twatteyne@linear.com, maria-rita.palattella@uni.lu, a.grieco@poliba.it
  RFC7555          ||      G. Swallow, V. Lim, S. Aldrin         ||       swallow@cisco.com, vlim@cisco.com, aldrin.ietf@gmail.com
  RFC7556          ||      D. Anipko, Ed.         ||       dmitry.anipko@gmail.com
  RFC7557          ||      J. Chroboczek         ||       jch@pps.univ-paris-diderot.fr
  RFC7558          ||      K. Lynn, S. Cheshire, M. Blanchet, D. Migault         ||       kerry.lynn@verizon.com, cheshire@apple.com, Marc.Blanchet@viagenie.ca, daniel.migault@ericsson.com
  RFC7559          ||      S. Krishnan, D. Anipko, D. Thaler         ||       suresh.krishnan@ericsson.com, dmitry.anipko@gmail.com, dthaler@microsoft.com
  RFC7560          ||      M. Kuehlewind, Ed., R. Scheffenegger, B. Briscoe         ||       mirja.kuehlewind@tik.ee.ethz.ch, rs@netapp.com, ietf@bobbriscoe.net
  RFC7561          ||      J. Kaippallimalil, R. Pazhyannur, P. Yegani         ||       john.kaippallimalil@huawei.com, rpazhyan@cisco.com, pyegani@juniper.net
  RFC7562          ||      D. Thakore         ||       d.thakore@cablelabs.com
  RFC7563          ||      R. Pazhyannur, S. Speicher, S. Gundavelli, J. Korhonen, J. Kaippallimalil         ||       rpazhyan@cisco.com, sespeich@cisco.com, sgundave@cisco.com, jouni.nospam@gmail.com, john.kaippallimalil@huawei.com
  RFC7564          ||      P. Saint-Andre, M. Blanchet         ||       peter@andyet.com, Marc.Blanchet@viagenie.ca
  RFC7565          ||      P. Saint-Andre         ||       peter@andyet.com
  RFC7566          ||      L. Goix, K. Li         ||       laurent.goix@econocom-osiatis.com, kepeng.likp@gmail.com
  RFC7567          ||      F. Baker, Ed., G. Fairhurst, Ed.         ||       fred@cisco.com, gorry@erg.abdn.ac.uk
  RFC7568          ||      R. Barnes, M. Thomson, A. Pironti, A. Langley         ||       rlb@ipv.sx, martin.thomson@gmail.com, alfredo@pironti.eu, agl@google.com
  RFC7569          ||      D. Quigley, J. Lu, T. Haynes         ||       dpquigl@davequigley.com, Jarrett.Lu@oracle.com, thomas.haynes@primarydata.com
  RFC7570          ||      C. Margaria, Ed., G. Martinelli, S. Balls, B. Wright         ||       cmargaria@juniper.net, giomarti@cisco.com, steve.balls@metaswitch.com, ben.wright@metaswitch.com
  RFC7571          ||      J. Dong, M. Chen, Z. Li, D. Ceccarelli         ||       jie.dong@huawei.com, mach.chen@huawei.com, lizhenqiang@chinamobile.com, daniele.ceccarelli@ericsson.com
  RFC7572          ||      P. Saint-Andre, A. Houri, J. Hildebrand         ||       peter@andyet.com, avshalom@il.ibm.com, jhildebr@cisco.com
  RFC7573          ||      P. Saint-Andre, S. Loreto         ||       peter@andyet.com, Salvatore.Loreto@ericsson.com
  RFC7574          ||      A. Bakker, R. Petrocco, V. Grishchenko         ||       arno@cs.vu.nl, r.petrocco@gmail.com, victor.grishchenko@gmail.com
  RFC7575          ||      M. Behringer, M. Pritikin, S. Bjarnason, A. Clemm, B. Carpenter, S. Jiang, L. Ciavaglia         ||       mbehring@cisco.com, pritikin@cisco.com, sbjarnas@cisco.com, alex@cisco.com, brian.e.carpenter@gmail.com, jiangsheng@huawei.com, Laurent.Ciavaglia@alcatel-lucent.com
  RFC7576          ||      S. Jiang, B. Carpenter, M. Behringer         ||       jiangsheng@huawei.com, brian.e.carpenter@gmail.com, mbehring@cisco.com
  RFC7577          ||      J. Quittek, R. Winter, T. Dietz         ||       quittek@neclab.eu, rolf.winter@neclab.eu, Thomas.Dietz@neclab.eu
  RFC7578          ||      L. Masinter         ||       masinter@adobe.com
  RFC7579          ||      G. Bernstein, Ed., Y. Lee, Ed., D. Li, W. Imajuku, J. Han         ||       gregb@grotto-networking.com, ylee@huawei.com, danli@huawei.com, imajuku.wataru@lab.ntt.co.jp, hanjianrui@huawei.com
  RFC7580          ||      F. Zhang, Y. Lee, J. Han, G. Bernstein, Y. Xu         ||       zhangfatai@huawei.com, leeyoung@huawei.com, hanjianrui@huawei.com, gregb@grotto-networking.com, xuyunbin@mail.ritt.com.cn
  RFC7581          ||      G. Bernstein, Ed., Y. Lee, Ed., D. Li, W. Imajuku, J. Han         ||       gregb@grotto-networking.com, leeyoung@huawei.com, danli@huawei.com, imajuku.wataru@lab.ntt.co.jp, hanjianrui@huawei.com
  RFC7582          ||      E. Rosen, IJ. Wijnands, Y. Cai, A. Boers         ||       erosen@juniper.net, ice@cisco.com, yiqunc@microsoft.com, arjen@boers.com
  RFC7583          ||      S. Morris, J. Ihren, J. Dickinson, W. Mekking         ||       stephen@isc.org, johani@netnod.se, jad@sinodun.com, mmekking@dyn.com
  RFC7584          ||      R. Ravindranath, T. Reddy, G. Salgueiro         ||       rmohanr@cisco.com, tireddy@cisco.com, gsalguei@cisco.com
  RFC7585          ||      S. Winter, M. McCauley         ||       stefan.winter@restena.lu, mikem@airspayce.com
  RFC7586          ||      Y. Nachum, L. Dunbar, I. Yerushalmi, T. Mizrahi         ||       youval.nachum@gmail.com, ldunbar@huawei.com, yilan@marvell.com, talmi@marvell.com
  RFC7587          ||      J. Spittka, K. Vos, JM. Valin         ||       jspittka@gmail.com, koenvos74@gmail.com, jmvalin@jmvalin.ca
  RFC7588          ||      R. Bonica, C. Pignataro, J. Touch         ||       rbonica@juniper.net, cpignata@cisco.com, touch@isi.edu
  RFC7589          ||      M. Badra, A. Luchuk, J. Schoenwaelder         ||       mohamad.badra@zu.ac.ae, luchuk@snmp.com, j.schoenwaelder@jacobs-university.de
  RFC7590          ||      P. Saint-Andre, T. Alkemade         ||       peter@andyet.com, me@thijsalkema.de
  RFC7591          ||      J. Richer, Ed., M. Jones, J. Bradley, M. Machulak, P. Hunt         ||       ietf@justin.richer.org, mbj@microsoft.com, ve7jtb@ve7jtb.com, maciej.machulak@gmail.com, phil.hunt@yahoo.com
  RFC7592          ||      J. Richer, Ed., M. Jones, J. Bradley, M. Machulak         ||       ietf@justin.richer.org, mbj@microsoft.com, ve7jtb@ve7jtb.com, maciej.machulak@gmail.com
  RFC7593          ||      K. Wierenga, S. Winter, T. Wolniewicz         ||       klaas@cisco.com, stefan.winter@restena.lu, twoln@umk.pl
  RFC7594          ||      P. Eardley, A. Morton, M. Bagnulo, T. Burbridge, P. Aitken, A. Akhter         ||       philip.eardley@bt.com, acmorton@att.com, marcelo@it.uc3m.es, trevor.burbridge@bt.com, paitken@brocade.com, aakhter@gmail.com
  RFC7595          ||      D. Thaler, Ed., T. Hansen, T. Hardie         ||       dthaler@microsoft.com, tony+urireg@maillennium.att.com, ted.ietf@gmail.com
  RFC7596          ||      Y. Cui, Q. Sun, M. Boucadair, T. Tsou, Y. Lee, I. Farrer         ||       yong@csnet1.cs.tsinghua.edu.cn, sunqiong@ctbri.com.cn, mohamed.boucadair@orange.com, tena@huawei.com, yiu_lee@cable.comcast.com, ian.farrer@telekom.de
  RFC7597          ||      O. Troan, Ed., W. Dec, X. Li, C. Bao, S. Matsushima, T. Murakami, T. Taylor, Ed.         ||       ot@cisco.com, wdec@cisco.com, xing@cernet.edu.cn, congxiao@cernet.edu.cn, satoru.matsushima@g.softbank.co.jp, tetsuya@ipinfusion.com, tom.taylor.stds@gmail.com
  RFC7598          ||      T. Mrugalski, O. Troan, I. Farrer, S. Perreault, W. Dec, C. Bao, L. Yeh, X. Deng         ||       tomasz.mrugalski@gmail.com, ot@cisco.com, ian.farrer@telekom.de, sperreault@jive.com, wdec@cisco.com, congxiao@cernet.edu.cn, leaf.y.yeh@hotmail.com, dxhbupt@gmail.com
  RFC7599          ||      X. Li, C. Bao, W. Dec, Ed., O. Troan, S. Matsushima, T. Murakami         ||       xing@cernet.edu.cn, congxiao@cernet.edu.cn, wdec@cisco.com, ot@cisco.com, satoru.matsushima@g.softbank.co.jp, tetsuya@ipinfusion.com
  RFC7600          ||      R. Despres, S. Jiang, Ed., R. Penno, Y. Lee, G. Chen, M. Chen         ||       despres.remi@laposte.net, jiangsheng@huawei.com, repenno@cisco.com, yiu_lee@cable.comcast.com, phdgang@gmail.com, maoke@bbix.net
  RFC7601          ||      M. Kucherawy         ||       superuser@gmail.com
  RFC7602          ||      U. Chunduri, W. Lu, A. Tian, N. Shen         ||       uma.chunduri@ericsson.com, wenhu.lu@ericsson.com, albert.tian@ericsson.com, naiming@cisco.com
  RFC7603          ||      B. Schoening, M. Chandramouli, B. Nordman         ||       brad.schoening@verizon.net, moulchan@cisco.com, bnordman@lbl.gov
  RFC7604          ||      M. Westerlund, T. Zeng         ||       magnus.westerlund@ericsson.com, thomas.zeng@gmail.com
  RFC7605          ||      J. Touch         ||       touch@isi.edu
  RFC7606          ||      E. Chen, Ed., J. Scudder, Ed., P. Mohapatra, K. Patel         ||       enkechen@cisco.com, jgs@juniper.net, mpradosh@yahoo.com, keyupate@cisco.com
  RFC7607          ||      W. Kumari, R. Bush, H. Schiller, K. Patel         ||       warren@kumari.net, randy@psg.com, has@google.com, keyupate@cisco.com
  RFC7608          ||      M. Boucadair, A. Petrescu, F. Baker         ||       mohamed.boucadair@orange.com, alexandre.petrescu@cea.fr, fred@cisco.com
  RFC7609          ||      M. Fox, C. Kassimis, J. Stevens         ||       mjfox@us.ibm.com, kassimis@us.ibm.com, sjerry@us.ibm.com
  RFC7610          ||      F. Gont, W. Liu, G. Van de Velde         ||       fgont@si6networks.com, liushucheng@huawei.com, gunter.van_de_velde@alcatel-lucent.com
  RFC7611          ||      J. Uttaro, P. Mohapatra, D. Smith, R. Raszuk, J. Scudder         ||       uttaro@att.com, mpradosh@yahoo.com, djsmith@cisco.com, robert@raszuk.net, jgs@juniper.net
  RFC7612          ||      P. Fleming, I. McDonald         ||       patfleminghtc@gmail.com, blueroofmusic@gmail.com
  RFC7613          ||      P. Saint-Andre, A. Melnikov         ||       peter@andyet.com, alexey.melnikov@isode.com
  RFC7614          ||      R. Sparks         ||       rjsparks@nostrum.com
  RFC7615          ||      J. Reschke         ||       julian.reschke@greenbytes.de
  RFC7616          ||      R. Shekh-Yusef, Ed., D. Ahrens, S. Bremer         ||       rifaat.ietf@gmail.com, ahrensdc@gmail.com, sophie.bremer@netzkonform.de
  RFC7617          ||      J. Reschke         ||       julian.reschke@greenbytes.de
  RFC7618          ||      Y. Cui, Q. Sun, I. Farrer, Y. Lee, Q. Sun, M. Boucadair         ||       yong@csnet1.cs.tsinghua.edu.cn, sunqi.ietf@gmail.com, ian.farrer@telekom.de, yiu_lee@cable.comcast.com, sunqiong@ctbri.com.cn, mohamed.boucadair@orange.com
  RFC7619          ||      V. Smyslov, P. Wouters         ||       svan@elvis.ru, pwouters@redhat.com
  RFC7620          ||      M. Boucadair, Ed., B. Chatras, T. Reddy, B. Williams, B. Sarikaya         ||       mohamed.boucadair@orange.com, bruno.chatras@orange.com, tireddy@cisco.com, brandon.williams@akamai.com, sarikaya@ieee.org
  RFC7621          ||      A.B. Roach         ||       adam@nostrum.com
  RFC7622          ||      P. Saint-Andre         ||       peter@andyet.com
  RFC7623          ||      A. Sajassi, Ed., S. Salam, N. Bitar, A. Isaac, W. Henderickx         ||       sajassi@cisco.com, ssalam@cisco.com, nabil.n.bitar@verizon.com, aisaac@juniper.net, wim.henderickx@alcatel-lucent.com
  RFC7624          ||      R. Barnes, B. Schneier, C. Jennings, T. Hardie, B. Trammell, C. Huitema, D. Borkmann         ||       rlb@ipv.sx, schneier@schneier.com, fluffy@cisco.com, ted.ietf@gmail.com, ietf@trammell.ch, huitema@huitema.net, daniel@iogearbox.net
  RFC7625          ||      J. T. Hao, P. Maheshwari, R. Huang, L. Andersson, M. Chen         ||       haojiangtao@huawei.com, praveen.maheshwari@in.airtel.com, river.huang@huawei.com, loa@mail01.huawei.com, mach.chen@huawei.com
  RFC7626          ||      S. Bortzmeyer         ||       bortzmeyer+ietf@nic.fr
  RFC7627          ||      K. Bhargavan, Ed., A. Delignat-Lavaud, A. Pironti, A. Langley, M. Ray         ||       karthikeyan.bhargavan@inria.fr, antoine.delignat-lavaud@inria.fr, alfredo.pironti@inria.fr, agl@google.com, maray@microsoft.com
  RFC7628          ||      W. Mills, T. Showalter, H. Tschofenig         ||       wmills_92105@yahoo.com, tjs@psaux.com, Hannes.Tschofenig@gmx.net
  RFC7629          ||      S. Gundavelli, Ed., K. Leung, G. Tsirtsis, A. Petrescu         ||       sgundave@cisco.com, kleung@cisco.com, tsirtsis@qualcomm.com, alexandru.petrescu@cea.fr
  RFC7630          ||      J. Merkle, Ed., M. Lochter         ||       johannes.merkle@secunet.com, manfred.lochter@bsi.bund.de
  RFC7631          ||      C. Dearlove, T. Clausen         ||       chris.dearlove@baesystems.com, T.Clausen@computer.org
  RFC7632          ||      D. Waltermire, D. Harrington         ||       david.waltermire@nist.gov, ietfdbh@gmail.com
  RFC7633          ||      P. Hallam-Baker         ||       philliph@comodo.com
  RFC7634          ||      Y. Nir         ||       ynir.ietf@gmail.com
  RFC7635          ||      T. Reddy, P. Patil, R. Ravindranath, J. Uberti         ||       tireddy@cisco.com, praspati@cisco.com, rmohanr@cisco.com, justin@uberti.name
  RFC7636          ||      N. Sakimura, Ed., J. Bradley, N. Agarwal         ||       n-sakimura@nri.co.jp, ve7jtb@ve7jtb.com, naa@google.com
  RFC7637          ||      P. Garg, Ed., Y. Wang, Ed.         ||       pankajg@microsoft.com, yushwang@microsoft.com
  RFC7638          ||      M. Jones, N. Sakimura         ||       mbj@microsoft.com, n-sakimura@nri.co.jp
  RFC7639          ||      A. Hutton, J. Uberti, M. Thomson         ||       andrew.hutton@unify.com, justin@uberti.name, martin.thomson@gmail.com
  RFC7640          ||      B. Constantine, R. Krishnan         ||       barry.constantine@jdsu.com, ramkri123@gmail.com
  RFC7641          ||      K. Hartke         ||       hartke@tzi.org
  RFC7642          ||      K. LI, Ed., P. Hunt, B. Khasnabish, A. Nadalin, Z. Zeltsan         ||       kepeng.lkp@alibaba-inc.com, phil.hunt@oracle.com, vumip1@gmail.com, tonynad@microsoft.com, zachary.zeltsan@gmail.com
  RFC7643          ||      P. Hunt, Ed., K. Grizzle, E. Wahlstroem, C. Mortimore         ||       phil.hunt@yahoo.com, kelly.grizzle@sailpoint.com, erik.wahlstrom@nexusgroup.com, cmortimore@salesforce.com
  RFC7644          ||      P. Hunt, Ed., K. Grizzle, M. Ansari, E. Wahlstroem, C. Mortimore         ||       phil.hunt@yahoo.com, kelly.grizzle@sailpoint.com, morteza.ansari@cisco.com, erik.wahlstrom@nexusgroup.com, cmortimore@salesforce.com
  RFC7645          ||      U. Chunduri, A. Tian, W. Lu         ||       uma.chunduri@ericsson.com, albert.tian@ericsson.com, wenhu.lu@ericsson.com
  RFC7646          ||      P. Ebersman, W. Kumari, C. Griffiths, J. Livingood, R. Weber         ||       ebersman-ietf@dragon.net, warren@kumari.net, cgriffiths@gmail.com, jason_livingood@cable.comcast.com, ralf.weber@nominum.com
  RFC7647          ||      R. Sparks, A.B. Roach         ||       rjsparks@nostrum.com, adam@nostrum.com
  RFC7648          ||      S. Perreault, M. Boucadair, R. Penno, D. Wing, S. Cheshire         ||       sperreault@jive.com, mohamed.boucadair@orange.com, repenno@cisco.com, dwing-ietf@fuggles.com, cheshire@apple.com
  RFC7649          ||      P. Saint-Andre, D. York         ||       peter@andyet.com, york@isoc.org
  RFC7650          ||      J. Jimenez, J. Lopez-Vega, J. Maenpaa, G. Camarillo         ||       jaime.jimenez@ericsson.com, jmlvega@ugr.es, jouni.maenpaa@ericsson.com, gonzalo.camarillo@ericsson.com
  RFC7651          ||      A. Dodd-Noble, S. Gundavelli, J. Korhonen, F. Baboescu, B. Weis         ||       noblea@cisco.com, sgundave@cisco.com, jouni.nospam@gmail.com, baboescu@broadcom.com, bew@cisco.com
  RFC7652          ||      M. Cullen, S. Hartman, D. Zhang, T. Reddy         ||       margaret@painless-security.com, hartmans@painless-security.com, zhang_dacheng@hotmail.com, tireddy@cisco.com
  RFC7653          ||      D. Raghuvanshi, K. Kinnear, D. Kukrety         ||       draghuva@cisco.com, kkinnear@cisco.com, dkukrety@cisco.com
  RFC7654          ||      S. Banks, F. Calabria, G. Czirjak, R. Machat         ||       sbanks@encrypted.net, fcalabri@cisco.com, gczirjak@juniper.net, rmachat@juniper.net
  RFC7655          ||      M. Ramalho, Ed., P. Jones, N. Harada, M. Perumal, L. Miao         ||       mramalho@cisco.com, paulej@packetizer.com, harada.noboru@lab.ntt.co.jp, muthu.arul@gmail.com, lei.miao@huawei.com
  RFC7656          ||      J. Lennox, K. Gross, S. Nandakumar, G. Salgueiro, B. Burman, Ed.         ||       jonathan@vidyo.com, kevin.gross@avanw.com, snandaku@cisco.com, gsalguei@cisco.com, bo.burman@ericsson.com
  RFC7657          ||      D. Black, Ed., P. Jones         ||       david.black@emc.com, paulej@packetizer.com
  RFC7658          ||      S. Perreault, T. Tsou, S. Sivakumar, T. Taylor         ||       sperreault@jive.com, tina.tsou.zouting@huawei.com, ssenthil@cisco.com, tom.taylor.stds@gmail.com
  RFC7659          ||      S. Perreault, T. Tsou, S. Sivakumar, T. Taylor         ||       sperreault@jive.com, tina.tsou.zouting@huawei.com, ssenthil@cisco.com, tom.taylor.stds@gmail.com
  RFC7660          ||      L. Bertz, S. Manning, B. Hirschman         ||       lyleb551144@gmail.com, sergem913@gmail.com, Brent.Hirschman@gmail.com
  RFC7661          ||      G. Fairhurst, A. Sathiaseelan, R. Secchi         ||       gorry@erg.abdn.ac.uk, arjuna@erg.abdn.ac.uk, raffaello@erg.abdn.ac.uk
  RFC7662          ||      J. Richer, Ed.         ||       ietf@justin.richer.org
  RFC7663          ||      B. Trammell, Ed., M. Kuehlewind, Ed.         ||       ietf@trammell.ch, mirja.kuehlewind@tik.ee.ethz.ch
  RFC7664          ||      D. Harkins, Ed.         ||       dharkins@arubanetworks.com
  RFC7665          ||      J. Halpern, Ed., C. Pignataro, Ed.         ||       jmh@joelhalpern.com, cpignata@cisco.com
  RFC7666          ||      H. Asai, M. MacFaden, J. Schoenwaelder, K. Shima, T. Tsou         ||       panda@hongo.wide.ad.jp, mrm@vmware.com, j.schoenwaelder@jacobs-university.de, keiichi@iijlab.net, tina.tsou.zouting@huawei.com
  RFC7667          ||      M. Westerlund, S. Wenger         ||       magnus.westerlund@ericsson.com, stewe@stewe.org
  RFC7668          ||      J. Nieminen, T. Savolainen, M. Isomaki, B. Patil, Z. Shelby, C. Gomez         ||       johannamaria.nieminen@gmail.com, teemu.savolainen@nokia.com, markus.isomaki@nokia.com, basavaraj.patil@att.com, zach.shelby@arm.com, carlesgo@entel.upc.edu
  RFC7669          ||      J. Levine         ||       standards@taugh.com
  RFC7670          ||      T. Kivinen, P. Wouters, H. Tschofenig         ||       kivinen@iki.fi, pwouters@redhat.com, Hannes.Tschofenig@gmx.net
  RFC7671          ||      V. Dukhovni, W. Hardaker         ||       ietf-dane@dukhovni.org, ietf@hardakers.net
  RFC7672          ||      V. Dukhovni, W. Hardaker         ||       ietf-dane@dukhovni.org, ietf@hardakers.net
  RFC7673          ||      T. Finch, M. Miller, P. Saint-Andre         ||       dot@dotat.at, mamille2@cisco.com, peter@andyet.com
  RFC7674          ||      J. Haas, Ed.         ||       jhaas@juniper.net
  RFC7675          ||      M. Perumal, D. Wing, R. Ravindranath, T. Reddy, M. Thomson         ||       muthu.arul@gmail.com, dwing-ietf@fuggles.com, rmohanr@cisco.com, tireddy@cisco.com, martin.thomson@gmail.com
  RFC7676          ||      C. Pignataro, R. Bonica, S. Krishnan         ||       cpignata@cisco.com, rbonica@juniper.net, suresh.krishnan@ericsson.com
  RFC7677          ||      T. Hansen         ||       tony+scramsha256@maillennium.att.com
  RFC7678          ||      C. Zhou, T. Taylor, Q. Sun, M. Boucadair         ||       cathy.zhou@huawei.com, tom.taylor.stds@gmail.com, sunqiong@ctbri.com.cn, mohamed.boucadair@orange.com
  RFC7679          ||      G. Almes, S. Kalidindi, M. Zekauskas, A. Morton, Ed.         ||       almes@acm.org, skalidindi@ixiacom.com, matt@internet2.edu, acmorton@att.com
  RFC7680          ||      G. Almes, S. Kalidindi, M. Zekauskas, A. Morton, Ed.         ||       almes@acm.org, skalidindi@ixiacom.com, matt@internet2.edu, acmorton@att.com
  RFC7681          ||      J. Davin         ||       info@eesst.org
  RFC7682          ||      D. McPherson, S. Amante, E. Osterweil, L. Blunk, D. Mitchell         ||       dmcpherson@verisign.com, amante@apple.com, eosterweil@verisign.com, ljb@merit.edu, dave@singularity.cx
  RFC7683          ||      J. Korhonen, Ed., S. Donovan, Ed., B. Campbell, L. Morand         ||       jouni.nospam@gmail.com, srdonovan@usdonovans.com, ben@nostrum.com, lionel.morand@orange.com
  RFC7684          ||      P. Psenak, H. Gredler, R. Shakir, W. Henderickx, J. Tantsura, A. Lindem         ||       ppsenak@cisco.com, hannes@gredler.at, rjs@rob.sh, wim.henderickx@alcatel-lucent.com, jeff.tantsura@ericsson.com, acee@cisco.com
  RFC7685          ||      A. Langley         ||       agl@google.com
  RFC7686          ||      J. Appelbaum, A. Muffett         ||       jacob@appelbaum.net, alecm@fb.com
  RFC7687          ||      S. Farrell, R. Wenning, B. Bos, M. Blanchet, H. Tschofenig         ||       stephen.farrell@cs.tcd.ie, rigo@w3.org, bert@w3.org, Marc.Blanchet@viagenie.ca, Hannes.Tschofenig@gmx.net
  RFC7688          ||      Y. Lee, Ed., G. Bernstein, Ed.         ||       leeyoung@huawei.com, gregb@grotto-networking.com
  RFC7689          ||      G. Bernstein, Ed., S. Xu, Y. Lee, Ed., G. Martinelli, H. Harai         ||       gregb@grotto-networking.com, xsg@nict.go.jp, leeyoung@huawei.com, giomarti@cisco.com, harai@nict.go.jp
  RFC7690          ||      M. Byerly, M. Hite, J. Jaeggli         ||       suckawha@gmail.com, mhite@hotmail.com, joelja@gmail.com
  RFC7691          ||      S. Bradner, Ed.         ||       sob@harvard.edu
  RFC7692          ||      T. Yoshino         ||       tyoshino@google.com
  RFC7693          ||      M-J. Saarinen, Ed., J-P. Aumasson         ||       m.saarinen@qub.ac.uk, jean-philippe.aumasson@nagra.com
  RFC7694          ||      J. Reschke         ||       julian.reschke@greenbytes.de
  RFC7695          ||      P. Pfister, B. Paterson, J. Arkko         ||       pierre.pfister@darou.fr, paterson.b@gmail.com, jari.arkko@piuha.net
  RFC7696          ||      R. Housley         ||       housley@vigilsec.com
  RFC7697          ||      P. Pan, S. Aldrin, M. Venkatesan, K. Sampath, T. Nadeau, S. Boutros         ||       none, aldrin.ietf@gmail.com, venkat.mahalingams@gmail.com, kannankvs@gmail.com, tnadeau@lucidvision.com, sboutros@vmware.com
  RFC7698          ||      O. Gonzalez de Dios, Ed., R. Casellas, Ed., F. Zhang, X. Fu, D. Ceccarelli, I. Hussain         ||       oscar.gonzalezdedios@telefonica.com, ramon.casellas@cttc.es, zhangfatai@huawei.com, fu.xihua@stairnote.com, daniele.ceccarelli@ericsson.com, ihussain@infinera.com
  RFC7699          ||      A. Farrel, D. King, Y. Li, F. Zhang         ||       adrian@olddog.co.uk, daniel@olddog.co.uk, wsliguotou@hotmail.com, zhangfatai@huawei.com
  RFC7700          ||      P. Saint-Andre         ||       peter@andyet.com
  RFC7701          ||      A. Niemi, M. Garcia-Martin, G. Sandbakken         ||       aki.niemi@iki.fi, miguel.a.garcia@ericsson.com, geirsand@cisco.com
  RFC7702          ||      P. Saint-Andre, S. Ibarra, S. Loreto         ||       peter@andyet.com, saul@ag-projects.com, Salvatore.Loreto@ericsson.com
  RFC7703          ||      E. Cordeiro, R. Carnier, A. Moreiras         ||       edwin@scordeiro.net, rodrigocarnier@gmail.com, moreiras@nic.br
  RFC7704          ||      D. Crocker, N. Clark         ||       dcrocker@bbiw.net, narelle.clark@pavonis.com.au
  RFC7705          ||      W. George, S. Amante         ||       wesley.george@twcable.com, amante@apple.com
  RFC7706          ||      W. Kumari, P. Hoffman         ||       warren@kumari.net, paul.hoffman@icann.org
  RFC7707          ||      F. Gont, T. Chown         ||       fgont@si6networks.com, tim.chown@jisc.ac.uk
  RFC7708          ||      T. Nadeau, L. Martini, S. Bryant         ||       tnadeau@lucidvision.com, lmartini@cisco.com, stewart.bryant@gmail.com
  RFC7709          ||      A. Malis, Ed., B. Wilson, G. Clapp, V. Shukla         ||       agmalis@gmail.com, bwilson@appcomsci.com, clapp@research.att.com, vishnu.shukla@verizon.com
  RFC7710          ||      W. Kumari, O. Gudmundsson, P. Ebersman, S. Sheng         ||       warren@kumari.net, olafur@cloudflare.com, ebersman-ietf@dragon.net, steve.sheng@icann.org
  RFC7711          ||      M. Miller, P. Saint-Andre         ||       mamille2@cisco.com, peter@andyet.com
  RFC7712          ||      P. Saint-Andre, M. Miller, P. Hancke         ||       peter@andyet.com, mamille2@cisco.com, fippo@andyet.com
  RFC7713          ||      M. Mathis, B. Briscoe         ||       mattmathis@google.com, ietf@bobbriscoe.net
  RFC7714          ||      D. McGrew, K. Igoe         ||       mcgrew@cisco.com, mythicalkevin@yahoo.com
  RFC7715          ||      IJ. Wijnands, Ed., K. Raza, A. Atlas, J. Tantsura, Q. Zhao         ||       ice@cisco.com, skraza@cisco.com, akatlas@juniper.net, jeff.tantsura@ericsson.com, quintin.zhao@huawei.com
  RFC7716          ||      J. Zhang, L. Giuliano, E. Rosen, Ed., K. Subramanian, D. Pacella         ||       zzhang@juniper.net, lenny@juniper.net, erosen@juniper.net, kartsubr@cisco.com, dante.j.pacella@verizonbusiness.com
  RFC7717          ||      K. Pentikousis, Ed., E. Zhang, Y. Cui         ||       k.pentikousis@eict.de, emma.zhanglijia@huawei.com, cuiyang@huawei.com
  RFC7718          ||      A. Morton         ||       acmorton@att.com
  RFC7719          ||      P. Hoffman, A. Sullivan, K. Fujiwara         ||       paul.hoffman@icann.org, asullivan@dyn.com, fujiwara@jprs.co.jp
  RFC7720          ||      M. Blanchet, L-J. Liman         ||       Marc.Blanchet@viagenie.ca, liman@netnod.se
  RFC7721          ||      A. Cooper, F. Gont, D. Thaler         ||       alcoop@cisco.com, fgont@si6networks.com, dthaler@microsoft.com
  RFC7722          ||      C. Dearlove, T. Clausen         ||       chris.dearlove@baesystems.com, T.Clausen@computer.org
  RFC7723          ||      S. Kiesel, R. Penno         ||       ietf-pcp@skiesel.de, repenno@cisco.com
  RFC7724          ||      K. Kinnear, M. Stapp, B. Volz, N. Russell         ||       kkinnear@cisco.com, mjs@cisco.com, volz@cisco.com, neil.e.russell@gmail.com
  RFC7725          ||      T. Bray         ||       tbray@textuality.com
  RFC7726          ||      V. Govindan, K. Rajaraman, G. Mirsky, N. Akiya, S. Aldrin         ||       venggovi@cisco.com, kalyanir@cisco.com, gregory.mirsky@ericsson.com, nobo.akiya.dev@gmail.com, aldrin.ietf@gmail.com
  RFC7727          ||      M. Zhang, H. Wen, J. Hu         ||       zhangmingui@huawei.com, wenhuafeng@huawei.com, hujie@ctbri.com.cn
  RFC7728          ||      B. Burman, A. Akram, R. Even, M. Westerlund         ||       bo.burman@ericsson.com, akram.muhammadazam@gmail.com, roni.even@mail01.huawei.com, magnus.westerlund@ericsson.com
  RFC7729          ||      B. Khasnabish, E. Haleplidis, J. Hadi Salim, Ed.         ||       vumip1@gmail.com, ehalep@ece.upatras.gr, hadi@mojatatu.com
  RFC7730          ||      G. Huston, S. Weiler, G. Michaelson, S. Kent         ||       gih@apnic.net, weiler@tislabs.com, ggm@apnic.net, kent@bbn.com
  RFC7731          ||      J. Hui, R. Kelsey         ||       jonhui@nestlabs.com, richard.kelsey@silabs.com
  RFC7732          ||      P. van der Stok, R. Cragie         ||       consultancy@vanderstok.org, robert.cragie@arm.com
  RFC7733          ||      A. Brandt, E. Baccelli, R. Cragie, P. van der Stok         ||       anders_brandt@sigmadesigns.com, Emmanuel.Baccelli@inria.fr, robert.cragie@arm.com, consultancy@vanderstok.org
  RFC7734          ||      D. Allan, Ed., J. Tantsura, D. Fedyk, A. Sajassi         ||       david.i.allan@ericsson.com, jeff.tantsura@ericsson.com, don.fedyk@hpe.com, sajassi@cisco.com
  RFC7735          ||      R. Sparks, T. Kivinen         ||       rjsparks@nostrum.com, kivinen@iki.fi
  RFC7736          ||      K. Ma         ||       kevin.j.ma@ericsson.com
  RFC7737          ||      N. Akiya, G. Swallow, C. Pignataro, L. Andersson, M. Chen         ||       nobo.akiya.dev@gmail.com, swallow@cisco.com, cpignata@cisco.com, loa@mail01.huawei.com, mach.chen@huawei.com
  RFC7738          ||      M. Blanchet, A. Schiltknecht, P. Shames         ||       Marc.Blanchet@viagenie.ca, audric.schiltknecht@viagenie.ca, peter.m.shames@jpl.nasa.gov
  RFC7739          ||      F. Gont         ||       fgont@si6networks.com
  RFC7740          ||      Z. Zhang, Y. Rekhter, A. Dolganow         ||       zzhang@juniper.net, none, andrew.dolganow@alcatel-lucent.com
  RFC7741          ||      P. Westin, H. Lundin, M. Glover, J. Uberti, F. Galligan         ||       patrik.westin@gmail.com, hlundin@google.com, michaelglover262@gmail.com, justin@uberti.name, fgalligan@google.com
  RFC7742          ||      A.B. Roach         ||       adam@nostrum.com
  RFC7743          ||      J. Luo, Ed., L. Jin, Ed., T. Nadeau, Ed., G. Swallow, Ed.         ||       luo.jian@zte.com.cn, lizho.jin@gmail.com, tnadeau@lucidvision.com, swallow@cisco.com
  RFC7744          ||      L. Seitz, Ed., S. Gerdes, Ed., G. Selander, M. Mani, S. Kumar         ||       ludwig@sics.se, gerdes@tzi.org, goran.selander@ericsson.com, mehdi.mani@itron.com, sandeep.kumar@philips.com
  RFC7745          ||      T. Manderson         ||       terry.manderson@icann.org
  RFC7746          ||      R. Bonica, I. Minei, M. Conn, D. Pacella, L. Tomotaki         ||       rbonica@juniper.net, inaminei@google.com, meconn26@gmail.com, dante.j.pacella@verizon.com, luis.tomotaki@verizon.com
  RFC7747          ||      R. Papneja, B. Parise, S. Hares, D. Lee, I. Varlashkin         ||       rajiv.papneja@huawei.com, bparise@skyportsystems.com, shares@ndzh.com, dlee@ixiacom.com, ilya@nobulus.com
  RFC7748          ||      A. Langley, M. Hamburg, S. Turner         ||       agl@google.com, mike@shiftleft.org, sean@sn3rd.com
  RFC7749          ||      J. Reschke         ||       julian.reschke@greenbytes.de
  RFC7750          ||      J. Hedin, G. Mirsky, S. Baillargeon         ||       jonas.hedin@ericsson.com, gregory.mirsky@ericsson.com, steve.baillargeon@ericsson.com
  RFC7751          ||      S. Sorce, T. Yu         ||       ssorce@redhat.com, tlyu@mit.edu
  RFC7752          ||      H. Gredler, Ed., J. Medved, S. Previdi, A. Farrel, S. Ray         ||       hannes@gredler.at, jmedved@cisco.com, sprevidi@cisco.com, adrian@olddog.co.uk, raysaikat@gmail.com
  RFC7753          ||      Q. Sun, M. Boucadair, S. Sivakumar, C. Zhou, T. Tsou, S. Perreault         ||       sunqiong@ctbri.com.cn, mohamed.boucadair@orange.com, ssenthil@cisco.com, cathy.zhou@huawei.com, tina.tsou@philips.com, sperreault@jive.com
  RFC7754          ||      R. Barnes, A. Cooper, O. Kolkman, D. Thaler, E. Nordmark         ||       rlb@ipv.sx, alcoop@cisco.com, kolkman@isoc.org, dthaler@microsoft.com, nordmark@arista.com
  RFC7755          ||      T. Anderson         ||       tore@redpill-linpro.com
  RFC7756          ||      T. Anderson, S. Steffann         ||       tore@redpill-linpro.com, sander@steffann.nl
  RFC7757          ||      T. Anderson, A. Leiva Popper         ||       tore@redpill-linpro.com, ydahhrk@gmail.com
  RFC7758          ||      T. Mizrahi, Y. Moses         ||       dew@tx.technion.ac.il, moses@ee.technion.ac.il
  RFC7759          ||      E. Bellagamba, G. Mirsky, L. Andersson, P. Skoldstrom, D. Ward, J. Drake         ||       elisa.bellagamba@gmail.com, gregory.mirsky@ericsson.com, loa@mail01.huawei.com, pontus.skoldstrom@acreo.se, dward@cisco.com, jdrake@juniper.net
  RFC7760          ||      R. Housley         ||       housley@vigilsec.com
  RFC7761          ||      B. Fenner, M. Handley, H. Holbrook, I. Kouvelas, R. Parekh, Z. Zhang, L. Zheng         ||       fenner@arista.com, m.handley@cs.ucl.ac.uk, holbrook@arista.com, kouvelas@arista.com, riparekh@cisco.com, zzhang@juniper.net, vero.zheng@huawei.com
  RFC7762          ||      M. West         ||       mkwst@google.com
  RFC7763          ||      S. Leonard         ||       dev+ietf@seantek.com
  RFC7764          ||      S. Leonard         ||       dev+ietf@seantek.com
  RFC7765          ||      P. Hurtig, A. Brunstrom, A. Petlund, M. Welzl         ||       per.hurtig@kau.se, anna.brunstrom@kau.se, apetlund@simula.no, michawe@ifi.uio.no
  RFC7766          ||      J. Dickinson, S. Dickinson, R. Bellis, A. Mankin, D. Wessels         ||       jad@sinodun.com, sara@sinodun.com, ray@isc.org, allison.mankin@gmail.com, dwessels@verisign.com
  RFC7767          ||      S. Vinapamula, S. Sivakumar, M. Boucadair, T. Reddy         ||       sureshk@juniper.net, ssenthil@cisco.com, mohamed.boucadair@orange.com, tireddy@cisco.com
  RFC7768          ||      T. Tsou, W. Li, T. Taylor, J. Huang         ||       tina.tsou@philips.com, mweiboli@gmail.com, tom.taylor.stds@gmail.com, james.huang@huawei.com
  RFC7769          ||      S. Sivabalan, S. Boutros, H. Shah, S. Aldrin, M. Venkatesan         ||       msiva@cisco.com, sboutros@cisco.com, hshah@ciena.com, aldrin.ietf@gmail.com, mannan_venkatesan@cable.comcast.com
  RFC7770          ||      A. Lindem, Ed., N. Shen, JP. Vasseur, R. Aggarwal, S. Shaffer         ||       acee@cisco.com, naiming@cisco.com, jpv@cisco.com, raggarwa_1@yahoo.com, sshaffer@akamai.com
  RFC7771          ||      A. Malis, Ed., L. Andersson, H. van Helvoort, J. Shin, L. Wang, A. D'Alessandro         ||       agmalis@gmail.com, loa@mail01.huawei.com, huubatwork@gmail.com, jongyoon.shin@sk.com, wangleiyj@chinamobile.com, alessandro.dalessandro@telecomitalia.it
  RFC7772          ||      A. Yourtchenko, L. Colitti         ||       ayourtch@cisco.com, lorenzo@google.com
  RFC7773          ||      S. Santesson         ||       sts@aaa-sec.com
  RFC7774          ||      Y. Doi, M. Gillmore         ||       yusuke.doi@toshiba.co.jp, matthew.gillmore@itron.com
  RFC7775          ||      L. Ginsberg, S. Litkowski, S. Previdi         ||       ginsberg@cisco.com, stephane.litkowski@orange.com, sprevidi@cisco.com
  RFC7776          ||      P. Resnick, A. Farrel         ||       presnick@qti.qualcomm.com, adrian@olddog.co.uk
  RFC7777          ||      S. Hegde, R. Shakir, A. Smirnov, Z. Li, B. Decraene         ||       shraddha@juniper.net, rjs@rob.sh, as@cisco.com, lizhenbin@huawei.com, bruno.decraene@orange.com
  RFC7778          ||      D. Kutscher, F. Mir, R. Winter, S. Krishnan, Y. Zhang, CJ. Bernardos         ||       kutscher@neclab.eu, faisal.mir@gmail.com, rolf.winter@neclab.eu, suresh.krishnan@ericsson.com, ying.zhang13@hp.com, cjbc@it.uc3m.es
  RFC7779          ||      H. Rogge, E. Baccelli         ||       henning.rogge@fkie.fraunhofer.de, Emmanuel.Baccelli@inria.fr
  RFC7780          ||      D. Eastlake 3rd, M. Zhang, R. Perlman, A. Banerjee, A. Ghanwani, S. Gupta         ||       d3e3e3@gmail.com, zhangmingui@huawei.com, radia@alum.mit.edu, ayabaner@cisco.com, anoop@alumni.duke.edu, sujay.gupta@ipinfusion.com
  RFC7781          ||      H. Zhai, T. Senevirathne, R. Perlman, M. Zhang, Y. Li         ||       honjun.zhai@tom.com, tsenevir@gmail.com, radia@alum.mit.edu, zhangmingui@huawei.com, liyizhou@huawei.com
  RFC7782          ||      M. Zhang, R. Perlman, H. Zhai, M. Durrani, S. Gupta         ||       zhangmingui@huawei.com, radia@alum.mit.edu, honjun.zhai@tom.com, mdurrani@cisco.com, sujay.gupta@ipinfusion.com
  RFC7783          ||      T. Senevirathne, J. Pathangi, J. Hudson         ||       tsenevir@gmail.com, pathangi_janardhanan@dell.com, jon.hudson@gmail.com
  RFC7784          ||      D. Kumar, S. Salam, T. Senevirathne         ||       dekumar@cisco.com, ssalam@cisco.com, tsenevir@gmail.com
  RFC7785          ||      S. Vinapamula, M. Boucadair         ||       sureshk@juniper.net, mohamed.boucadair@orange.com
  RFC7786          ||      M. Kuehlewind, Ed., R. Scheffenegger         ||       mirja.kuehlewind@tik.ee.ethz.ch, rs.ietf@gmx.at
  RFC7787          ||      M. Stenberg, S. Barth         ||       markus.stenberg@iki.fi, cyrus@openwrt.org
  RFC7788          ||      M. Stenberg, S. Barth, P. Pfister         ||       markus.stenberg@iki.fi, cyrus@openwrt.org, pierre.pfister@darou.fr
  RFC7789          ||      C. Cardona, P. Francois, P. Lucente         ||       juancamilo.cardona@imdea.org, pifranco@cisco.com, plucente@cisco.com
  RFC7790          ||      Y. Yoneya, T. Nemoto         ||       yoshiro.yoneya@jprs.co.jp, t.nemo10@kmd.keio.ac.jp
  RFC7791          ||      D. Migault, Ed., V. Smyslov         ||       daniel.migault@ericsson.com, svan@elvis.ru
  RFC7792          ||      F. Zhang, X. Zhang, A. Farrel, O. Gonzalez de Dios, D. Ceccarelli         ||       zhangfatai@huawei.com, zhang.xian@huawei.com, adrian@olddog.co.uk, oscar.gonzalezdedios@telefonica.com, daniele.ceccarelli@ericsson.com
  RFC7793          ||      M. Andrews         ||       marka@isc.org
  RFC7794          ||      L. Ginsberg, Ed., B. Decraene, S. Previdi, X. Xu, U. Chunduri         ||       ginsberg@cisco.com, bruno.decraene@orange.com, sprevidi@cisco.com, xuxiaohu@huawei.com, uma.chunduri@ericsson.com
  RFC7795          ||      J. Dong, H. Wang         ||       jie.dong@huawei.com, rainsword.wang@huawei.com
  RFC7796          ||      Y. Jiang, Ed., L. Yong, M. Paul         ||       jiangyuanlong@huawei.com, lucyyong@huawei.com, Manuel.Paul@telekom.de
  RFC7797          ||      M. Jones         ||       mbj@microsoft.com
  RFC7798          ||      Y.-K. Wang, Y. Sanchez, T. Schierl, S. Wenger, M. M. Hannuksela         ||       yekui.wang@gmail.com, yago.sanchez@hhi.fraunhofer.de, thomas.schierl@hhi.fraunhofer.de, stewe@stewe.org, miska.hannuksela@nokia.com
  RFC7799          ||      A. Morton         ||       acmorton@att.com
  RFC7800          ||      M. Jones, J. Bradley, H. Tschofenig         ||       mbj@microsoft.com, ve7jtb@ve7jtb.com, Hannes.Tschofenig@gmx.net
  RFC7801          ||      V. Dolmatov, Ed.         ||       dol@srcc.msu.ru
  RFC7802          ||      S. Emery, N. Williams         ||       shawn.emery@oracle.com, nico@cryptonector.com
  RFC7803          ||      B. Leiba         ||       barryleiba@computer.org
  RFC7804          ||      A. Melnikov         ||       alexey.melnikov@isode.com
  RFC7805          ||      A. Zimmermann, W. Eddy, L. Eggert         ||       alexander@zimmermann.eu.com, wes@mti-systems.com, lars@netapp.com
  RFC7806          ||      F. Baker, R. Pan         ||       fred@cisco.com, ropan@cisco.com
  RFC7807          ||      M. Nottingham, E. Wilde         ||       mnot@mnot.net, erik.wilde@dret.net
  RFC7808          ||      M. Douglass, C. Daboo         ||       mdouglass@sphericalcowgroup.com, cyrus@daboo.name
  RFC7809          ||      C. Daboo         ||       cyrus@daboo.name
  RFC7810          ||      S. Previdi, Ed., S. Giacalone, D. Ward, J. Drake, Q. Wu         ||       sprevidi@cisco.com, spencer.giacalone@gmail.com, wardd@cisco.com, jdrake@juniper.net, sunseawq@huawei.com
  RFC7811          ||      G. Enyedi, A. Csaszar, A. Atlas, C. Bowers, A. Gopalan         ||       Gabor.Sandor.Enyedi@ericsson.com, Andras.Csaszar@ericsson.com, akatlas@juniper.net, cbowers@juniper.net, abishek@ece.arizona.edu
  RFC7812          ||      A. Atlas, C. Bowers, G. Enyedi         ||       akatlas@juniper.net, cbowers@juniper.net, Gabor.Sandor.Enyedi@ericsson.com
  RFC7813          ||      J. Farkas, Ed., N. Bragg, P. Unbehagen, G. Parsons, P. Ashwood-Smith, C. Bowers         ||       janos.farkas@ericsson.com, nbragg@ciena.com, unbehagen@avaya.com, glenn.parsons@ericsson.com, Peter.AshwoodSmith@huawei.com, cbowers@juniper.net
  RFC7814          ||      X. Xu, C. Jacquenet, R. Raszuk, T. Boyes, B. Fee         ||       xuxiaohu@huawei.com, christian.jacquenet@orange.com, robert@raszuk.net, tboyes@bloomberg.net, bfee@extremenetworks.com
  RFC7815          ||      T. Kivinen         ||       kivinen@iki.fi
  RFC7816          ||      S. Bortzmeyer         ||       bortzmeyer+ietf@nic.fr
  RFC7817          ||      A. Melnikov         ||       alexey.melnikov@isode.com
  RFC7818          ||      M. Jethanandani         ||       mjethanandani@gmail.com
  RFC7819          ||      S. Jiang, S. Krishnan, T. Mrugalski         ||       jiangsheng@huawei.com, suresh.krishnan@ericsson.com, tomasz.mrugalski@gmail.com
  RFC7820          ||      T. Mizrahi         ||       talmi@marvell.com
  RFC7821          ||      T. Mizrahi         ||       talmi@marvell.com
  RFC7822          ||      T. Mizrahi, D. Mayer         ||       talmi@marvell.com, mayer@ntp.org
  RFC7823          ||      A. Atlas, J. Drake, S. Giacalone, S. Previdi         ||       akatlas@juniper.net, jdrake@juniper.net, spencer.giacalone@gmail.com, sprevidi@cisco.com
  RFC7824          ||      S. Krishnan, T. Mrugalski, S. Jiang         ||       suresh.krishnan@ericsson.com, tomasz.mrugalski@gmail.com, jiangsheng@huawei.com
  RFC7825          ||      J. Goldberg, M. Westerlund, T. Zeng         ||       jgoldber@cisco.com, magnus.westerlund@ericsson.com, thomas.zeng@gmail.com
  RFC7826          ||      H. Schulzrinne, A. Rao, R. Lanphier, M. Westerlund, M. Stiemerling, Ed.         ||       schulzrinne@cs.columbia.edu, anrao@cisco.com, robla@robla.net, magnus.westerlund@ericsson.com, mls.ietf@gmail.com
  RFC7827          ||      L. Eggert         ||       lars@netapp.com
  RFC7828          ||      P. Wouters, J. Abley, S. Dickinson, R. Bellis         ||       pwouters@redhat.com, jabley@dyn.com, sara@sinodun.com, ray@isc.org
  RFC7829          ||      Y. Nishida, P. Natarajan, A. Caro, P. Amer, K. Nielsen         ||       nishida@wide.ad.jp, prenatar@cisco.com, acaro@bbn.com, amer@udel.edu, karen.nielsen@tieto.com
  RFC7830          ||      A. Mayrhofer         ||       alex.mayrhofer.ietf@gmail.com
  RFC7831          ||      J. Howlett, S. Hartman, H. Tschofenig, J. Schaad         ||       josh.howlett@ja.net, hartmans-ietf@mit.edu, Hannes.Tschofenig@gmx.net, ietf@augustcellars.com
  RFC7832          ||      R. Smith, Ed.         ||       rhys.smith@jisc.ac.uk
  RFC7833          ||      J. Howlett, S. Hartman, A. Perez-Mendez, Ed.         ||       josh.howlett@ja.net, hartmans-ietf@mit.edu, alex@um.es
  RFC7834          ||      D. Saucez, L. Iannone, A. Cabellos, F. Coras         ||       damien.saucez@inria.fr, ggx@gigix.net, acabello@ac.upc.edu, fcoras@ac.upc.edu
  RFC7835          ||      D. Saucez, L. Iannone, O. Bonaventure         ||       damien.saucez@inria.fr, ggx@gigix.net, Olivier.Bonaventure@uclouvain.be
  RFC7836          ||      S. Smyshlyaev, Ed., E. Alekseev, I. Oshkin, V. Popov, S. Leontiev, V. Podobaev, D. Belyavsky         ||       svs@cryptopro.ru, alekseev@cryptopro.ru, oshkin@cryptopro.ru, vpopov@cryptopro.ru, lse@CryptoPro.ru, v_podobaev@factor-ts.ru, beldmit@gmail.com
  RFC7837          ||      S. Krishnan, M. Kuehlewind, B. Briscoe, C. Ralli         ||       suresh.krishnan@ericsson.com, mirja.kuehlewind@tik.ee.ethz.ch, ietf@bobbriscoe.net, ralli@tid.es
  RFC7838          ||      M. Nottingham, P. McManus, J. Reschke         ||       mnot@mnot.net, mcmanus@ducksong.com, julian.reschke@greenbytes.de
  RFC7839          ||      S. Bhandari, S. Gundavelli, M. Grayson, B. Volz, J. Korhonen         ||       shwethab@cisco.com, sgundave@cisco.com, mgrayson@cisco.com, volz@cisco.com, jouni.nospam@gmail.com
  RFC7840          ||      J. Winterbottom, H. Tschofenig, L. Liess         ||       a.james.winterbottom@gmail.com, Hannes.Tschofenig@gmx.net, L.Liess@telekom.de
  RFC7841          ||      J. Halpern, Ed., L. Daigle, Ed., O. Kolkman, Ed.         ||       jmh@joelhalpern.com, ldaigle@thinkingcat.com, kolkman@isoc.org
  RFC7842          ||      R. Sparks         ||       rjsparks@nostrum.com
  RFC7843          ||      A. Ripke, R. Winter, T. Dietz, J. Quittek, R. da Silva         ||       ripke@neclab.eu, winter@neclab.eu, dietz@neclab.eu, quittek@neclab.eu, rafaelalejandro.lopezdasilva@telefonica.com
  RFC7844          ||      C. Huitema, T. Mrugalski, S. Krishnan         ||       huitema@microsoft.com, tomasz.mrugalski@gmail.com, suresh.krishnan@ericsson.com
  RFC7845          ||      T. Terriberry, R. Lee, R. Giles         ||       tterribe@xiph.org, ron@debian.org, giles@xiph.org
  RFC7846          ||      R. Cruz, M. Nunes, J. Xia, R. Huang, Ed., J. Taveira, D. Lingli         ||       rui.cruz@ieee.org, mario.nunes@inov.pt, xiajinwei@huawei.com, rachel.huang@huawei.com, joao.silva@inov.pt, denglingli@chinamobile.com
  RFC7847          ||      T. Melia, Ed., S. Gundavelli, Ed.         ||       telemaco.melia@gmail.com, sgundave@cisco.com
  RFC7848          ||      G. Lozano         ||       gustavo.lozano@icann.org
  RFC7849          ||      D. Binet, M. Boucadair, A. Vizdal, G. Chen, N. Heatley, R. Chandler, D. Michaud, D. Lopez, W. Haeffner         ||       david.binet@orange.com, mohamed.boucadair@orange.com, Ales.Vizdal@T-Mobile.cz, phdgang@gmail.com, nick.heatley@ee.co.uk, ross@eircom.net, dave.michaud@rci.rogers.com, diego.r.lopez@telefonica.com, walter.haeffner@vodafone.com
  RFC7850          ||      S. Nandakumar         ||       snandaku@cisco.com
  RFC7851          ||      H. Song, X. Jiang, R. Even, D. Bryan, Y. Sun         ||       haibin.song@huawei.com, jiangxingfeng@huawei.com, ron.even.tlv@gmail.com, dbryan@ethernot.org, sunyi@ict.ac.cn
  RFC7852          ||      R. Gellens, B. Rosen, H. Tschofenig, R. Marshall, J. Winterbottom         ||       rg+ietf@randy.pensive.org, br@brianrosen.net, Hannes.Tschofenig@gmx.net, rmarshall@telecomsys.com, a.james.winterbottom@gmail.com
  RFC7853          ||      S. Martin, S. Tuecke, B. McCollam, M. Lidman         ||       sjmartin@uchicago.edu, tuecke@globus.org, bmccollam@uchicago.edu, mattias@uchicago.edu<
  RFC7854          ||      J. Scudder, Ed., R. Fernando, S. Stuart         ||       jgs@juniper.net, rex@cisco.com, sstuart@google.com
  RFC7855          ||      S. Previdi, Ed., C. Filsfils, Ed., B. Decraene, S. Litkowski, M. Horneffer, R. Shakir         ||       sprevidi@cisco.com, cfilsfil@cisco.com, bruno.decraene@orange.com, stephane.litkowski@orange.com, Martin.Horneffer@telekom.de, rjs@rob.sh
  RFC7856          ||      Y. Cui, J. Dong, P. Wu, M. Xu, A. Yla-Jaaski         ||       yong@csnet1.cs.tsinghua.edu.cn, knight.dongjiang@gmail.com, weapon9@gmail.com, xmw@cernet.edu.cn, antti.yla-jaaski@aalto.fi
  RFC7857          ||      R. Penno, S. Perreault, M. Boucadair, Ed., S. Sivakumar, K. Naito         ||       repenno@cisco.com, sperreault@jive.com, mohamed.boucadair@orange.com, ssenthil@cisco.com, k.naito@nttv6.jp
  RFC7858          ||      Z. Hu, L. Zhu, J. Heidemann, A. Mankin, D. Wessels, P. Hoffman         ||       zihu@outlook.com, liangzhu@usc.edu, johnh@isi.edu, allison.mankin@gmail.com, dwessels@verisign.com, paul.hoffman@icann.org
  RFC7859          ||      C. Dearlove         ||       chris.dearlove@baesystems.com
  RFC7860          ||      J. Merkle, Ed., M. Lochter         ||       johannes.merkle@secunet.com, manfred.lochter@bsi.bund.de
  RFC7861          ||      A. Adamson, N. Williams         ||       andros@netapp.com, nico@cryptonector.com
  RFC7862          ||      T. Haynes         ||       thomas.haynes@primarydata.com
  RFC7863          ||      T. Haynes         ||       thomas.haynes@primarydata.com
  RFC7864          ||      CJ. Bernardos, Ed.         ||       cjbc@it.uc3m.es
  RFC7865          ||      R. Ravindranath, P. Ravindran, P. Kyzivat         ||       rmohanr@cisco.com, partha@parthasarathi.co.in, pkyzivat@alum.mit.edu
  RFC7866          ||      L. Portman, H. Lum, Ed., C. Eckel, A. Johnston, A. Hutton         ||       leon.portman@gmail.com, henry.lum@genesyslab.com, eckelcu@cisco.com, alan.b.johnston@gmail.com, andrew.hutton@unify.com
  RFC7867          ||      R. Huang         ||       rachel.huang@huawei.com
  RFC7868          ||      D. Savage, J. Ng, S. Moore, D. Slice, P. Paluch, R. White         ||       dsavage@cisco.com, jamng@cisco.com, smoore@cisco.com, dslice@cumulusnetworks.com, peter.paluch@fri.uniza.sk, russ@riw.us
  RFC7869          ||      D. Warden, I. Iordanov         ||       david_warden@dell.com, iiordanov@gmail.com
  RFC7870          ||      Y. Fu, S. Jiang, J. Dong, Y. Chen         ||       fuyu@cnnic.cn, jiangsheng@huawei.com, knight.dongjiang@gmail.com, flashfoxmx@gmail.com
  RFC7871          ||      C. Contavalli, W. van der Gaast, D. Lawrence, W. Kumari         ||       ccontavalli@google.com, wilmer@google.com, tale@akamai.com, warren@kumari.net
  RFC7872          ||      F. Gont, J. Linkova, T. Chown, W. Liu         ||       fgont@si6networks.com, furry@google.com, tim.chown@jisc.ac.uk, liushucheng@huawei.com
  RFC7873          ||      D. Eastlake 3rd, M. Andrews         ||       d3e3e3@gmail.com, marka@isc.org
  RFC7874          ||      JM. Valin, C. Bran         ||       jmvalin@jmvalin.ca, cary.bran@plantronics.com
  RFC7875          ||      S. Proust, Ed.         ||       stephane.proust@orange.com
  RFC7876          ||      S. Bryant, S. Sivabalan, S. Soni         ||       stewart.bryant@gmail.com, msiva@cisco.com, sagsoni@cisco.com
  RFC7877          ||      K. Cartwright, V. Bhatia, S. Ali, D. Schwartz         ||       kcartwright@tnsi.com, vbhatia@tnsi.com, syed.ali@neustar.biz, dschwartz@xconnect.net
  RFC7878          ||      K. Cartwright, V. Bhatia, J-F. Mule, A. Mayrhofer         ||       kcartwright@tnsi.com, vbhatia@tnsi.com, jfmule@apple.com, alexander.mayrhofer@nic.at
  RFC7879          ||      R. Ravindranath, T. Reddy, G. Salgueiro, V. Pascual, P. Ravindran         ||       rmohanr@cisco.com, tireddy@cisco.com, gsalguei@cisco.com, victor.pascual.avila@oracle.com, partha@parthasarathi.co.in
  RFC7880          ||      C. Pignataro, D. Ward, N. Akiya, M. Bhatia, S. Pallagatti         ||       cpignata@cisco.com, wardd@cisco.com, nobo.akiya.dev@gmail.com, manav@ionosnetworks.com, santosh.pallagatti@gmail.com
  RFC7881          ||      C. Pignataro, D. Ward, N. Akiya         ||       cpignata@cisco.com, wardd@cisco.com, nobo.akiya.dev@gmail.com
  RFC7882          ||      S. Aldrin, C. Pignataro, G. Mirsky, N. Kumar         ||       aldrin.ietf@gmail.com, cpignata@cisco.com, gregory.mirsky@ericsson.com, naikumar@cisco.com
  RFC7883          ||      L. Ginsberg, N. Akiya, M. Chen         ||       ginsberg@cisco.com, nobo.akiya.dev@gmail.com, mach.chen@huawei.com
  RFC7884          ||      C. Pignataro, M. Bhatia, S. Aldrin, T. Ranganath         ||       cpignata@cisco.com, manav@ionosnetworks.com, aldrin.ietf@gmail.com, trilok.ranganatha@nokia.com
  RFC7885          ||      V. Govindan, C. Pignataro         ||       venggovi@cisco.com, cpignata@cisco.com
  RFC7886          ||      V. Govindan, C. Pignataro         ||       venggovi@cisco.com, cpignata@cisco.com
  RFC7887          ||      S. Venaas, J. Arango, I. Kouvelas         ||       stig@cisco.com, jearango@cisco.com, kouvelas@arista.com
  RFC7888          ||      A. Melnikov, Ed.         ||       alexey.melnikov@isode.com
  RFC7889          ||      J. SrimushnamBoovaraghamoorthy, N. Bisht         ||       jayantheesh.sb@gmail.com, narendrasingh.bisht@gmail.com
  RFC7890          ||      D. Bryan, P. Matthews, E. Shim, D. Willis, S. Dawkins         ||       dbryan@ethernot.org, philip_matthews@magma.ca, eunsooshim@gmail.com, dean.willis@softarmor.com, spencerdawkins.ietf@gmail.com
  RFC7891          ||      J. Asghar, IJ. Wijnands, Ed., S. Krishnaswamy, A. Karan, V. Arya         ||       jasghar@cisco.com, ice@cisco.com, sowkrish@cisco.com, apoorva@cisco.com, varya@directv.com
  RFC7892          ||      Z. Ali, A. Bonfanti, M. Hartley, F. Zhang         ||       zali@cisco.com, abonfant@cisco.com, mhartley@cisco.com, zhangfatai@huawei.com
  RFC7893          ||      Y(J) Stein, D. Black, B. Briscoe         ||       yaakov_s@rad.com, david.black@emc.com, ietf@bobbriscoe.net
  RFC7894          ||      M. Pritikin, C. Wallace         ||       pritikin@cisco.com, carl@redhoundsoftware.com
  RFC7895          ||      A. Bierman, M. Bjorklund, K. Watsen         ||       andy@yumaworks.com, mbj@tail-f.com, kwatsen@juniper.net
  RFC7896          ||      D. Dhody         ||       dhruv.ietf@gmail.com
  RFC7897          ||      D. Dhody, U. Palle, R. Casellas         ||       dhruv.ietf@gmail.com, udayasree.palle@huawei.com, ramon.casellas@cttc.es
  RFC7898          ||      D. Dhody, U. Palle, V. Kondreddy, R. Casellas         ||       dhruv.ietf@gmail.com, udayasree.palle@huawei.com, venugopalreddyk@huawei.com, ramon.casellas@cttc.es
  RFC7899          ||      T. Morin, Ed., S. Litkowski, K. Patel, Z. Zhang, R. Kebler, J. Haas         ||       thomas.morin@orange.com, stephane.litkowski@orange.com, keyupate@cisco.com, zzhang@juniper.net, rkebler@juniper.net, jhaas@juniper.net
  RFC7900          ||      Y. Rekhter, Ed., E. Rosen, Ed., R. Aggarwal, Y. Cai, T. Morin         ||       none, erosen@juniper.net, raggarwa_1@yahoo.com, yiqun.cai@alibaba-inc.com, thomas.morin@orange.com
  RFC7901          ||      P. Wouters         ||       pwouters@redhat.com
  RFC7902          ||      E. Rosen, T. Morin         ||       erosen@juniper.net, thomas.morin@orange.com
  RFC7903          ||      S. Leonard         ||       dev+ietf@seantek.com
  RFC7904          ||      C. Jennings, B. Lowekamp, E. Rescorla, S. Baset, H. Schulzrinne, T. Schmidt, Ed.         ||       fluffy@cisco.com, bbl@lowekamp.net, ekr@rtfm.com, sabaset@us.ibm.com, hgs@cs.columbia.edu, t.schmidt@haw-hamburg.de
  RFC7905          ||      A. Langley, W. Chang, N. Mavrogiannopoulos, J. Strombergson, S. Josefsson         ||       agl@google.com, wtc@google.com, nmav@redhat.com, joachim@secworks.se, simon@josefsson.org
  RFC7906          ||      P. Timmel, R. Housley, S. Turner         ||       pstimme@nsa.gov, housley@vigilsec.com, turners@ieca.com
  RFC7908          ||      K. Sriram, D. Montgomery, D. McPherson, E. Osterweil, B. Dickson         ||       ksriram@nist.gov, dougm@nist.gov, dmcpherson@verisign.com, eosterweil@verisign.com, brian.peter.dickson@gmail.com
  RFC7909          ||      R. Kisteleki, B. Haberman         ||       robert@ripe.net, brian@innovationslab.net
  RFC7910          ||      W. Zhou         ||       zhouweiisu@gmail.com
  RFC7911          ||      D. Walton, A. Retana, E. Chen, J. Scudder         ||       dwalton@cumulusnetworks.com, aretana@cisco.com, enkechen@cisco.com, jgs@juniper.net
  RFC7912          ||      A. Melnikov         ||       alexey.melnikov@isode.com
  RFC7913          ||      C. Holmberg         ||       christer.holmberg@ericsson.com
  RFC7914          ||      C. Percival, S. Josefsson         ||       cperciva@tarsnap.com, simon@josefsson.org
  RFC7915          ||      C. Bao, X. Li, F. Baker, T. Anderson, F. Gont         ||       congxiao@cernet.edu.cn, xing@cernet.edu.cn, fred@cisco.com, tore@redpill-linpro.com, fgont@si6networks.com
  RFC7916          ||      S. Litkowski, Ed., B. Decraene, C. Filsfils, K. Raza, M. Horneffer, P. Sarkar         ||       stephane.litkowski@orange.com, bruno.decraene@orange.com, cfilsfil@cisco.com, skraza@cisco.com, Martin.Horneffer@telekom.de, pushpasis.ietf@gmail.com
  RFC7917          ||      P. Sarkar, Ed., H. Gredler, S. Hegde, S. Litkowski, B. Decraene         ||       pushpasis.ietf@gmail.com, hannes@rtbrick.com, shraddha@juniper.net, stephane.litkowski@orange.com, bruno.decraene@orange.com
  RFC7918          ||      A. Langley, N. Modadugu, B. Moeller         ||       agl@google.com, nagendra@cs.stanford.edu, bmoeller@acm.org
  RFC7919          ||      D. Gillmor         ||       dkg@fifthhorseman.net
  RFC7920          ||      A. Atlas, Ed., T. Nadeau, Ed., D. Ward         ||       akatlas@juniper.net, tnadeau@lucidvision.com, wardd@cisco.com
  RFC7921          ||      A. Atlas, J. Halpern, S. Hares, D. Ward, T. Nadeau         ||       akatlas@juniper.net, joel.halpern@ericsson.com, shares@ndzh.com, wardd@cisco.com, tnadeau@lucidvision.com
  RFC7922          ||      J. Clarke, G. Salgueiro, C. Pignataro         ||       jclarke@cisco.com, gsalguei@cisco.com, cpignata@cisco.com
  RFC7923          ||      E. Voit, A. Clemm, A. Gonzalez Prieto         ||       evoit@cisco.com, alex@cisco.com, albertgo@cisco.com
  RFC7924          ||      S. Santesson, H. Tschofenig         ||       sts@aaa-sec.com, Hannes.Tschofenig@gmx.net
  RFC7925          ||      H. Tschofenig, Ed., T. Fossati         ||       Hannes.Tschofenig@gmx.net, thomas.fossati@nokia.com
  RFC7926          ||      A. Farrel, Ed., J. Drake, N. Bitar, G. Swallow, D. Ceccarelli, X. Zhang         ||       adrian@olddog.co.uk, jdrake@juniper.net, nbitar40@gmail.com, swallow@cisco.com, daniele.ceccarelli@ericsson.com, zhang.xian@huawei.com
  RFC7927          ||      D. Kutscher, Ed., S. Eum, K. Pentikousis, I. Psaras, D. Corujo, D. Saucez, T. Schmidt, M. Waehlisch         ||       kutscher@neclab.eu, suyong@ist.osaka-u.ac.jp, k.pentikousis@travelping.com, i.psaras@ucl.ac.uk, dcorujo@av.it.pt, damien.saucez@inria.fr, t.schmidt@haw-hamburg.de, waehlisch@ieee.org
  RFC7928          ||      N. Kuhn, Ed., P. Natarajan, Ed., N. Khademi, Ed., D. Ros         ||       nicolas.kuhn@cnes.fr, prenatar@cisco.com, naeemk@ifi.uio.no, dros@simula.no
  RFC7929          ||      P. Wouters         ||       pwouters@redhat.com
  RFC7930          ||      S. Hartman         ||       hartmans-ietf@mit.edu
  RFC7931          ||      D. Noveck, Ed., P. Shivam, C. Lever, B. Baker         ||       davenoveck@gmail.com, piyush.shivam@oracle.com, chuck.lever@oracle.com, bill.baker@oracle.com
  RFC7932          ||      J. Alakuijala, Z. Szabadka         ||       jyrki@google.com, szabadka@google.com
  RFC7933          ||      C. Westphal, Ed., S. Lederer, D. Posch, C. Timmerer, A. Azgin, W. Liu, C. Mueller, A. Detti, D. Corujo, J. Wang, M. Montpetit, N. Murray         ||       Cedric.Westphal@huawei.com, stefan.lederer@itec.aau.at, daniel.posch@itec.aau.at, christian.timmerer@itec.aau.at, aytac.azgin@huawei.com, liushucheng@huawei.com, christopher.mueller@bitmovin.net, andrea.detti@uniroma2.it, dcorujo@av.it.pt, jianwang@cityu.edu.hk, marie@mjmontpetit.com, nmurray@research.ait.ie
  RFC7934          ||      L. Colitti, V. Cerf, S. Cheshire, D. Schinazi         ||       lorenzo@google.com, vint@google.com, cheshire@apple.com, dschinazi@apple.com
  RFC7935          ||      G. Huston, G. Michaelson, Ed.         ||       gih@apnic.net, ggm@apnic.net
  RFC7936          ||      T. Hardie         ||       ted.ietf@gmail.com
  RFC7937          ||      F. Le Faucheur, Ed., G. Bertrand, Ed., I. Oprescu, Ed., R. Peterkofsky         ||       flefauch@gmail.com, gilbertrand@gmail.com, iuniana.oprescu@gmail.com, peterkofsky@google.com
  RFC7938          ||      P. Lapukhov, A. Premji, J. Mitchell, Ed.         ||       petr@fb.com, ariff@arista.com, jrmitche@puck.nether.net
  RFC7939          ||      U. Herberg, R. Cole, I. Chakeres, T. Clausen         ||       ulrich@herberg.name, rgcole01@comcast.net, ian.chakeres@gmail.com, T.Clausen@computer.org
  RFC7940          ||      K. Davies, A. Freytag         ||       kim.davies@icann.org, asmus@unicode.org
  RFC7941          ||      M. Westerlund, B. Burman, R. Even, M. Zanaty         ||       magnus.westerlund@ericsson.com, bo.burman@ericsson.com, roni.even@mail01.huawei.com, mzanaty@cisco.com
  RFC7942          ||      Y. Sheffer, A. Farrel         ||       yaronf.ietf@gmail.com, adrian@olddog.co.uk
  RFC7943          ||      F. Gont, W. Liu         ||       fgont@si6networks.com, liushucheng@huawei.com
  RFC7944          ||      S. Donovan         ||       srdonovan@usdonovans.com
  RFC7945          ||      K. Pentikousis, Ed., B. Ohlman, E. Davies, S. Spirou, G. Boggia         ||       k.pentikousis@travelping.com, Borje.Ohlman@ericsson.com, davieseb@scss.tcd.ie, spis@intracom-telecom.com, g.boggia@poliba.it
  RFC7946          ||      H. Butler, M. Daly, A. Doyle, S. Gillies, S. Hagen, T. Schaub         ||       howard@hobu.co, martin.daly@cadcorp.com, adoyle@intl-interfaces.com, sean.gillies@gmail.com, stefan@hagen.link, tim.schaub@gmail.com
  RFC7947          ||      E. Jasinska, N. Hilliard, R. Raszuk, N. Bakker         ||       elisa@bigwaveit.org, nick@inex.ie, robert@raszuk.net, nbakker@akamai.com
  RFC7948          ||      N. Hilliard, E. Jasinska, R. Raszuk, N. Bakker         ||       nick@inex.ie, elisa@bigwaveit.org, robert@raszuk.net, nbakker@akamai.com
  RFC7949          ||      I. Chen, A. Lindem, R. Atkinson         ||       ichen@kuatrotech.com, acee@cisco.com, rja.lists@gmail.com
  RFC7950          ||      M. Bjorklund, Ed.         ||       mbj@tail-f.com
  RFC7951          ||      L. Lhotka         ||       lhotka@nic.cz
  RFC7952          ||      L. Lhotka         ||       lhotka@nic.cz
  RFC7953          ||      C. Daboo, M. Douglass         ||       cyrus@daboo.name, mdouglass@sphericalcowgroup.com
  RFC7954          ||      L. Iannone, D. Lewis, D. Meyer, V. Fuller         ||       ggx@gigix.net, darlewis@cisco.com, dmm@1-4-5.net, vaf@vaf.net
  RFC7955          ||      L. Iannone, R. Jorgensen, D. Conrad, G. Huston         ||       ggx@gigix.net, rogerj@gmail.com, drc@virtualized.org, gih@apnic.net
  RFC7956          ||      W. Hao, Y. Li, A. Qu, M. Durrani, P. Sivamurugan         ||       haoweiguo@huawei.com, liyizhou@huawei.com, laodulaodu@gmail.com, mdurrani@equinix.com, ponkarthick.sivamurugan@ipinfusion.com
  RFC7957          ||      B. Campbell, Ed., A. Cooper, B. Leiba         ||       ben@nostrum.com, alcoop@cisco.com, barryleiba@computer.org
  RFC7958          ||      J. Abley, J. Schlyter, G. Bailey, P. Hoffman         ||       jabley@dyn.com, jakob@kirei.se, guillaumebailey@outlook.com, paul.hoffman@icann.org
  RFC7959          ||      C. Bormann, Z. Shelby, Ed.         ||       cabo@tzi.org, zach.shelby@arm.com
  RFC7960          ||      F. Martin, Ed., E. Lear, Ed., T. Draegen. Ed., E. Zwicky, Ed., K. Andersen, Ed.         ||       fmartin@linkedin.com, lear@cisco.com, tim@dmarcian.com, zwicky@yahoo-inc.com, kandersen@linkedin.com
  RFC7961          ||      D. Eastlake 3rd, L. Yizhou         ||       d3e3e3@gmail.com, liyizhou@huawei.com
  RFC7962          ||      J. Saldana, Ed., A. Arcia-Moret, B. Braem, E. Pietrosemoli, A. Sathiaseelan, M. Zennaro         ||       jsaldana@unizar.es, andres.arcia@cl.cam.ac.uk, bart.braem@iminds.be, ermanno@ictp.it, arjuna.sathiaseelan@cl.cam.ac.uk, mzennaro@ictp.it
  RFC7963          ||      Z. Ali, A. Bonfanti, M. Hartley, F. Zhang         ||       zali@cisco.com, abonfant@cisco.com, mhartley@cisco.com, zhangfatai@huawei.com
  RFC7964          ||      D. Walton, A. Retana, E. Chen, J. Scudder         ||       dwalton@cumulusnetworks.com, aretana@cisco.com, enkechen@cisco.com, jgs@juniper.net
  RFC7965          ||      M. Chen, W. Cao, A. Takacs, P. Pan         ||       mach.chen@huawei.com, wayne.caowei@huawei.com, attila.takacs@ericsson.com, none
  RFC7966          ||      H. Tschofenig, J. Korhonen, Ed., G. Zorn, K. Pillay         ||       Hannes.tschofenig@gmx.net, jouni.nospam@gmail.com, glenzorn@gmail.com, kervin.pillay@gmail.com
  RFC7967          ||      A. Bhattacharyya, S. Bandyopadhyay, A. Pal, T. Bose         ||       abhijan.bhattacharyya@tcs.com, soma.bandyopadhyay@tcs.com, arpan.pal@tcs.com, tulika.bose@tcs.com
  RFC7968          ||      Y. Li, D. Eastlake 3rd, W. Hao, H. Chen, S. Chatterjee         ||       liyizhou@huawei.com, d3e3e3@gmail.com, haoweiguo@huawei.com, philips.chenhao@huawei.com, somnath.chatterjee01@gmail.com
  RFC7969          ||      T. Lemon, T. Mrugalski         ||       ted.lemon@nominum.com, tomasz.mrugalski@gmail.com
  RFC7970          ||      R. Danyliw         ||       rdd@cert.org
  RFC7971          ||      M. Stiemerling, S. Kiesel, M. Scharf, H. Seidel, S. Previdi         ||       mls.ietf@gmail.com, ietf-alto@skiesel.de, michael.scharf@nokia.com, hseidel@benocs.com, sprevidi@cisco.com
  RFC7972          ||      P. Lemieux         ||       pal@sandflow.com
  RFC7973          ||      R. Droms, P. Duffy         ||       rdroms.ietf@gmail.com, paduffy@cisco.com
  RFC7974          ||      B. Williams, M. Boucadair, D. Wing         ||       brandon.williams@akamai.com, mohamed.boucadair@orange.com, dwing-ietf@fuggles.com
  RFC7975          ||      B. Niven-Jenkins, Ed., R. van Brandenburg, Ed.         ||       ben.niven-jenkins@nokia.com, ray.vanbrandenburg@tno.nl
  RFC7976          ||      C. Holmberg, N. Biondic, G. Salgueiro         ||       christer.holmberg@ericsson.com, nevenka.biondic@ericsson.com, gsalguei@cisco.com
  RFC7977          ||      P. Dunkley, G. Llewellyn, V. Pascual, G. Salgueiro, R. Ravindranath         ||       peter.dunkley@xura.com, gavin.llewellyn@xura.com, victor.pascual.avila@oracle.com, gsalguei@cisco.com, rmohanr@cisco.com
  RFC7978          ||      D. Eastlake 3rd, M. Umair, Y. Li         ||       d3e3e3@gmail.com, mohammed.umair2@gmail.com, liyizhou@huawei.com
  RFC7979          ||      E. Lear, Ed., R. Housley, Ed.         ||       lear@cisco.com, housley@vigilsec.com
  RFC7980          ||      M. Behringer, A. Retana, R. White, G. Huston         ||       mbehring@cisco.com, aretana@cisco.com, russw@riw.us, gih@apnic.net
  RFC7981          ||      L. Ginsberg, S. Previdi, M. Chen         ||       ginsberg@cisco.com, sprevidi@cisco.com, mach.chen@huawei.com
  RFC7982          ||      P. Martinsen, T. Reddy, D. Wing, V. Singh         ||       palmarti@cisco.com, tireddy@cisco.com, dwing-ietf@fuggles.com, varun@callstats.io
  RFC7983          ||      M. Petit-Huguenin, G. Salgueiro         ||       marc@petit-huguenin.org, gsalguei@cisco.com
  RFC7984          ||      O. Johansson, G. Salgueiro, V. Gurbani, D. Worley, Ed.         ||       oej@edvina.net, gsalguei@cisco.com, vkg@bell-labs.com, worley@ariadne.com
  RFC7985          ||      J. Yi, T. Clausen, U. Herberg         ||       jiazi@jiaziyi.com, T.Clausen@computer.org, ulrich@herberg.name
  RFC7986          ||      C. Daboo         ||       cyrus@daboo.name
  RFC7987          ||      L. Ginsberg, P. Wells, B. Decraene, T. Przygienda, H. Gredler         ||       ginsberg@cisco.com, pauwells@cisco.com, bruno.decraene@orange.com, prz@juniper.net, hannes@rtbrick.com
  RFC7988          ||      E. Rosen, Ed., K. Subramanian, Z. Zhang         ||       erosen@juniper.net, karthik@sproute.com, zzhang@juniper.net
  RFC7989          ||      P. Jones, G. Salgueiro, C. Pearce, P. Giralt         ||       paulej@packetizer.com, gsalguei@cisco.com, chrep@cisco.com, pgiralt@cisco.com
  RFC7990          ||      H. Flanagan         ||       rse@rfc-editor.org
  RFC7991          ||      P. Hoffman         ||       paul.hoffman@icann.org
  RFC7992          ||      J. Hildebrand, Ed., P. Hoffman         ||       joe-ietf@cursive.net, paul.hoffman@icann.org
  RFC7993          ||      H. Flanagan         ||       rse@rfc-editor.org
  RFC7994          ||      H. Flanagan         ||       rse@rfc-editor.org
  RFC7995          ||      T. Hansen, Ed., L. Masinter, M. Hardy         ||       tony@att.com, masinter@adobe.com, mahardy@adobe.com
  RFC7996          ||      N. Brownlee         ||       n.brownlee@auckland.ac.nz
  RFC7997          ||      H. Flanagan, Ed.         ||       rse@rfc-editor.org
  RFC7998          ||      P. Hoffman, J. Hildebrand         ||       paul.hoffman@icann.org, joe-ietf@cursive.net
  RFC7999          ||      T. King, C. Dietzel, J. Snijders, G. Doering, G. Hankins         ||       thomas.king@de-cix.net, christoph.dietzel@de-cix.net, job@ntt.net, gert@space.net, greg.hankins@nokia.com
  RFC8000          ||      A. Adamson, N. Williams         ||       andros@netapp.com, nico@cryptonector.com
  RFC8001          ||      F. Zhang, Ed., O. Gonzalez de Dios, Ed., C. Margaria, M. Hartley, Z. Ali         ||       zhangfatai@huawei.com, oscar.gonzalezdedios@telefonica.com, cmargaria@juniper.net, mhartley@cisco.com, zali@cisco.com
  RFC8002          ||      T. Heer, S. Varjonen         ||       heer@hs-albsig.de, samu.varjonen@helsinki.fi
  RFC8003          ||      J. Laganier, L. Eggert         ||       julien.ietf@gmail.com, lars@netapp.com
  RFC8004          ||      J. Laganier, L. Eggert         ||       julien.ietf@gmail.com, lars@netapp.com
  RFC8005          ||      J. Laganier         ||       julien.ietf@gmail.com
  RFC8006          ||      B. Niven-Jenkins, R. Murray, M. Caulfield, K. Ma         ||       ben.niven-jenkins@nokia.com, rob.murray@nokia.com, mcaulfie@cisco.com, kevin.j.ma@ericsson.com
  RFC8007          ||      R. Murray, B. Niven-Jenkins         ||       rob.murray@nokia.com, ben.niven-jenkins@nokia.com
  RFC8008          ||      J. Seedorf, J. Peterson, S. Previdi, R. van Brandenburg, K. Ma         ||       jan.seedorf@hft-stuttgart.de, jon.peterson@neustar.biz, sprevidi@cisco.com, ray.vanbrandenburg@tno.nl, kevin.j.ma@ericsson.com
  RFC8009          ||      M. Jenkins, M. Peck, K. Burgin         ||       mjjenki@tycho.ncsc.mil, mpeck@mitre.org, kelley.burgin@gmail.com
  RFC8010          ||      M. Sweet, I. McDonald         ||       msweet@apple.com, blueroofmusic@gmail.com
  RFC8011          ||      M. Sweet, I. McDonald         ||       msweet@apple.com, blueroofmusic@gmail.com
  RFC8012          ||      N. Akiya, G. Swallow, C. Pignataro, A. Malis, S. Aldrin         ||       nobo.akiya.dev@gmail.com, swallow@cisco.com, cpignata@cisco.com, agmalis@gmail.com, aldrin.ietf@gmail.com
  RFC8013          ||      D. Joachimpillai, J. Hadi Salim         ||       damascene.joachimpillai@verizon.com, hadi@mojatatu.com
  RFC8014          ||      D. Black, J. Hudson, L. Kreeger, M. Lasserre, T. Narten         ||       david.black@dell.com, jon.hudson@gmail.com, lkreeger@gmail.com, mmlasserre@gmail.com, narten@us.ibm.com
  RFC8015          ||      V. Singh, C. Perkins, A. Clark, R. Huang         ||       varun@callstats.io, csp@csperkins.org, alan.d.clark@telchemy.com, Rachel@huawei.com
  RFC8016          ||      T. Reddy, D. Wing, P. Patil, P. Martinsen         ||       tireddy@cisco.com, dwing-ietf@fuggles.com, praspati@cisco.com, palmarti@cisco.com
  RFC8017          ||      K. Moriarty, Ed., B. Kaliski, J. Jonsson, A. Rusch         ||       Kathleen.Moriarty@emc.com, bkaliski@verisign.com, jakob.jonsson@subset.se, andreas.rusch@rsa.com
  RFC8018          ||      K. Moriarty, Ed., B. Kaliski, A. Rusch         ||       Kathleen.Moriarty@Dell.com, bkaliski@verisign.com, andreas.rusch@rsa.com
  RFC8019          ||      Y. Nir, V. Smyslov         ||       ynir.ietf@gmail.com, svan@elvis.ru
  RFC8020          ||      S. Bortzmeyer, S. Huque         ||       bortzmeyer+ietf@nic.fr, shuque@verisign.com
  RFC8021          ||      F. Gont, W. Liu, T. Anderson         ||       fgont@si6networks.com, liushucheng@huawei.com, tore@redpill-linpro.com
  RFC8022          ||      L. Lhotka, A. Lindem         ||       lhotka@nic.cz, acee@cisco.com
  RFC8023          ||      M. Thomas, A. Mankin, L. Zhang         ||       mthomas@verisign.com, allison.mankin@gmail.com, lixia@cs.ucla.edu
  RFC8024          ||      Y. Jiang, Ed., Y. Luo, E. Mallette, Ed., Y. Shen, W. Cheng         ||       jiangyuanlong@huawei.com, dennis.luoyong@huawei.com, edwin.mallette@gmail.com, yshen@juniper.net, chengweiqiang@chinamobile.com
  RFC8025          ||      P. Thubert, Ed., R. Cragie         ||       pthubert@cisco.com, robert.cragie@gridmerge.com
  RFC8026          ||      M. Boucadair, I. Farrer         ||       mohamed.boucadair@orange.com, ian.farrer@telekom.de
  RFC8027          ||      W. Hardaker, O. Gudmundsson, S. Krishnaswamy         ||       ietf@hardakers.net, olafur+ietf@cloudflare.com, suresh@tislabs.com
  RFC8028          ||      F. Baker, B. Carpenter         ||       fredbaker.ietf@gmail.com, brian.e.carpenter@gmail.com
  RFC8029          ||      K. Kompella, G. Swallow, C. Pignataro, Ed., N. Kumar, S. Aldrin, M. Chen         ||       kireeti.kompella@gmail.com, swallow.ietf@gmail.com, cpignata@cisco.com, naikumar@cisco.com, aldrin.ietf@gmail.com, mach.chen@huawei.com
  RFC8030          ||      M. Thomson, E. Damaggio, B. Raymor, Ed.         ||       martin.thomson@gmail.com, elioda@microsoft.com, brian.raymor@microsoft.com
  RFC8031          ||      Y. Nir, S. Josefsson         ||       ynir.ietf@gmail.com, simon@josefsson.org
  RFC8032          ||      S. Josefsson, I. Liusvaara         ||       simon@josefsson.org, ilariliusvaara@welho.com
  RFC8033          ||      R. Pan, P. Natarajan, F. Baker, G. White         ||       ropan@cisco.com, prenatar@cisco.com, fredbaker.ietf@gmail.com, g.white@cablelabs.com
  RFC8034          ||      G. White, R. Pan         ||       g.white@cablelabs.com, ropan@cisco.com
  RFC8035          ||      C. Holmberg         ||       christer.holmberg@ericsson.com
  RFC8036          ||      N. Cam-Winget, Ed., J. Hui, D. Popa         ||       ncamwing@cisco.com, jonhui@nestlabs.com, daniel.popa@itron.com
  RFC8037          ||      I. Liusvaara         ||       ilariliusvaara@welho.com
  RFC8039          ||      A. Shpiner, R. Tse, C. Schelp, T. Mizrahi         ||       alexshp@mellanox.com, Richard.Tse@microsemi.com, craig.schelp@oracle.com, talmi@marvell.com
  RFC8040          ||      A. Bierman, M. Bjorklund, K. Watsen         ||       andy@yumaworks.com, mbj@tail-f.com, kwatsen@juniper.net
  RFC8041          ||      O. Bonaventure, C. Paasch, G. Detal         ||       Olivier.Bonaventure@uclouvain.be, cpaasch@apple.com, gregory.detal@tessares.net
  RFC8042          ||      Z. Zhang, L. Wang, A. Lindem         ||       zzhang@juniper.net, liliw@juniper.net, acee@cisco.com
  RFC8043          ||      B. Sarikaya, M. Boucadair         ||       sarikaya@ieee.org, mohamed.boucadair@orange.com
  RFC8044          ||      A. DeKok         ||       aland@freeradius.org
  RFC8045          ||      D. Cheng, J. Korhonen, M. Boucadair, S. Sivakumar         ||       dean.cheng@huawei.com, jouni.nospam@gmail.com, mohamed.boucadair@orange.com, ssenthil@cisco.com
  RFC8046          ||      T. Henderson, Ed., C. Vogt, J. Arkko         ||       tomhend@u.washington.edu, mail@christianvogt.net, jari.arkko@piuha.net
  RFC8047          ||      T. Henderson, Ed., C. Vogt, J. Arkko         ||       tomhend@u.washington.edu, mail@christianvogt.net, jari.arkko@piuha.net
  RFC8048          ||      P. Saint-Andre         ||       peter@filament.com
  RFC8049          ||      S. Litkowski, L. Tomotaki, K. Ogaki         ||       stephane.litkowski@orange.com, luis.tomotaki@verizon.com, ke-oogaki@kddi.com
  RFC8051          ||      X. Zhang, Ed., I. Minei, Ed.         ||       zhang.xian@huawei.com, inaminei@google.com
  RFC8053          ||      Y. Oiwa, H. Watanabe, H. Takagi, K. Maeda, T. Hayashi, Y. Ioku         ||       y.oiwa@aist.go.jp, h-watanabe@aist.go.jp, takagi.hiromitsu@aist.go.jp, maeda@lepidum.co.jp, hayashi@lepidum.co.jp, mutual-work@ioku.org
  RFC8054          ||      K. Murchison, J. Elie         ||       murch@andrew.cmu.edu, julien@trigofacile.com
  RFC8055          ||      C. Holmberg, Y. Jiang         ||       christer.holmberg@ericsson.com, jiangyi@chinamobile.com
  RFC8056          ||      J. Gould         ||       jgould@verisign.com
  RFC8057          ||      B. Stark, D. Sinicrope, W. Lupton         ||       barbara.stark@att.com, david.sinicrope@ericsson.com, wlupton@broadband-forum.org
  RFC8058          ||      J. Levine, T. Herkula         ||       standards@taugh.com, t.herkula@optivo.com
  RFC8059          ||      J. Arango, S. Venaas, I. Kouvelas, D. Farinacci         ||       jearango@cisco.com, stig@cisco.com, kouvelas@arista.com, farinacci@gmail.com
  RFC8060          ||      D. Farinacci, D. Meyer, J. Snijders         ||       farinacci@gmail.com, dmm@1-4-5.net, job@ntt.net
  RFC8061          ||      D. Farinacci, B. Weis         ||       farinacci@gmail.com, bew@cisco.com
  RFC8062          ||      L. Zhu, P. Leach, S. Hartman, S. Emery, Ed.         ||       larry.zhu@microsoft.com, pauljleach@msn.com, hartmans-ietf@mit.edu, shawn.emery@gmail.com
  RFC8063          ||      H.W. Ribbers, M.W. Groeneweg, R. Gieben, A.L.J. Verschuren         ||       rik.ribbers@sidn.nl, marc.groeneweg@sidn.nl, miek@miek.nl, ietf@antoin.nl
  RFC8064          ||      F. Gont, A. Cooper, D. Thaler, W. Liu         ||       fgont@si6networks.com, alcoop@cisco.com, dthaler@microsoft.com, liushucheng@huawei.com
  RFC8065          ||      D. Thaler         ||       dthaler@microsoft.com
  RFC8066          ||      S. Chakrabarti, G. Montenegro, R. Droms, J. Woodyatt         ||       samitac.ietf@gmail.com, Gabriel.Montenegro@microsoft.com, rdroms.ietf@gmail.com, jhw@google.com
  RFC8067          ||      B. Leiba         ||       barryleiba@computer.org
  RFC8068          ||      R. Ravindranath, P. Ravindran, P. Kyzivat         ||       rmohanr@cisco.com, partha@parthasarathi.co.in, pkyzivat@alum.mit.edu
  RFC8069          ||      A. Thomas         ||       a.n.thomas@ieee.org
  RFC8070          ||      M. Short, Ed., S. Moore, P. Miller         ||       michikos@microsoft.com, sethmo@microsoft.com, paumil@microsoft.com
  RFC8071          ||      K. Watsen         ||       kwatsen@juniper.net
  RFC8072          ||      A. Bierman, M. Bjorklund, K. Watsen         ||       andy@yumaworks.com, mbj@tail-f.com, kwatsen@juniper.net
  RFC8073          ||      K. Moriarty, M. Ford         ||       Kathleen.Moriarty@dell.com, ford@isoc.org
  RFC8074          ||      J. Bi, G. Yao, J. Halpern, E. Levy-Abegnoli, Ed.         ||       junbi@tsinghua.edu.cn, yaoguang.china@gmail.com, joel.halpern@ericsson.com, elevyabe@cisco.com
  RFC8075          ||      A. Castellani, S. Loreto, A. Rahman, T. Fossati, E. Dijk         ||       angelo@castellani.net, Salvatore.Loreto@ericsson.com, Akbar.Rahman@InterDigital.com, thomas.fossati@nokia.com, esko.dijk@philips.com
  RFC8076          ||      A. Knauf, T. Schmidt, Ed., G. Hege, M. Waehlisch         ||       alexanderknauf@gmail.com, t.schmidt@haw-hamburg.de, hege@daviko.com, mw@link-lab.net
  RFC8077          ||      L. Martini, Ed., G. Heron, Ed.         ||       lmartini@monoski.com, giheron@cisco.com
  RFC8078          ||      O. Gudmundsson, P. Wouters         ||       olafur+ietf@cloudflare.com, pwouters@redhat.com
  RFC8079          ||      L. Miniero, S. Garcia Murillo, V. Pascual         ||       lorenzo@meetecho.com, sergio.garcia.murillo@gmail.com, victor.pascual.avila@oracle.com
  RFC8080          ||      O. Sury, R. Edmonds         ||       ondrej.sury@nic.cz, edmonds@mycre.ws
  RFC8081          ||      C. Lilley         ||       chris@w3.org
  RFC8082          ||      S. Wenger, J. Lennox, B. Burman, M. Westerlund         ||       stewe@stewe.org, jonathan@vidyo.com, bo.burman@ericsson.com, magnus.westerlund@ericsson.com
  RFC8083          ||      C. Perkins, V. Singh         ||       csp@csperkins.org, varun@callstats.io
  RFC8084          ||      G. Fairhurst         ||       gorry@erg.abdn.ac.uk
  RFC8085          ||      L. Eggert, G. Fairhurst, G. Shepherd         ||       lars@netapp.com, gorry@erg.abdn.ac.uk, gjshep@gmail.com
  RFC8086          ||      L. Yong, Ed., E. Crabbe, X. Xu, T. Herbert         ||       lucy.yong@huawei.com, edward.crabbe@gmail.com, xuxiaohu@huawei.com, tom@herbertland.com
  RFC8087          ||      G. Fairhurst, M. Welzl         ||       gorry@erg.abdn.ac.uk, michawe@ifi.uio.no
  RFC8089          ||      M. Kerwin         ||       matthew.kerwin@qut.edu.au
  RFC8090          ||      R. Housley         ||       housley@vigilsec.com
  RFC8091          ||      E. Wilde         ||       erik.wilde@dret.net
  RFC8092          ||      J. Heitz, Ed., J. Snijders, Ed., K. Patel, I. Bagdonas, N. Hilliard         ||       jheitz@cisco.com, job@ntt.net, keyur@arrcus.com, ibagdona.ietf@gmail.com, nick@inex.ie
  RFC8093          ||      J. Snijders         ||       job@ntt.net
  RFC8094          ||      T. Reddy, D. Wing, P. Patil         ||       tireddy@cisco.com, dwing-ietf@fuggles.com, praspati@cisco.com
  RFC8095          ||      G. Fairhurst, Ed., B. Trammell, Ed., M. Kuehlewind, Ed.         ||       gorry@erg.abdn.ac.uk, ietf@trammell.ch, mirja.kuehlewind@tik.ee.ethz.ch
  RFC8096          ||      B. Fenner         ||       fenner@fenron.com
  RFC8097          ||      P. Mohapatra, K. Patel, J. Scudder, D. Ward, R. Bush         ||       mpradosh@yahoo.com, keyur@arrcus.com, jgs@juniper.net, dward@cisco.com, randy@psg.com
  RFC8098          ||      T. Hansen, Ed., A. Melnikov, Ed.         ||       tony@att.com, alexey.melnikov@isode.com
  RFC8099          ||      H. Chen, R. Li, A. Retana, Y. Yang, Z. Liu         ||       huaimo.chen@huawei.com, renwei.li@huawei.com, aretana@cisco.com, yyang1998@gmail.com, liu.cmri@gmail.com
  RFC8100          ||      R. Geib, Ed., D. Black         ||       Ruediger.Geib@telekom.de, david.black@dell.com
  RFC8101          ||      C. Holmberg, J. Axell         ||       christer.holmberg@ericsson.com, jorgen.axell@ericsson.com
  RFC8102          ||      P. Sarkar, Ed., S. Hegde, C. Bowers, H. Gredler, S. Litkowski         ||       pushpasis.ietf@gmail.com, shraddha@juniper.net, cbowers@juniper.net, hannes@rtbrick.com, stephane.litkowski@orange.com
  RFC8103          ||      R. Housley         ||       housley@vigilsec.com
  RFC8104          ||      Y. Shen, R. Aggarwal, W. Henderickx, Y. Jiang         ||       yshen@juniper.net, raggarwa_1@yahoo.com, wim.henderickx@nokia.com, jiangyuanlong@huawei.com
  RFC8106          ||      J. Jeong, S. Park, L. Beloeil, S. Madanapalli         ||       pauljeong@skku.edu, soohong.park@samsung.com, luc.beloeil@orange.com, smadanapalli@gmail.com
  RFC8107          ||      J. Wold         ||       jwold@ad-id.org
  RFC8108          ||      J. Lennox, M. Westerlund, Q. Wu, C. Perkins         ||       jonathan@vidyo.com, magnus.westerlund@ericsson.com, bill.wu@huawei.com, csp@csperkins.org
  RFC8109          ||      P. Koch, M. Larson, P. Hoffman         ||       pk@DENIC.DE, matt.larson@icann.org, paul.hoffman@icann.org
  RFC8110          ||      D. Harkins, Ed., W. Kumari, Ed.         ||       dharkins@arubanetworks.com, warren@kumari.net
  RFC8113          ||      M. Boucadair, C. Jacquenet         ||       mohamed.boucadair@orange.com, christian.jacquenet@orange.com
  RFC8114          ||      M. Boucadair, C. Qin, C. Jacquenet, Y. Lee, Q. Wang         ||       mohamed.boucadair@orange.com, jacni@jacni.com, christian.jacquenet@orange.com, yiu_lee@cable.comcast.com, 13301168516@189.cn
  RFC8115          ||      M. Boucadair, J. Qin, T. Tsou, X. Deng         ||       mohamed.boucadair@orange.com, jacni@jacni.com, tina.tsou@philips.com, dxhbupt@gmail.com
  RFC8117          ||      C. Huitema, D. Thaler, R. Winter         ||       huitema@huitema.net, dthaler@microsoft.com, rolf.winter@hs-augsburg.de
  RFC8118          ||      M. Hardy, L. Masinter, D. Markovic, D. Johnson, M. Bailey         ||       mahardy@adobe.com, masinter@adobe.com, dmarkovi@adobe.com, duff.johnson@pdfa.org, martin.bailey@globalgraphics.com
  RFC8119          ||      M. Mohali, M. Barnes         ||       marianne.mohali@orange.com, mary.ietf.barnes@gmail.com
  RFC8120          ||      Y. Oiwa, H. Watanabe, H. Takagi, K. Maeda, T. Hayashi, Y. Ioku         ||       y.oiwa@aist.go.jp, h-watanabe@aist.go.jp, takagi.hiromitsu@aist.go.jp, kaorumaeda.ml@gmail.com, hayashi@lepidum.co.jp, mutual-work@ioku.org
  RFC8121          ||      Y. Oiwa, H. Watanabe, H. Takagi, K. Maeda, T. Hayashi, Y. Ioku         ||       y.oiwa@aist.go.jp, h-watanabe@aist.go.jp, takagi.hiromitsu@aist.go.jp, kaorumaeda.ml@gmail.com, hayashi@lepidum.co.jp, mutual-work@ioku.org
  RFC8122          ||      J. Lennox, C. Holmberg         ||       jonathan@vidyo.com, christer.holmberg@ericsson.com
  RFC8123          ||      P. Dawes, C. Arunachalam         ||       peter.dawes@vodafone.com, carunach@cisco.com
  RFC8124          ||      R. Ravindranath, G. Salgueiro         ||       rmohanr@cisco.com, gsalguei@cisco.com
  RFC8128          ||      C. Morgan         ||       cmorgan@amsl.com
  RFC8129          ||      A. Jain, N. Kinder, N. McCallum         ||       ajain323@gatech.edu, nkinder@redhat.com, npmccallum@redhat.com
  RFC8130          ||      V. Demjanenko, D. Satterlee         ||       victor.demjanenko@vocal.com, david.satterlee@vocal.com
  RFC8131          ||      X. Zhang, H. Zheng, Ed., R. Gandhi, Ed., Z. Ali, P. Brzozowski         ||       zhang.xian@huawei.com, zhenghaomian@huawei.com, rgandhi@cisco.com, zali@cisco.com, pbrzozowski@advaoptical.com
  RFC8132          ||      P. van der Stok, C. Bormann, A. Sehgal         ||       consultancy@vanderstok.org, cabo@tzi.org, anuj.sehgal@navomi.com
  RFC8133          ||      S. Smyshlyaev. Ed., E. Alekseev, I. Oshkin, V. Popov         ||       svs@cryptopro.ru, alekseev@cryptopro.ru, oshkin@cryptopro.ru, vpopov@cryptopro.ru
  RFC8135          ||      M. Danielson, M. Nilsson         ||       magda@netinsight.net, mansaxel@besserwisser.org
  RFC8136          ||      B. Carpenter, R. Hinden         ||       brian.e.carpenter@gmail.com, bob.hinden@gmail.com
  RFC8138          ||      P. Thubert, Ed., C. Bormann, L. Toutain, R. Cragie         ||       pthubert@cisco.com, cabo@tzi.org, Laurent.Toutain@IMT-Atlantique.fr, robert.cragie@arm.com
  RFC8140          ||      A. Farrel         ||       adrian@olddog.co.uk
  RFC8144          ||      K. Murchison         ||       murch@andrew.cmu.edu
  RFC8145          ||      D. Wessels, W. Kumari, P. Hoffman         ||       dwessels@verisign.com, warren@kumari.net, paul.hoffman@icann.org""".split('\n')


# Many of these are addresses that the draft parser found incorrectly
ignore_addresses =[
'0004454742@mcimail.com',
'0006423401@mcimail.com',
'cabo@tzi.orgemail',
'california@san',
'cdl@rincon.com',
'hss@lando.hns.com',
'ietf-info@cnri.reston.va.us',
'illinois@urbana-champaign',
'jasdips@rwhois.net',
'labs@network',
'member@the',
'park@mit',
'research@icsi',
'research@isci',
'technopark@chaichee',
'texas@arlington',
'ura-bunyip@bunyip.com',
]

def get_rfc_data():
    author_names = dict()
    author_emails = dict()
    for line in rfced_data:
        (rfc,names,emails) = line.split('||')
        rfc = int(rfc.lower().strip()[3:])
        author_names[rfc] = [ x for x in map(str.lower,map(str.strip,names.split(','))) if x not in ['Ed.', 'ed.', '' ] ]
        author_emails[rfc] = [ x for x in map(unicode,map(str.lower,map(str.strip,emails.split(',')))) if x not in [ '', ] ]
    return author_names, author_emails

def get_all_the_email():
    all_the_email = Email.objects.all()
    for e in all_the_email:
        e.l_address = e.address.lower()
    return all_the_email

def get_matching_emails(all_the_email,addrlist):
    """ Find Email objects with addresses case-insensitively matching things in the supplied list (for lack of __iin) """
    l_addrlist = map(unicode.lower,addrlist)
    return [ e for e in all_the_email if e.l_address in l_addrlist ]

def show_verbose(rfc_num,*args):
    print "rfc%-4d :"%rfc_num,' '.join(map(str,args))

ParsedAuthor = namedtuple('ParsedAuthor',['name','address'])

def get_parsed_authors(rfc_num):
    h,n = mkstemp()
    os.close(h)
    f = open(n,"w")
    f.write('%s/rfc%d.txt\n'%(settings.RFC_PATH,rfc_num))
    f.close()
    lines = subprocess.check_output(['ietf/utils/draft.py','-a',n])
    os.unlink(n)
    if not 'docauthors ' in lines:
        return []
    authorline = [l for l in lines.split('\n') if l.startswith('docauthors ')][0]
    authstrings = authorline.split(':')[1].split(',')
    retval = []
    for a in authstrings:
        if '<' in a:
            retval.append(ParsedAuthor(a[:a.find('<')].strip(),a[a.find('<'):a.find('>')][1:]))
        else:
            retval.append(ParsedAuthor(a.strip(),None))
    
    return retval

def calculate_changes(tracker_persons,tracker_emails,names,emails):
    adds = set()
    deletes = set()
    for email in emails:
        if email and email!='none' and email not in ignore_addresses:
            p = Person.objects.filter(email__address=email).first()
            if p:
                if not set(map(unicode.lower,p.email_set.values_list('address',flat=True))).intersection(tracker_emails):
                    adds.add(email)
            else:
                person_name = names[emails.index(email)]
                adds.add(email)
    for person in tracker_persons:
        if not set(map(unicode.lower,person.email_set.values_list('address',flat=True))).intersection(emails):
            match = False
            for index in [i for i,j in enumerate(emails) if j=='none' or not j]:
                if names[index].split()[-1].lower()==person.last_name().lower():
                    match = True
            if not match:
                    deletes.add(person) 
    return adds, deletes

def _main():

    parser = argparse.ArgumentParser(description="Recalculate RFC documentauthor_set")
    parser.add_argument('-v','--verbose',help="Show the action taken for each RFC",action='store_true') 
    parser.add_argument('--rfc',type=int, nargs='*',help="Only recalculate the given rfc numbers",dest='rfcnumberlist')
    args = parser.parse_args()

    probable_email_match = set()
    probable_duplicates = []
    
    all_the_email = get_all_the_email()
    author_names, author_emails = get_rfc_data()
    
    stats = { 'rfc not in tracker'                           :0,
              'same addresses'                               :0,
              'different addresses belonging to same people' :0,
              'same names, rfced emails do not match'        :0,
              'rfced data is unusable'                       :0,
              "data doesn't match but no changes found"      :0,
              'changed authors'                              :0, }

    for rfc_num in args.rfcnumberlist or sorted(author_names.keys()):
    
        rfc = Document.objects.filter(docalias__name='rfc%s'%rfc_num).first()
    
        if not rfc:
            if args.verbose:
                show_verbose(rfc_num,'rfc not in tracker')
            stats['rfc not in tracker'] += 1
            continue
    
        rfced_emails = set(author_emails[rfc_num])
        tracker_emails = set(map(unicode.lower,rfc.authors.values_list('address',flat=True)))
        tracker_persons = set([x.person for x in rfc.authors.all()])
        matching_emails = get_matching_emails(all_the_email,rfced_emails)
        rfced_persons = set([x.person for x in matching_emails])
        known_emails = set([e.l_address for e in matching_emails])
        unknown_emails = rfced_emails - known_emails
        unknown_persons = tracker_persons-rfced_persons
    
        rfced_lastnames = sorted([n.split()[-1].lower() for n in author_names[rfc_num]])
        tracker_lastnames = sorted([p.last_name().lower() for p in tracker_persons])
    
        if rfced_emails == tracker_emails:
            if args.verbose:
                show_verbose(rfc_num,'tracker and rfc editor have the same addresses')
            stats['same addresses'] += 1
            continue
    
        if len(rfced_emails)==len(tracker_emails) and not 'none' in author_emails[rfc_num]:
            if tracker_persons == rfced_persons:
                if args.verbose:
                    show_verbose(rfc_num,'tracker and rfc editor have the different addresses belonging to same people')
                stats['different addresses belonging to same people'] += 1
                continue
            else:
                if len(unknown_emails)==1 and len(tracker_persons-rfced_persons)==1:
                    p = list(tracker_persons-rfced_persons)[0]
                    probable_email_match.add(u"%s is probably %s (%s) : %s "%(list(unknown_emails)[0], p, p.pk, rfc_num))
                elif len(unknown_emails)==len(unknown_persons):
                    probable_email_match.add(u"%s are probably %s : %s"%(unknown_emails,[(p.ascii,p.pk) for p in unknown_persons],rfc_num))
                else:
                    probable_duplicates.append((tracker_persons^rfced_persons,rfc_num))
    
        if tracker_lastnames == rfced_lastnames:
            if args.verbose:
                show_verbose(rfc_num,"emails don't match up, but person names appear to be the same")
            stats[ 'same names, rfced emails do not match'] += 1
            continue
    
        use_rfc_data = bool(len(author_emails[rfc_num])==len(author_names[rfc_num]))
        if not use_rfc_data:
            if args.verbose:
                print 'Ignoring rfc database for rfc%d'%rfc_num
            stats[ 'rfced data is unusable'] += 1

        if use_rfc_data:
            adds, deletes = calculate_changes(tracker_persons,tracker_emails,author_names[rfc_num],author_emails[rfc_num])
        parsed_authors=get_parsed_authors(rfc_num)
        parsed_adds, parsed_deletes = calculate_changes(tracker_persons,tracker_emails,[x.name for x in parsed_authors],[x.address for x in parsed_authors])

        for e in adds.union(parsed_adds) if use_rfc_data else parsed_adds:
            if not e or e in ignore_addresses:
                continue
            if not Person.objects.filter(email__address=e).exists():
                if e not in parsed_adds:
                    #print rfc_num,"Would add",e,"as",author_names[rfc_num][author_emails[rfc_num].index(e)],"(rfced database)"
                    print "(address='%s',name='%s'),"%(e,author_names[rfc_num][author_emails[rfc_num].index(e)]),"# (rfced %d)"%rfc_num
                    for p in Person.objects.filter(name__iendswith=author_names[rfc_num][author_emails[rfc_num].index(e)].split(' ')[-1]):
                        print "\t", p.pk, p.ascii
                else:
                    name = [x.name for x in parsed_authors if x.address==e][0]
                    p = Person.objects.filter(name=name).first()
                    if p:
                        #print e,"is probably",p.pk,p
                        print "'%s': %d, # %s (%d)"%(e,p.pk,p.ascii,rfc_num)

                    else:
                        p = Person.objects.filter(ascii=name).first()
                        if p:
                            print e,"is probably",p.pk,p
                            print "'%s': %d, # %s (%d)"%(e,p.pk,p.ascii,rfc_num)
                        else:
                            p = Person.objects.filter(ascii_short=name).first()
                            if p:
                                print e,"is probably",p.pk,p
                                print "'%s': %d, # %s (%d)"%(e,p.pk,p.ascii,rfc_num)
                    #print rfc_num,"Would add",e,"as",name,"(parsed)"
                    print "(address='%s',name='%s'),"%(e,name),"# (parsed %d)"%rfc_num
                    for p in Person.objects.filter(name__iendswith=name.split(' ')[-1]):
                        print "\t", p.pk, p.ascii

        if False: # This was a little useful, but the noise in the rfc_ed file keeps it from being completely useful
            for p in deletes:
                for n in author_names[rfc_num]:
                    if p.last_name().lower()==n.split()[-1].lower():
                        email_candidate = author_emails[rfc_num][author_names[rfc_num].index(n)]
                        email_found = Email.objects.filter(address=email_candidate).first()
                        if email_found:    
                            probable_duplicates.append((set([p,email_found.person]),rfc_num))
                        else:
                            probable_email_match.add(u"%s is probably %s (%s) : %s"%(email_candidate, p, p.pk, rfc_num))
             
        if args.verbose:
            if use_rfc_data:
                working_adds = parsed_adds
                seen_people = set(Email.objects.get(address=e).person for e in parsed_adds)
                for addr in adds:
                    person = Email.objects.get(address=addr).person
                    if person not in seen_people:
                        working_adds.add(addr)
                        seen_people.add(person)
                working_deletes = deletes.union(parsed_deletes)
            else:
                working_adds = parsed_adds
                working_deletes = parsed_deletes
            # unique_adds = set() # TODO don't add different addresses for the same person from the two sources
            if working_adds or working_deletes:
                show_verbose(rfc_num,"Changing original list",tracker_persons,"by adding",working_adds," and deleting",working_deletes)
                print "(",rfc_num,",",[e for e in working_adds],",",[p.pk for p in working_deletes],"), #",[p.ascii for p in working_deletes]
            else:
                stats["data doesn't match but no changes found"] += 1
                show_verbose(rfc_num,"Couldn't figure out what to change")

        if False:
        #if tracker_persons:
        #if any(['iab@' in e for e in adds]) or any(['iesg@' in e for e in adds]) or any(['IESG'==p.name for p in deletes]) or any(['IAB'==p.name for p in deletes]):
            print rfc_num
            print "tracker_persons",tracker_persons
            print "author_names",author_names[rfc_num]
            print "author_emails",author_emails[rfc_num]
            print "Adds:", adds
            print "Deletes:", deletes
        
        stats['changed authors'] += 1
    
        if False:
            debug.show('rfc_num')
            debug.show('rfced_emails')
            debug.show('tracker_emails')
            debug.show('known_emails')
            debug.show('unknown_emails')
            debug.show('tracker_persons')
            debug.show('rfced_persons')
            debug.show('tracker_persons==rfced_persons')
            debug.show('[p.id for p in tracker_persons]')
            debug.show('[p.id for p in rfced_persons]')
            exit()
    
    if True:
        for p in sorted(list(probable_email_match)):
            print p
    if True:
        print "Probable duplicate persons"
        for d,r in sorted(probable_duplicates):
            print [(p,p.pk) for p in d], r
    else:
        print len(probable_duplicates)," probable duplicate persons"

    print stats

if __name__ == "__main__":
    _main()

