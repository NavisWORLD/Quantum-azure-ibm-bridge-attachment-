use strict;
use warnings;
use HTTP::Tiny;
use JSON::PP qw(encode_json decode_json);

my $base = $ARGV[0] // 'http://127.0.0.1:8766';
$base =~ s{/$}{};
my $http = HTTP::Tiny->new(timeout => 5);

sub request_json {
    my ($method, $path, $payload) = @_;
    my %options = (headers => { 'Accept' => 'application/json' });
    if (defined $payload) {
        $options{headers}{'Content-Type'} = 'application/json';
        $options{content} = encode_json($payload);
    }
    my $response = $http->request($method, $base . $path, \%options);
    die "QBT HTTP $response->{status}: $response->{content}" unless $response->{success};
    return decode_json($response->{content});
}

my $health = request_json('GET', '/health', undef);
die 'QBT health contract failed' unless $health->{status} eq 'ok';

my $sample = request_json('POST', '/v1/sample', {
    provider => 'simulator', shots => 128, seed => 7,
});
die 'QBT sample contract failed' unless $sample->{packet}{active_sources} == 1;

my $normalized = request_json('POST', '/v1/normalize', {
    provider => 'perl', backend => 'smoke', mode => 'simulator',
    counts => { '0' => 64, '1' => 64 }, shots => 128,
});
die 'QBT normalize contract failed'
    unless abs($normalized->{state}{entropy} - 1.0) < 1e-12;

print "Perl QBT smoke: OK\n";
