
def generate_html( intent, prefix="" ):
    def render( k, T ):
        if T=="string":
            return "<input type='text' name='%s' value=''/>" % k
        elif "|" in T:
            return "\n".join( 
                ("<input type='radio' name='%s' value='%s'/>" % (k,v))
                for v in T.split("|")
            )
        elif "&" in T:
            return "\n".join( 
                ("<input type='checkbox' name='%s' value='%s'/>" % (k,v))
                for v in T.split("&")
            )
        else:
            raise ValueError("Unknown form type: "+repr(T))
    return "\n".join(
        render(k,T) for (k,T) in intent.items()
    )

def parse_response( d ):
    pass
