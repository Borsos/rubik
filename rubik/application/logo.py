#!/usr/bin/env python3
#
# Copyright 2014 Simone Campagna
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
#

__author__ = "Simone Campagna"

RUBIK = r"""
                                         _a??</                                 
                                     .a;?:: :..(<                               
                                  _a?':..-....:.:)`,                            
                                awWw,:..:..-.-.:...::,                          
                            <c31siITW6w -..-.-....:.wyW,                        
                        .a%TllillllliY$Wa/:-..-.<amQWWTYTs/.                    
                      a#1iillllllllllliIWWm/:_wWQWQU1illllv5,.                  
                     ]QWmwiilIlIlllllIIll3$QXQWWTCllllllllllICs                 
                     ]QQQWWwvllllIlIlllvwmWQWQWw%vlllllllIlllli3</              
          .a3VVs_a,. dQQQWWmWmziIlllvymQWDYill3SWhwillIlIllIlllvwmL,            
       _cJ1nvnnoSoXVsQQQQQQWQQBguvwyQQBTlllIIlilY5mGuvllllIIlqwWWP?:(_.         
    a%U1nnnnonnonoqm?! .:??9WWWQXmW@TlIlIlllllIIllITm#w%IInyQWP!...:.:)_.       
  <QwponnnnnnnogW?!....-......-9QWQmwllllIllIlllllIll3Q@$WQP?.......-...-(a     
  -HV$WQmggggD?`-.....-.-.:.=wmUSnooXVuwallIlIIlIlvlwmWWWWQa.:....-..-.:.. ?_,  
   5vnv3VVQZQwa;....:.-.-_ayBVnnoo2ooooooZSnwzlllnwQQQWTl3TWha..:.:.-.-..:..=yc 
    2nnnnnv$WU8QQmaw,:_wm@Voooooo2o2o2o2ooqmWQQwQQQWT1ivlillV$ma,....-..-_wmBT' 
    )onnnnn3QpXoXZHUWQXWmpnooo2o2o2oSo2mmQWVSn$WWT1lllllllllli39Q6a.:.:wm@Vn2'  
     <nnnnnn$Q2XXSX2XdQF?9QW#gpno2ooqmQQHoo2ooXW%ivlllllllllllli%$WWsjQUnoSS    
     -"gvnnnn$mXXSSXSXW6=;::??YQQm3QWHSooo22o2oQWmwilllllIlIlIlllvwQm#2o22q`    
      .@HWmgwmQm2SSSS2SWc::;;;;::4mZooo222o22o2dQQm$w%IIlllllllwm@YWSnooq7'     
       {XSSXH$WBqSSSSXSdQ/;;;;;;;+Qmo22o2o22o2ooQWWQmWgcIlIIwyQT|=mUnqp?<'      
        pXSSSSSmWQmgXSSXQL:;;:;;:=]Qo2o22o2o222oQQQQQQmWywwmDT+++dWq?!=i`       
        )2XSSSSdWknVHWWmmQc;=;;;;::Qmo2o22222qgQQQQQQWQQwdT(==+|yDT==+<'        
         ]SSSSSSWQ2vvvvXV$mmwa/:;;=]Qpo2o2qgQ@T1v3QQQQQWm[+==vaQT|=+<r'         
          4SSSXoXWQvnnnvnv$W8$QQma>-QEoomQWVIvvvvvWWQQWGC=|aT(n@;=aZd'          
          -T$mgXX$WpvnnnnnvWZS2XUHWWQ@TQVCvvvvvvvv3WQQ#ZszT|ij@svGnq            
           \==*?QBWWzvnvnvnUWZ2So22oXBWevvvvvvvIvvvQWQWT|>||w@Vnn2q`            
            c==+==?$WQgpvnvnQmoSSSSSS2#mvvvvvvvvvvI3QE|||<wm&nnor"              
            -%=++++|h:)9QQwo$WXoS222S2SQvvvvvvvvvvnQW(|<dC<@no?                 
             <=+++++4f;;:+?9W@$2S2XS2SS$mvvvvvvnym@?$a3(|sm"'                   
              "-a=+=|5;=:;;=:]WQQmgw2S2XW2vvvwm@?+::+C|</`                      
                 -!-c]m:;;;;;:4QXXUUQQgmWmymWY^;:;;;:{"                         
                     ??<:=;;;;+Qm2XSSXU$QmW?:::;;:;::]/                         
                        .^:;=:;$WZXSSSS22$Q::;;:;:;;:;5                         
                           ."'<=QmSSSSSXXdW/;:;:;:;::=J                         
                               .??4S2SSSSXUm=:;::;;<7'.                         
                                    ?{m2XSSQ;=::=/?                             
                                       -"4ZWm;a"`                               
                                        .  "?'.        
"""
