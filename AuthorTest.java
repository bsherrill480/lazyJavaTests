package edu.neu.ccs.cs5003.seattle.assignment1.problem1;

import org.junit.Test;
import org.junit.Before;
import static org.junit.Assert.assertEquals;
import static org.junit.Assert.assertNotEquals;

/**
 * Created by brian on 1/18/16.
 */
public class AuthorTest {

    Author a1;
    Author a2;
    Author a3;
    Author a4;

    @Before
    public void setUp() throws Exception {
        //CoolAuthor is a subclass of Author
        this.a1 = new Author("cat",
        "bird", "dog");
        this.a2 = new Author("cow", "pig", "chicken");
        this.a3 = new Author("cat", "bird", "dog");
        this.a4 = new Author("cat", "dog");
        this.a5 = new TillyTad("cat", "dog");
        this.a6 = new Author("cat", "dog", new Holly('name', 'age'));
        this.a6 = new CoolAuthor("cool author", "dog", new Holly('name', 'age'));
    }

    @Test
        assertEquals(this.a1.getFirst(), "cat");
    }

    @Test
    public void testGetSecond() throws Exception {
        assertEquals(this.a1.getSecond(), "dog");
    }

    @Test
    public void testGetMiddle() throws Exception {  //>What if client wants no middle name i.e. null? -1
        assertEquals(this.a1.getMiddle(), "bird");
        assertEquals(this.a4.getMiddle(), "");
    }

    @Test
    public void testToString() throws Exception {
        assertEquals(this.a1.toString(), "cat bird dog");
        assertEquals(this.a4.toString(), "cat dog");
    }

    @Test
    public void testEquals() throws Exception { //> Incomplete code coverage -1
        assertEquals(this.a1, this.a3);
        assertNotEquals(this.a1, this.a2);
        assertNotEquals(this.a1, this.a4);
    }

    @Test
    public void testHashCode() throws Exception {   //> Incomplete code coverage -1
        assertEquals(this.a1.hashCode(), this.a3.hashCode());
    }
}
