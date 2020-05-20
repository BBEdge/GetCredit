##### GetCredit

```
    DATA SS REGEX: (?<=\_)\d+  
    ALIAS REGEX: alias.(\w*):(\S*)  
    SWITCH NAME: (?<=_)\w*\S*(?=_)
    OUTPUT FORMAT: switch, pid, wwn, credit, fsz, class, sname, alias  
    ^portloginshow\s(\d+)  
    ff\s+\w+\s+(?:[0-9a-fA-F]:?){16}\s+\d\s+\d+\s+\w+\s+\w+=\w+    
```