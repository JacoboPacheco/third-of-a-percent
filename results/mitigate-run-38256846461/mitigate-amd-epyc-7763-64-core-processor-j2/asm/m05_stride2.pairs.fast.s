0000000000001240 <_Z16kern_m05_stride2RNSt3__16vectorIiNS_9allocatorIiEEEERKS3_>:
    1240:	mov    (%rdi),%rax
    1243:	mov    0x8(%rdi),%rdi
    1247:	mov    %rdi,%rcx
    124a:	sub    %rax,%rcx
    124d:	sar    $0x2,%rcx
    1251:	mov    (%rsi),%rdx
    1254:	mov    0x8(%rsi),%rsi
    1258:	sub    %rdx,%rsi
    125b:	sar    $0x2,%rsi
    125f:	mov    %rsi,%r8
    1262:	shr    $1,%r8
    1265:	cmp    %rcx,%r8
    1268:	jb     12a7 <_Z16kern_m05_stride2RNSt3__16vectorIiNS_9allocatorIiEEEERKS3_+0x67>
    126a:	cmp    %rax,%rdi
    126d:	je     12a6 <_Z16kern_m05_stride2RNSt3__16vectorIiNS_9allocatorIiEEEERKS3_+0x66>
    126f:	cmp    $0x1,%rcx
    1273:	adc    $0x0,%rcx
    1277:	xor    %edi,%edi
    1279:	nopl   0x0(%rax)
    1280:	cmp    %rdi,%rsi
    1283:	jbe    12a7 <_Z16kern_m05_stride2RNSt3__16vectorIiNS_9allocatorIiEEEERKS3_+0x67>
    1285:	lea    0x1(%rdi),%r8
    1289:	cmp    %r8,%rsi
    128c:	jbe    12a7 <_Z16kern_m05_stride2RNSt3__16vectorIiNS_9allocatorIiEEEERKS3_+0x67>
    128e:	mov    0x4(%rdx,%rdi,4),%r9d
    1293:	add    (%rdx,%rdi,4),%r9d
    1297:	mov    %r9d,(%rax,%rdi,2)
    129b:	inc    %r8
    129e:	mov    %r8,%rdi
    12a1:	dec    %rcx
    12a4:	jne    1280 <_Z16kern_m05_stride2RNSt3__16vectorIiNS_9allocatorIiEEEERKS3_+0x40>
    12a6:	ret
    12a7:	ud2
    12a9:	nopl   0x0(%rax)
