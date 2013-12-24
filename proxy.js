#! /usr/bin/env phantomjs

var system = require( 'system' );
var webpage = require( 'webpage' );
var fs = require('fs');


var targetURL = 'http://proxyhttp.net/free-list/anonymous-server-hide-ip-address';
var serverList = [];
var outFile = 'list.txt';

var page = webpage.create();

page.settings = {
    loadImages: false,
    javascriptEnabled: true,
    viewportSize: { width: 640, height: 960 },
    userAgent: 'Mozilla/5.0 (iPhone; CPU iPhone OS 5_0 like Mac OS X) AppleWebKit/534.46 (KHTML, like Gecko) Version/5.1 Mobile/9A334 Safari/7534.48.3'
};

page.onResourceRequested = function( requestData, networkRequest ) {
    if ( /\.css/.test( requestData.url ) ) {
        networkRequest.abort();
        // console.info( 'abort resource:', requestData.url );
    }
};

page.open( targetURL, processPage );



function processPage ( status ) {
    if ( status !== 'success' ) {
        console.info( 'network error', status );
        phantom.exit( 1 );
    }
    else {
        var data = page.evaluate( parse4ProxyList );
        serverList = serverList.concat( data.servers );

        if ( data.page ) {
            console.info( 'next page: ', data.page );
            // page.close();
            setTimeout(
                function() {
                    page.open( data.page, processPage );
                },
                1000
            );
        }
        else {
            setTimeout( function () {
                // system.stdout.write(
                //     'proxys=' + JSON.stringify( serverList )
                // );

                // console.log( JSON.stringify( serverList ) );

                console.info( 'write to file...' );
                var f = fs.open( outFile, 'w' );
                f.write(
                    serverList.sort(function ( a, b ) {
                        if ( a.anonymity < b.anonymity ) return -1;
                        else if ( a.anonymity > b.anonymity ) return 1;
                        return 0;
                    }).map(function ( s ) {
                        return s.ip + ':' + s.port +
                            ',' + s.anonymity +
                            ',' + s.https +
                            ',' + s.country;
                    }).join( '\n' )
                );
                f.close();
                console.info( 'success' );

                phantom.exit( 0 );
            }, 300);
        }
    }
}


function parse4ProxyList() {
    var trs = document.querySelectorAll(
                '#incontent .proxytbl tr:not(:nth-child(1))'
            );

    var servers = [];
    [].forEach.call( trs, function ( tr ) {
        var server = {};
        var tds = tr.querySelectorAll( 'td' );
        server[ 'ip' ] = tds[0].innerText.trim();
        server[ 'port' ] = tds[1].innerText.trim();
        server[ 'country' ] = tds[2].innerText.trim();
        server[ 'anonymity' ] = tds[3].innerText.toLowerCase().trim();
        if ( server[ 'anonymity' ] === 'high' ) {
            server[ 'anonymity' ] = 1;
        }
        else if ( server[ 'anonymity' ] === 'anonymous' ) {
            server[ 'anonymity' ] = 2;
        }
        else {
            server[ 'anonymity' ] = 3;
        }
        server[ 'https' ] = tds[4].innerHTML.trim().indexOf( 'ok.png' ) > 0;
        servers.push( server );
    });

    var page;
    var p = document.querySelector( '#pages .current' );
    if ( p ) {
        while ( ( p = p.nextElementSibling ) ) {
            if ( p.tagName.toLowerCase() === 'a' ) {
                var href = p.getAttribute( 'href' ).trim();
                if ( /^\/free\-list\//i.test( href ) ) {
                    page = location.protocol + '//' + location.hostname + href;
                    break;
                }
            }
        }
    }

    return {
        servers: servers,
        page: page
    };
}







