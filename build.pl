#!/usr/bin/perl

use POSIX qw(strftime);

my %langs = (
  'en' => 'English',
  'cs' => 'Czech',
  'fr' => 'French',
  'de' => 'German',
  'ru' => 'Russian',
  'hi' => 'Hindi',
);

my $file = shift || "wmt14/export-2014-03-26-10-58.csv";
my $pct = shift || .5;
my $runs = shift || 20;

foreach my $lang (keys %langs) {
  next if $lang eq "en";

  chomp(my $num_judgments = `grep "^$langs{$lang},English" $file | wc -l`);
  print "$langs{$lang} -> English ($num_judgments)\n";
  chomp($num_judgments = `grep "^English,$langs{$lang}" $file | wc -l`);
  print "English -> $langs{$lang} ($num_judgments)\n";

  for my $num (0..$runs-1) {
    system("egrep '^(srclang|$langs{$lang},English)' $file | python2.7 src/infer_TS.py result/$lang-en$num -n 2 -d 0 -p $pct");

    system("egrep '^(srclang|English,$langs{$lang})' $file | python2.7 src/infer_TS.py result/en-$lang$num -n 2 -d 0 -p $pct");
  }

  system("python2.7 eval/cluster_by_rank.py result/$lang-en $runs");
  system("python2.7 eval/cluster_by_rank.py result/en-$lang $runs");
}

my $outfile = "pdfs/ts-" . (strftime "%Y-%m-%d-%H-%M", localtime) . ".pdf";
system("pdfunite result/*-*.pdf $outfile");
