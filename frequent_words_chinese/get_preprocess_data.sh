

##GetData
#if [-f zh_cn.txt]; then
#	#unzip data
#	unzip zh_cn-2012.zip
#fi 
cd data
unzip zh_cn-2012.zip

#remove logs
rm zh_cn-s.log
rm zh_cn.log


## Clean the data: Filter rows to keep only chinese characters. Remove lines that contains latin letters
cat zh_cn.txt | awk -F " " '{if (!( $1~/[0-9a-zA-Z]/)) print $0}' > zh_cn_clean.txt


#### Obtain a file with the frequencies of each character (instead of words)
cat zh_cn_clean.txt |

#separate each character of the words
sed -e 's/\([^0-9]\)/ \1/g' | 

# count the frequency of each character
awk -F " " '{ 
  for (i=1;i<(NF-1);i++) {
   M[$i]=M[$i]+$(NF-1) #add the frequency in (NF-1) column to the character $i
  }
 }
 END{
  for (k in M) {
   print k" "M[k]
 }

}' |

# sort again. By second column (-k2 -n) and descending order (-r)
sort -k2 -n -r     > zh_cn_characters.txt

cd ..