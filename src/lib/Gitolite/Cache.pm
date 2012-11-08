package Gitolite::Cache;

# cache stuff using an external database (redis)
# ----------------------------------------------------------------------

@EXPORT = qw(
  cache_set
  cache_get
  cache_flush_repo
  cache_control
);

use Exporter 'import';

use Gitolite::Common;
use Gitolite::Rc;
use Storable qw(freeze thaw);
use Redis;

my $redis;
my $cache_up = 1;

my $redis_sock = "$ENV{HOME}/.redis-gitolite.sock";
if ( -S $redis_sock ) {
    _connect_redis();
} else {
    _start_redis();
    _connect_redis();

    # this redis db is a transient, caching only, db, so let's not
    # accidentally use any stale data when if we're just starting up
    cache_control('stop');
    cache_control('start');
}

# ----------------------------------------------------------------------

my $ttl = ( $rc{CACHE_TTL} || ( $rc{GROUPLIST_PGM} ? 60 : 99999 ) );

sub cache_set {
    my $type = shift;
    my $hash = shift;
    my $key  = shift;
    my $val;

    return if not $redis->exists('cache-up');

    if ( $type eq 'SCALAR' ) {
        $val = shift;
    } elsif ( $type eq 'ARRAY' ) {
        $val = freeze( \@_ );
    } elsif ( $type eq 'HASH' ) {
        %val = @_;
        $val = freeze( \%val );
    }
    $redis->set( "$hash: $key", $val );
    $redis->expire( "$hash: $key", $ttl ) if $ttl;
}

sub cache_get {
    my ( $type, $hash, $key, $ref ) = @_;

    return 0 if not $cache_up;
    # and don't touch the 'ref'1

    my $val = $redis->get("$hash: $key");
    return 0 if not defined($val);

    if ( $type eq 'SCALAR' ) {
        ${$ref} = $val;
    }
    if ( $type eq 'ARRAY' ) {
        @{$ref} = @{ thaw($val) };
    } elsif ( $type eq 'HASH' ) {
        %{$ref} = %{ thaw($val) };
    }
    return 1;
}

sub cache_flush_repo {
    my $repo = shift;
    for my $glob ("memberships: user, $repo,*", "rules: $repo,*") {
        my @keys = $redis->keys($glob);
        $redis->del( @keys ) if @keys;
    }
}

sub cache_control {
    my $op = shift;
    if ( $op eq 'stop' ) {
        $redis->flushall();
    } elsif ( $op eq 'start' ) {
        $redis->set( 'cache-up', 1 );
    }
}

# ----------------------------------------------------------------------

sub _start_redis {
    my $conf = join( "", <DATA> );
    $conf =~ s/%HOME/$ENV{HOME}/g;

    open( REDIS, "|-", "/usr/sbin/redis-server", "-" ) or die "start redis server failed: $!";
    print REDIS $conf;
    close REDIS;

    # give it a little time to come up
    select( undef, undef, undef, 0.2 );
}

sub _connect_redis {
    $redis = Redis->new( sock => $redis_sock, encoding => undef ) or die "redis new failed: $!";
    $redis->ping or die "redis ping failed: $!";
}

1;

__DATA__
# resources
maxmemory 50MB
port 0
unixsocket %HOME/.redis-gitolite.sock
unixsocketperm 700
timeout 0
databases 1

# daemon
daemonize yes
pidfile %HOME/.redis-gitolite.pid
dbfilename %HOME/.redis-gitolite.rdb
dir %HOME

# feedback
loglevel notice
logfile %HOME/.redis-gitolite.log

# we don't save
